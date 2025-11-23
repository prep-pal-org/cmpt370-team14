from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import bcrypt
import os

from werkzeug.utils import secure_filename
from cmpt370_project_user_management.Model.Recipe import Recipe
from cmpt370_project_user_management.FlaskConnections.RecipeManager import RecipeManager
from cmpt370_project_user_management.db.setup_database import database_connection, create_tables
from cmpt370_project_user_management.Model.calendar_service import CalendarService, CalendarError

app = Flask(__name__)
app.secret_key = "saucy"
DB_NAME = "db/saucyapp.db"
calendar_service = CalendarService()

# -------------------------------------------------------------
# ROUTE: New Updated Home Page - Randi
# -------------------------------------------------------------
@app.route('/')
def home():
    return render_template('use_home_page.html')

# Old home page (legacy)
@app.route('/old_home')
def old_home():
    return render_template('homePage.html')


# -------------------------------------------------------------
# ROUTES: Grocery List (Soham + Randi)
# -------------------------------------------------------------
@app.route('/grocery-list')
def grocery_list():
    # Check if user is logged in
    if 'username' not in session:
        flash("You must be logged in to see your grocery list.")
        return redirect(url_for('login'))

    conn = database_connection(DB_NAME)
    cursor = conn.cursor()

    try:
        # Get the user_id from the session username
        cursor.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
        user_result = cursor.fetchone()

        # If user not found (shouldn't happen if logged in), log them out
        if not user_result:
            flash("Error finding user. Please log in again.")
            return redirect(url_for('logout'))

        current_user_id = user_result[0]

        # Fetch items for the *current* user
        cursor.execute("SELECT item_id, item_text, quantity FROM grocery_list WHERE user_id = ?", (current_user_id,))
        items_tuples = cursor.fetchall()

    except sqlite3.Error as e:
        print("Error fetching grocery list:", e)
        flash("An error occurred while fetching your list.")
        items_tuples = []  # Ensure items_tuples is defined even if try fails
    finally:
        conn.close()

    # Convert list of tuples to a list of dicts
    items_list = []
    for row in items_tuples:
        items_list.append({"id": row[0], "item_text": row[1], "quantity": row[2]})

    return render_template('grocery_list.html', items=items_list)


# Route to add an item to the grocery list
@app.route('/add_grocery_item', methods=['POST'])
def add_grocery_item():
    # Check if user is logged in
    if 'username' not in session:
        flash("You must be logged in to add items.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        item_text = request.form['item_text']
        quantity = request.form['quantity']

        if item_text:
            conn = database_connection(DB_NAME)
            cursor = conn.cursor()
            try:
                # Get the user_id from the session username
                cursor.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
                user_result = cursor.fetchone()

                if not user_result:
                    flash("Error finding user. Please log in again.")
                    return redirect(url_for('logout'))

                current_user_id = user_result[0]

                # Insert the item with the *current* user's ID
                cursor.execute("INSERT INTO grocery_list (user_id, item_text, quantity) VALUES (?, ?, ?)",
                               (current_user_id, item_text, quantity))
                conn.commit()
            except sqlite3.Error as e:
                print("Error adding grocery item:", e)
                flash("Error adding item to list.")
            finally:
                conn.close()

        # Redirect back to the grocery list page
        return redirect(url_for('grocery_list'))


@app.route('/remove_grocery_item', methods=['POST'])
def remove_grocery_item():
    # Check if user is logged in
    if 'username' not in session:
        flash("You must be logged in to remove items.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        item_id = request.form['item_id']

        conn = database_connection(DB_NAME)
        cursor = conn.cursor()
        try:
            # Get the user_id from the session username
            cursor.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
            user_result = cursor.fetchone()

            if not user_result:
                flash("Error finding user. Please log in again.")
                return redirect(url_for('logout'))

            current_user_id = user_result[0]

            # Securely delete the item
            # This query ensures a user can ONLY delete their own items
            cursor.execute("DELETE FROM grocery_list WHERE item_id = ? AND user_id = ?", (item_id, current_user_id))
            conn.commit()

            # Check if any row was actually deleted
            if cursor.rowcount == 0:
                flash("Error: Item not found or you do not have permission to remove it.")
            else:
                flash("Item removed.")

        except sqlite3.Error as e:
            print("Error removing grocery item:", e)
            flash("Error removing item.")
        finally:
            conn.close()

    # Redirect back to the grocery list page
    return redirect(url_for('grocery_list'))


# -------------------------------------------------------------
# USER PROFILE / LOGIN
# -------------------------------------------------------------
@app.route('/create_profile', methods=['GET', 'POST'])
def createProfile():
    message = ''
    if request.method == 'POST':
        userName = request.form['username']
        email = request.form['email']
        password = request.form['password']
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, "db", "saucyapp.db")

        hash_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        try:
            with sqlite3.connect('db/saucyapp.db') as conn:
                cur = conn.cursor()
                cur.execute(" INSERT INTO user_profile (username, email, password) VALUES (?, ?,?)",
                           (userName,email,hash_password))
                conn.commit()
                flash("Profile created successfully")
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already taken.")
            return redirect(url_for('createProfile'))

    return render_template('create_profile.html')

# Login page -Randi
@app.route('/login_page', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        userName = request.form['username']
        entered_password = request.form['password']

        with sqlite3.connect('db/saucyapp.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT password FROM user_profile WHERE username = ?", (userName,))
            result = cur.fetchone()
        if result is None:
            flash('Invalid username or password')

        else:
            stored_hash = result[0]
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode("utf-8")

            if bcrypt.checkpw(entered_password.encode("utf-8"), stored_hash):
                session['username'] = userName
                return render_template('login_landing_page.html')
            else:
                flash("Invalid username or password")
    return render_template('login_page.html')

# Login landing page -Randi
@app.route('/login_landing_page')
def login_landing_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('login_landing_page.html')

# User logout. -Randi
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# User list for testing purposes - Randi
@app.route('/user_list_for_testing')
def user_list_for_testing():
    connect = sqlite3.connect('db/saucyapp.db')
    cur = connect.cursor()
    cur.execute(" SELECT * FROM user_profile")
    rows = cur.fetchall()
    return render_template("user_list_for_testing.html", data=rows)

# Create a comment - Randi
@app.route('/create_comment',methods=['GET', 'POST'])
def create_comment():
    if request.method == 'POST':
        # add a line to get the name of the commenter
        comment = request.form['comment']
        with sqlite3.connect('db/saucyapp.db') as conn:
            cur = conn.cursor()
            cur.execute(" INSERT INTO user_interaction (comment) VALUES (?)",
                        (comment,))
            conn.commit()
        return render_template('homePage.html')
    else:
        return render_template('create_comment.html')

# View a comment - Randi
@app.route('/view_comments')
def view_comment():
    connect = sqlite3.connect('db/saucyapp.db')
    cur = connect.cursor()
    cur.execute(" SELECT * FROM user_interaction")
    com_rows = cur.fetchall()
    return render_template("view_comments.html", com_data=com_rows)


# -------------------------------------
# ROUTE: View Recipe List (Added Search Functionality - Soham)
# -------------------------------------
@app.route('/recipes')
def recipe_list():
    search_query = request.args.get('search_query', '')

    manager = RecipeManager()

    try:
        # Check if a search is being performed
        if search_query:
            # Use the manager's filter method
            recipes = manager.filterByPreference(search_query)
        else:
            # If no search, get all recipes
            recipes = manager.getAllRecipes()

    except sqlite3.Error as e:
        print(f"Error searching recipes: {e}")
        flash("An error occurred while searching for recipes.")
        recipes = []

    return render_template('recipe_list.html', recipes=recipes, search_query=search_query)


# -------------------------------------------------------------
# ADD RECIPE — Baraa (with validation + optional images)
# -------------------------------------------------------------
@app.route('/recipes/add', methods=['GET', 'POST'])
def add_recipe():
    """Display the add recipe form and handle submission."""
    if request.method == 'POST':
        name = request.form['name'].strip()
        ingredients = request.form['ingredients'].strip()
        instructions = request.form['instructions'].strip()
        diet_tags = request.form.getlist('diet[]')
        category = ",".join(diet_tags)

        if not name or not ingredients or not instructions:
            flash("All fields are required.")
            return redirect(url_for('add_recipe'))

        # get the logged-in user id
        conn = database_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
        user_id = cur.fetchone()[0]
        conn.close()

        # create recipe WITHOUT image_path in constructor
        new_recipe = Recipe(
            recipe_id=None,
            name=name,
            ingredients=ingredients,
            instructions=instructions
        )
        # attach extra attributes so RecipeManager can still use them
        new_recipe.category = category
        new_recipe.user_id = user_id

        manager = RecipeManager()
        recipe_id = manager.addRecipe(new_recipe)

        # ---------------------------
        # Handle images
        # ---------------------------
        files = request.files.getlist('recipe_images')

        if files:
            upload_folder = os.path.join(app.static_folder, 'recipe_images')
            os.makedirs(upload_folder, exist_ok=True)

            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                for file in files:
                    if not file or file.filename == '':
                        continue
                    if not allowed_file(file.filename):
                        continue

                    safe = secure_filename(file.filename)
                    unique = f"recipe_{recipe_id}_{safe}"
                    abs_path = os.path.join(upload_folder, unique)
                    rel_path = f"recipe_images/{unique}"

                    file.save(abs_path)

                    cur.execute("""
                        INSERT INTO recipe_image (recipe_id, image_path, upload_date)
                        VALUES (?, ?, DATE('now'))
                    """, (recipe_id, rel_path))

                conn.commit()

        # After adding, go back to list
        return redirect(url_for('recipe_list'))

    # On GET, just show the form
    return render_template('recipe_add.html')


# -------------------------------------------------------------
# EDIT RECIPE — Baraa (with validation + images list)
# -------------------------------------------------------------
@app.route('/recipes/edit/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    manager = RecipeManager()
    recipe = manager.getRecipeById(recipe_id)

    if recipe is None:
        return "Recipe not found", 404

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        ingredients = request.form.get('ingredients', '').strip()
        instructions = request.form.get('instructions', '').strip()

        if not name or not ingredients or not instructions:
            flash("All fields (name, ingredients, instructions) are required.")
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))

        updated_recipe = Recipe(recipe_id, name, ingredients, instructions)
        manager.editRecipe(recipe_id, updated_recipe)

        return redirect(url_for('recipe_list'))

    # Load all images for the gallery
    images = manager.getImagesForRecipe(recipe_id)
    return render_template('recipe_edit.html', recipe=recipe, images=images)


# -------------------------------------------------------------
# DELETE RECIPE — Baraa (also delete images)
# -------------------------------------------------------------
@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    # Delete images from disk + DB first
    upload_root = app.static_folder  # e.g., cmpt370_project_user_management/static

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT image_path FROM recipe_image WHERE recipe_id = ?", (recipe_id,))
        rows = cur.fetchall()

        for (image_path,) in rows:
            abs_path = os.path.join(upload_root, image_path)
            if os.path.exists(abs_path):
                os.remove(abs_path)

        cur.execute("DELETE FROM recipe_image WHERE recipe_id = ?", (recipe_id,))
        conn.commit()

    # Delete recipe row
    manager = RecipeManager()
    manager.deleteRecipe(recipe_id)

    flash("Recipe and its images deleted.")
    return redirect(url_for('recipe_list'))


# -------------------------------------
# ROUTE: Upload Recipe Image(s) - Baraa
# -------------------------------------
@app.route('/recipes/<int:recipe_id>/upload_image', methods=['POST'])
def upload_image(recipe_id):
    """
    Handles uploading one or more images for a recipe.
    Validates file type and saves to static/recipe_images.
    """
    manager = RecipeManager()
    if manager.getRecipeById(recipe_id) is None:
        flash("Recipe not found.")
        return redirect(url_for('recipe_list'))

    files = request.files.getlist('recipe_images')
    if not files:
        flash("No files selected.")
        return redirect(url_for('edit_recipe', recipe_id=recipe_id))

    upload_folder = os.path.join(app.static_folder, 'recipe_images')
    os.makedirs(upload_folder, exist_ok=True)

    saved_any = False

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        for file in files:
            if not file or file.filename == '':
                continue

            if not allowed_file(file.filename):
                flash("Some files were skipped (only .png, .jpg, .jpeg, .gif allowed).")
                continue

            safe_name = secure_filename(file.filename)
            unique_name = f"recipe_{recipe_id}_{safe_name}"
            abs_path = os.path.join(upload_folder, unique_name)
            rel_path = f"recipe_images/{unique_name}"

            file.save(abs_path)

            cur.execute("""
                INSERT INTO recipe_image (recipe_id, image_path, upload_date)
                VALUES (?, ?, DATE('now'))
            """, (recipe_id, rel_path))
            saved_any = True

        conn.commit()

    if saved_any:
        flash("Image(s) uploaded.")
    else:
        flash("No valid images uploaded.")

    return redirect(url_for('edit_recipe', recipe_id=recipe_id))


# -------------------------------------
# ROUTE: Delete a single Recipe Image - Baraa
# -------------------------------------
@app.route('/recipes/<int:recipe_id>/images/<int:image_id>/delete', methods=['POST'])
def delete_image(recipe_id, image_id):
    upload_root = app.static_folder

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT image_path
            FROM recipe_image
            WHERE image_id = ? AND recipe_id = ?
        """, (image_id, recipe_id))
        row = cur.fetchone()

        if not row:
            flash("Image not found.")
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))

        image_path = row[0]
        abs_path = os.path.join(upload_root, image_path)

        if os.path.exists(abs_path):
            os.remove(abs_path)

        cur.execute("DELETE FROM recipe_image WHERE image_id = ?", (image_id,))
        conn.commit()

    flash("Image deleted.")
    return redirect(url_for('edit_recipe', recipe_id=recipe_id))

# -------------------------------------
# ROUTE: Integrating Grocery list - Baraa
# -------------------------------------
@app.route('/add_ingredient_to_list', methods=['POST'])
def add_ingredient_to_list():
    if 'username' not in session:
        flash("Login required.")
        return redirect(url_for('login'))

    ingredient = request.form['ingredient'].strip()

    if ingredient == "":
        flash("Invalid ingredient.")
        return redirect(request.referrer)

    conn = database_connection(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
    user_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO grocery_list (user_id, item_text, quantity)
        VALUES (?, ?, ?)
    """, (user_id, ingredient, "1"))

    conn.commit()
    conn.close()

    flash(f"Added '{ingredient}' to grocery list ✔")
    return redirect(request.referrer)


# -------------------------------------------------------------
# MY RECIPES — Only show recipes created by this user
# -------------------------------------------------------------
@app.route('/my_recipes')
def my_recipes():
    if 'username' not in session:
        return redirect(url_for('login'))

    # find the logged-in user's ID
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
        result = cur.fetchone()

        if not result:
            flash("Error: Could not find user.")
            return redirect(url_for('logout'))

        user_id = result[0]

    manager = RecipeManager()
    recipes = manager.getRecipesByUser(user_id)

    return render_template('my_recipes.html', recipes=recipes)


# -------------------------------------------------------------
# Calendar Routes - Jordan
# -------------------------------------------------------------
# calendar view - determines calendar_id, sets in session, then renders calendar
@app.route('/calendar')
def calendar_view():
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        # get user_id integer from username in session and user_profile table
        username = session.get('username')
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM user_profile WHERE username = ?", (username,))
        user_id = cursor.fetchone()
        # get meal_plan_id to show single calendar for grouped meal plan
        #cursor.execute("SELECT meal_plan_id FROM meal_plan WHERE creator_id = ?", (user_id[0],))
        #meal_plan_id = cursor.fetchone()
        # Check for error in getting user_id / meal_plan_id
        if not user_id:
            print("Error in calendar view route - user_id missing")
            return redirect(url_for("home"))
        # Else get/create the calendar_id for this user and set session variable, render calendar
        calendar_id = calendar_service.create_or_get_calendar(connection, user_id[0])
        session["calendar_id"] = calendar_id
        return render_template("calendar.html", calendar_id=calendar_id)
    finally:
        # Close connection when done
        connection.close()

# load calendar events - FullCalendar API route to load all events for current calendar_id - Jordan
@app.route("/api/events")
def api_events():
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session
        if "calendar_id" not in session:
            return redirect(url_for('home'))
        calendar_id = session["calendar_id"]
        # Pull events from database
        events = calendar_service.get_calendar_events(connection, calendar_id)
        # return all calendar events in FullCalendar format
        full_calendar_events = []
        for event in events:
            full_calendar_events.append({
                "id": event["event_id"],
                "title": event["event_name"],
                "start": event["event_date"],
                "extendedProps": {
                    "timeSlot": event["event_time"],
                    "recipe_id": event["recipe_id"],
                    "recurrence_id": event["recurrence_id"]
                }
            })
        # return all calendar events
        return jsonify(full_calendar_events)
    finally:
        # Close connection when done
        connection.close()

# load calendar recipes - FullCalendar API route to load all recipes into calendar - Jordan
@app.route("/api/recipes")
def api_recipes():
    #Get all recipes from Recipe Manager
    manager = RecipeManager()
    recipes = manager.getAllRecipes()
    #Format to required FullCalendar format
    all_recipes = [
        {"recipe_id": rec.recipe_id, "recipe_name": rec.name
    }for rec in recipes]
    return jsonify(all_recipes)

# add calendar event - FullCalendar API route to add new event for current calendar_id - Jordan
@app.route("/api/events", methods=["POST"])
def api_add_event():
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session
        if "calendar_id" not in session:
            return redirect(url_for('home'))
        calendar_id = session["calendar_id"]
        # Create event using calendar service
        data = request.json
        event_id = calendar_service.insert_calendar_event(
            connection,
            recipe_id=data["recipe_id"],
            calendar_id=calendar_id,
            event_name=data["recipe_name"],
            event_date=data["event_date"],
            event_time=data["event_time"]
        )
        return jsonify({"event_id": event_id})
    except CalendarError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        # Close connection when done
        connection.close()

# delete calendar event - FullCalendar API route to delete event for current calendar_id - Jordan
@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def api_delete_event(event_id):
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session - not required but check for still in session
        if "calendar_id" not in session:
            return redirect(url_for('home'))
        deleted_event = calendar_service.delete_calendar_event(connection, event_id)
        #return True
        return jsonify({"event_deleted": True})
    finally:
        # Close connection when done
        connection.close()

# update calendar event - FullCalendar API route to update event for current calendar_id - Jordan
@app.route("/api/events/<int:event_id>", methods=["PATCH"])
def api_update_event(event_id):
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session
        if "calendar_id" not in session:
            return redirect(url_for('home'))
        # Get request update data
        data = request.json
        # Update event and return True
        calendar_service.update_event(
            connection,
            event_id,
            new_date=data.get("event_date"),
            new_time=data.get("event_time"),
            recipe_id=data.get("recipe_id")
        )
        return jsonify({"event_updated": True})
    except CalendarError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        # Close connection when done
        connection.close()

# add recurring event - FullCalendar API route to add new recurring event for current calendar_id - Jordan
@app.route("/api/recurring", methods=["POST"])
def api_add_recurring():
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session
        if "calendar_id" not in session:
            return redirect(url_for('home'))
        calendar_id = session["calendar_id"]
        # Get data from request
        data = request.json
        parent_event_id = data["parent_event_id"]
        frequency = data["frequency"]
        duration = data["duration"]
        start_date = data["start_date"]
        #Insert recurring event details into database recurring_event table
        recurring_event_id = calendar_service.insert_recurring_event(connection, parent_event_id, frequency, duration, start_date)
        #Generate calendar events based on recurrence details
        calendar_service.generate_recurring_events(connection,parent_event_id, recurring_event_id,frequency, duration, start_date)
        return jsonify({"recurring_event_id": recurring_event_id})
    except CalendarError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        #Close connection when done
        connection.close()

# delete recurring event series - FullCalendar API route to delete all recurring event for current calendar_id & recurring_event_id
@app.route("/api/recurring/<int:recurring_event_id>", methods=["DELETE"])
def api_delete_recurring_event(recurring_event_id):
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session - not required but check for still in session
        if "calendar_id" not in session:
            return redirect(url_for('home'))
        # Delete event(s)
        calendar_service.delete_recurring_series(connection, recurring_event_id)
        return jsonify({"event_deleted": True})
    finally:
        # Close connection when done
        connection.close()


# --------- Baraa: Image upload config + validation ---------
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------------------------------------
# STARTUP
# -------------------------------------------------------------
if __name__ == '__main__':
    conn = database_connection(DB_NAME)
    if conn is not None:
        create_tables(conn)
        conn.close()
    app.run(debug=True)

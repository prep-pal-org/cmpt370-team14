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
    return render_template('use_home_page.html')


# -------------------------------------------------------------
# ROUTES: Grocery List (Soham + Randi)
# -------------------------------------------------------------
@app.route('/grocery-list')
def grocery_list():
    if 'username' not in session:
        flash("You must be logged in to see your grocery list.")
        return redirect(url_for('login'))

    conn = database_connection(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
        user_result = cursor.fetchone()

        if not user_result:
            flash("Error finding user. Please log in again.")
            return redirect(url_for('logout'))

        current_user_id = user_result[0]

        cursor.execute(
            "SELECT item_id, item_text, quantity FROM grocery_list WHERE user_id = ?",
            (current_user_id,)
        )
        items_tuples = cursor.fetchall()

    except sqlite3.Error as e:
        print("Error fetching grocery list:", e)
        flash("An error occurred while fetching your list.")
        items_tuples = []
    finally:
        conn.close()

    items_list = [
        {"id": row[0], "item_text": row[1], "quantity": row[2]}
        for row in items_tuples
    ]

    return render_template('grocery_list.html', items=items_list)


@app.route('/add_grocery_item', methods=['POST'])
def add_grocery_item():
    if 'username' not in session:
        flash("You must be logged in to add items.")
        return redirect(url_for('login'))

    item_text = request.form['item_text']
    quantity = request.form['quantity']

    if item_text:
        conn = database_connection(DB_NAME)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
            user_result = cursor.fetchone()

            if not user_result:
                flash("Error finding user.")
                return redirect(url_for('logout'))

            current_user_id = user_result[0]

            cursor.execute("""
                INSERT INTO grocery_list (user_id, item_text, quantity)
                VALUES (?, ?, ?)
            """, (current_user_id, item_text, quantity))

            conn.commit()
        except sqlite3.Error as e:
            print("Error adding grocery item:", e)
            flash("Error adding item.")
        finally:
            conn.close()

    return redirect(url_for('grocery_list'))


@app.route('/remove_grocery_item', methods=['POST'])
def remove_grocery_item():
    if 'username' not in session:
        flash("You must be logged in to remove items.")
        return redirect(url_for('login'))

    item_id = request.form['item_id']

    conn = database_connection(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
        user_result = cursor.fetchone()

        if not user_result:
            flash("Error finding user.")
            return redirect(url_for('logout'))

        current_user_id = user_result[0]

        cursor.execute("""
            DELETE FROM grocery_list
            WHERE item_id = ? AND user_id = ?
        """, (item_id, current_user_id))

        conn.commit()

        if cursor.rowcount == 0:
            flash("Error: Item not found or you do not have permission.")
        else:
            flash("Item removed.")

    except sqlite3.Error as e:
        print("Error removing grocery item:", e)
        flash("Error removing item.")
    finally:
        conn.close()

    return redirect(url_for('grocery_list'))


# -------------------------------------------------------------
# USER PROFILE / LOGIN
# -------------------------------------------------------------
@app.route('/create_profile', methods=['GET', 'POST'])
def createProfile():
    if request.method == 'POST':
        userName = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hash_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        try:
            with sqlite3.connect('db/saucyapp.db') as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO user_profile (username, email, password)
                    VALUES (?, ?, ?)
                """, (userName, email, hash_password))

                conn.commit()
                flash("Profile created successfully!")
                return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash("Username already taken.")
            return redirect(url_for('createProfile'))

    return render_template('create_profile.html')


@app.route('/login_page', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userName = request.form['username']
        entered_password = request.form['password']

        with sqlite3.connect('db/saucyapp.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT password FROM user_profile WHERE username = ?", (userName,))
            result = cur.fetchone()

        if result is None:
            flash("Invalid username or password")
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


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# -------------------------------------------------------------
# RECIPE LIST + SEARCH — Baraa + Soham
# -------------------------------------------------------------
@app.route('/recipes')
def recipe_list():
    search_query = request.args.get('search_query', '')
    manager = RecipeManager()

    try:
        if search_query:
            recipes = manager.filterByPreference(search_query)
        else:
            recipes = manager.getAllRecipes()
    except sqlite3.Error as e:
        print(f"Error searching recipes: {e}")
        flash("An error occurred while searching.")
        recipes = []

    return render_template('recipe_list.html', recipes=recipes, search_query=search_query)


# -------------------------------------------------------------
# ADD RECIPE — Baraa (with validation + optional images)
# -------------------------------------------------------------
@app.route('/recipes/add', methods=['GET', 'POST'])
def add_recipe():
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

        # create recipe with user_id attached
        new_recipe = Recipe(
            recipe_id=None,
            name=name,
            ingredients=ingredients,
            instructions=instructions,
            image_path="",
            category=category,
            user_id=user_id
        )

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

        return redirect(url_for('recipe_list'))

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

    # find the user id
    cur.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
    user_id = cur.fetchone()[0]

    # insert ingredient as grocery item
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
# CALENDAR ROUTES — Jordan
# -------------------------------------------------------------
@app.route('/calendar')
def calendar_view():
    connection = sqlite3.connect(DB_NAME)

    try:
        username = session.get('username')
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM user_profile WHERE username = ?", (username,))
        user_id = cursor.fetchone()

        if not user_id:
            return redirect(url_for("home"))

        calendar_id = calendar_service.create_or_get_calendar(connection, user_id[0])
        session["calendar_id"] = calendar_id

        return render_template("calendar.html", calendar_id=calendar_id)

    finally:
        connection.close()


@app.route("/api/events")
def api_events():
    connection = sqlite3.connect(DB_NAME)

    try:
        if "calendar_id" not in session:
            return redirect(url_for('home'))

        calendar_id = session["calendar_id"]
        events = calendar_service.get_calendar_events(connection, calendar_id)

        full_calendar_events = [
            {
                "id": event["event_id"],
                "title": event["event_name"],
                "start": event["event_date"],
                "extendedProps": {
                    "timeSlot": event["event_time"],
                    "recipe_id": event["recipe_id"]
                }
            } for event in events
        ]

        return jsonify(full_calendar_events)
    finally:
        connection.close()


@app.route("/api/events", methods=["POST"])
def api_add_event():
    connection = sqlite3.connect(DB_NAME)

    try:
        if "calendar_id" not in session:
            return redirect(url_for('home'))

        data = request.json
        calendar_id = session["calendar_id"]

        event_id = calendar_service.insert_calendar_event(
            connection,
            recipe_id=data["recipe_id"],
            calendar_id=calendar_id,
            event_name=data["event_name"],
            event_date=data["event_date"],
            event_time=data["event_time"]
        )

        return jsonify({"event_id": event_id})
    except CalendarError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        connection.close()


@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def api_delete_event(event_id):
    connection = sqlite3.connect(DB_NAME)

    try:
        if "calendar_id" not in session:
            return redirect(url_for('home'))

        calendar_service.delete_calendar_event(connection, event_id)
        return jsonify({"event_deleted": True})
    finally:
        connection.close()


@app.route("/api/events/<int:event_id>", methods=["PATCH"])
def api_update_event(event_id):
    connection = sqlite3.connect(DB_NAME)

    try:
        if "calendar_id" not in session:
            return redirect(url_for('home'))

        data = request.json

        calendar_service.update_event(
            connection,
            event_id,
            new_date=data.get("event_date"),
            new_time=data.get("event_time")
        )

        return jsonify({"event_updated": True})

    except CalendarError as e:
        return jsonify({"error": str(e)}), 409

    finally:
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

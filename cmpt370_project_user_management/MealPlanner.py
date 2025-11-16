from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from FlaskConnections.RecipeManager import RecipeManager
import os

from backups.setup_database_backup import database_connection
from Model.Recipe import Recipe


import sqlite3
import bcrypt

from db.setup_database import database_connection, create_tables #update_tables
from Model.calendar_service import CalendarService

app = Flask(__name__)
app.secret_key = "saucy"
DB_NAME = "db/saucyapp.db"
calendar_service = CalendarService()

# Routing to a home page - Randi.
@app.route('/')
def home():
    return render_template('use_home_page.html')

# Rout to the old home page -Randi
@app.route('/old_home')
def old_home():
    return render_template('homePage.html')

# Routing for the grocery list
@app.route('/grocery-list')
def grocery_list():
    current_user_id = 1

    conn = database_connection(DB_NAME)
    cursor = conn.cursor()

    # Fetch items for the current user
    cursor.execute("SELECT item_id, item_text, quantity FROM grocery_list WHERE user_id = ?", (current_user_id,))
    items_tuples = cursor.fetchall()
    conn.close()

    # Convert list of tuples to a list of dicts
    items_list = []
    for row in items_tuples:
        items_list.append({"id": row[0], "item_text": row[1], "quantity": row[2]})

    return render_template('grocery_list.html', items=items_list)


# Route to add an item to the grocery list
@app.route('/add_grocery_item', methods=['POST'])
def add_grocery_item():
    if request.method == 'POST':
        item_text = request.form['item_text']

        quantity = request.form['quantity']

        current_user_id = 1

        if item_text:
            conn = database_connection(DB_NAME)
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO grocery_list (user_id, item_text, quantity) VALUES (?, ?, ?)",
                               (current_user_id, item_text, quantity))
                conn.commit()
            except sqlite3.Error as e:
                print("Error adding grocery item:", e)
            finally:
                conn.close()

        # Redirect back to the grocery list page
        return redirect(url_for('grocery_list'))


@app.route('/remove_grocery_item', methods=['POST'])
def remove_grocery_item():
    if request.method == 'POST':
        item_id = request.form['item_id']

        conn = database_connection(DB_NAME)
        cursor = conn.cursor()
        try:
            # Delete the item based on its unique item_id
            cursor.execute("DELETE FROM grocery_list WHERE item_id = ?", (item_id,))
            conn.commit()
        except sqlite3.Error as e:
            print("Error removing grocery item:", e)
        finally:
            conn.close()

    # Redirect back to the grocery list page
    return redirect(url_for('grocery_list'))

# User profile creation -Randi
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
    """Display the recipe list page."""
    # For now, just a placeholder page
    # Later we can connect this to RecipeManager
    manager = RecipeManager()
    recipes = manager.getAllRecipes()
    return render_template('recipe_list.html')

    conn = database_connection(DB_NAME)
    cursor = conn.cursor()

    recipes_list = []
    try:
        if search_query:
            search_term = f"%{search_query}%"
            cursor.execute(
                "SELECT recipe_id, recipe_name, description FROM recipe WHERE recipe_name LIKE ? OR ingredients LIKE ?",
                (search_term, search_term)
            )
        else:
            cursor.execute("SELECT recipe_id, recipe_name, description FROM recipe")

        recipes_list = cursor.fetchall()

    except sqlite3.Error as e:
        print(f"Error searching recipes: {e}")
        flash("An error occurred while searching for recipes.")  # Let the user know
    finally:
        conn.close()

    return render_template('recipe_list.html', recipes=recipes_list, search_query=search_query)

# -------------------------------------
# ROUTE: Add a Recipe - Baraa
# -------------------------------------
@app.route('/recipes/add', methods=['GET', 'POST'])
def add_recipe():
    """Display the add recipe form and handle submission."""
    if request.method == 'POST':
        # For now, just print to console instead of saving
        name = request.form['name']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']

        print(f"Recipe added: {name}")
        print(f"Ingredients: {ingredients}")
        print(f"Instructions: {instructions}")

        new_recipe = Recipe(None, name, ingredients, instructions)
        manager = RecipeManager()
        manager.addRecipe(new_recipe)

        # After adding, go back to list
        return redirect(url_for('recipe_list'))

    # On GET, just show the form
    return render_template('recipe_add.html')

# -------------------------------------
# ROUTE: Edit Recipe - Baraa
# -------------------------------------
@app.route('/recipes/edit/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    manager = RecipeManager()
    recipe = manager.getRecipeById(recipe_id)

    if recipe is None:
        return "Recipe not found", 404

    if request.method == 'POST':
        name = request.form['name']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']

        updated_recipe = Recipe(recipe_id, name, ingredients, instructions)
        manager.editRecipe(recipe_id, updated_recipe)

        return redirect(url_for('recipe_list'))
    return render_template('recipe_edit.html', recipe=recipe)


#Calendar View route - Jordan
@app.route('/calendar')
def calendar_view():
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        #get user_id integer from username in session and user_profile table
        username = session['username']
        cursor = connection.cursor()
        cursor.execute(" SELECT user_id FROM user_profile WHERE username = ?", (username,))
        user_id = cursor.fetchone()
        if user_id[0] is None: #Error in username in session or user_profile data
            print("user_id is None - calendar_view function")
            return redirect(url_for("home"))
        else: #Else get/create the calendar_id for this user and set session variable, render calendar
            calendar_id = calendar_service.create_new_calendar(connection, user_id[0])
            session["calendar_id"] = calendar_id
            return render_template("calendar.html", calendar_id=calendar_id)
    except sqlite3.Error as e:
        print("Error getting/creating calendar:", e)
    finally:
        #Close connection when done
        connection.close()

#API Route - Get Events for current calendar - Jordan
@app.route("/api/events")
def api_events():
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session
        if "calendar_id" not in session:
            print("Redirect for no calendar_id - api_events")
            return redirect(url_for('home'))
        calendar_id = session["calendar_id"]
        #Pull events from database
        events = calendar_service.get_calendar_events(connection,calendar_id)
        #Convert events to FullCalendar JSON format
        full_calendar_events = []
        for event in events:
            full_calendar_events.append({
                "id": event["event_id"],
                "title": event["event_name"],
                "start": event["event_date"],
                "extendedProps":{
                    "timeSlot": event["event_time"],
                    "recipe_id": event["recipe_id"]
                }
            })
        #return all calendar events
        return jsonify(full_calendar_events)
    except sqlite3.Error as e:
        print("Error getting calendar events:", e)
    finally:
        #Close connection when done
        connection.close()


#API - Add new event - Jordan
@app.route("/api/events", methods=["POST"])
def api_add_event():
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        #Get Calendar_id from session
        if "calendar_id" not in session:
            print("Redirect for no calendar_id - api_add_event")
            return redirect(url_for('home'))
        data = request.json
        # Get calendar_id from session user_id
        calendar_id = session["calendar_id"]
        #Create event using calendar service
        event_id = calendar_service.insert_calendar_event(
            connection,
            recipe_id=data["recipe_id"],
            calendar_id=calendar_id,
            event_name=data["event_name"],
            event_date=data["event_date"],
            event_time=data["event_time"]
        )
        return jsonify({"event_id": event_id})
    except sqlite3.Error as e:
        print("Error adding event:", e)
    finally:
        #Close connection when done
        connection.close()

#API - delete existing event - Jordan
@app.route("/api/events/<int:event_id>",methods=["DELETE"])
def api_delete_event(event_id):
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        #Get calender_id from session - not used but kept to ensure still part of the session
        if "calendar_id" not in session:
            print("Redirect for no calender_id - api_delete_event")
            return redirect(url_for('home'))
        deleted_event = calendar_service.delete_calendar_event(connection,event_id)
        return jsonify({"event_deleted": True})
    except sqlite3.Error as e:
        print("Error deleting event:". e)
    finally:
        #Close connection when done
        connection.close()

# -------------------------------------
# ROUTE: Delete a Recipe - Baraa
# -------------------------------------
@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    """Delete a recipe from the database by ID and reload the recipe list."""
    manager = RecipeManager()
    manager.deleteRecipe(recipe_id)
    return redirect(url_for('recipe_list'))

# -------------------------------------
# ROUTE: Upload Recipe Image - Baraa
# -------------------------------------
@app.route('/recipes/<int:recipe_id>/upload_image', methods=['POST'])
def upload_image(recipe_id):
    image = request.files['image']

    if image.filename == "":
        return "No file selected", 400

    save_path = os.path.join('Static', 'images', image.filename)
    image.save(save_path)

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO recipe_image (recipe_id, image_path) VALUES (?, ?)",
                    (recipe_id, save_path))
        conn.commit()

    return redirect(url_for('edit_recipe', recipe_id=recipe_id))




if __name__ == '__main__':
    # First, make sure all tables exist before running the app
    conn = database_connection(DB_NAME)
    if conn is not None:
        create_tables(conn)
        #update_tables(conn)
        conn.close()
    app.run(debug=True)

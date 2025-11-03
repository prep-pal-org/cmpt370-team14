from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import bcrypt

from db.setup_database import database_connection, create_tables, update_tables

app = Flask(__name__)
DB_NAME = "db/saucyapp.db"

# Routing to a home page - Randi.
@app.route('/')
def home():
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
    if request.method == 'POST':
        userName = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hash_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        with sqlite3.connect('db/saucyapp.db') as conn:
            cur = conn.cursor()
            cur.execute(" INSERT INTO user_profile (username, email, password) VALUES (?, ?,?)",
                           (userName,email,hash_password))
            conn.commit()
        return render_template('homePage.html')
    else:
        return render_template('create_profile.html')

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
# ROUTE: View Recipe List
# -------------------------------------
@app.route('/recipes')
def recipe_list():
    """Display the recipe list page."""
    # For now, just a placeholder page
    # Later we can connect this to RecipeManager
    return render_template('recipe_list.html')


# -------------------------------------
# ROUTE: Add a Recipe
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

        # After adding, go back to list
        return redirect(url_for('recipe_list'))

    # On GET, just show the form
    return render_template('recipe_add.html')



if __name__ == '__main__':
    # First, make sure all tables exist before running the app
    conn = database_connection(DB_NAME)
    if conn is not None:
        create_tables(conn)
        update_tables(conn)
        conn.close()
    app.run(debug=True)
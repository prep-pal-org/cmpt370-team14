from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from cmpt370_project_user_management.FlaskConnections.RecipeManager import RecipeManager

import os

from cmpt370_project_user_management.db.setup_database import database_connection

from cmpt370_project_user_management.Model.Recipe import Recipe


import sqlite3

app = Flask(__name__)
app.secret_key = "saucy"
DB_NAME = "db/saucyapp.db"
calendar_service = CalendarService()


# Routing to a home page - Randi.
@app.route('/')
def home():
    return render_template('homePage.html')

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





@app.route('/create_profile', methods=['GET', 'POST'])
def createProfile():
    if request.method == 'POST':
        userName = request.form['username']
        email = request.form['email']
        password = request.form['password']
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, "db", "saucyapp.db")

        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(" INSERT INTO user_profile (username, email, password) VALUES (?, ?,?)",
                           (userName,email,password))
            conn.commit()
        return render_template('homePage.html')
    else:
        return render_template('create_profile.html')

@app.route('/user_list_for_testing')
def user_list_for_testing():
    connect = sqlite3.connect('db/saucyapp.db')
    cur = connect.cursor()
    cur.execute(" SELECT * FROM user_profile")
    rows = cur.fetchall()
    return render_template("user_list_for_testing.html", data=rows)

# -------------------------------------
# ROUTE: View Recipe List
# -------------------------------------
@app.route('/recipes')
def recipe_list():
    """Display the recipe list page."""
    # For now, just a placeholder page
    # Later we can connect this to RecipeManager
    manager = RecipeManager()
    recipes = manager.getAllRecipes()
    return render_template('recipe_list.html', recipes=recipes, search_query="")


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
    app.run(debug=True)
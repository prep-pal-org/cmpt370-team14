from flask import Flask, render_template, request, redirect, url_for
from Controller.RecipeManager import RecipeManager
from Model.Recipe import Recipe
import sqlite3

app = Flask(__name__)
manager = RecipeManager()


# Routing to a home page.
@app.route('/')
def home():
    return render_template('homePage.html')

@app.route('/create_profile', methods=['GET', 'POST'])
def createProfile():
    if request.method == 'POST':
        userName = request.form['username']
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect('db/saucyapp.db') as conn:
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

# --------------------------------------------------------
# ROUTE: Show all recipes
# Baraa
# --------------------------------------------------------
@app.route('/recipes')
def recipe_list():
    """Display all recipes from the database."""
    recipes = manager.getAllRecipes()
    return render_template('recipe_list.html', recipes=recipes)


# --------------------------------------------------------
# ROUTE: Add a new recipe
# Baraa
# --------------------------------------------------------
@app.route('/recipes/add', methods=['GET', 'POST'])
def add_recipe():
    """Handle the form to add a new recipe."""
    if request.method == 'POST':
        name = request.form['name']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']

        new_recipe = Recipe(name=name, ingredients=ingredients, instructions=instructions)
        manager.addRecipe(new_recipe)

        return redirect(url_for('recipe_list'))
    return render_template('recipe_add.html')


# --------------------------------------------------------
# ROUTE: Delete a recipe
# Baraa
# --------------------------------------------------------
@app.route('/recipes/delete/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    """Delete a recipe by its ID."""
    manager.deleteRecipe(recipe_id)
    return redirect(url_for('recipe_list'))


if __name__ == '__main__':
    app.run(debug=True)
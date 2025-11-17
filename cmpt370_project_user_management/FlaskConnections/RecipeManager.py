"""
Baraa
RecipeManager Controller Class
------------------------------
Responsible for managing all Recipe objects in the system.
Handles CRUD (Create, Read, Update, Delete) operations using SQLite.
Acts as the data access layer between the Flask UI and the database.
"""

import os
import sqlite3
from cmpt370_project_user_management.Model.Recipe import Recipe




BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "saucyapp.db")
print("🗂 Using database at:", DB_PATH)



class RecipeManager:
    """
    Handles interactions with the recipe database table.
    Maintains a list of Recipe objects and provides methods to manage them.
    """

    def __init__(self):
        """
        Constructor for RecipeManager.
        Initializes an empty recipe list.
        """
        self.recipeList: list[Recipe] = []

    # --------------------------------------------------------------

    def _connect(self):
        """
        Creates and returns a database connection to the SQLite database.

        :return: sqlite3.Connection object
        """
        return sqlite3.connect(DB_PATH)

    # --------------------------------------------------------------

    def addRecipe(self, r: Recipe) -> None:
        """
        Adds a new Recipe object to the database.

        :param r: A Recipe object to be added.
        :return: None
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO recipe (recipe_name, ingredients, instructions, category, cooking_time)
                VALUES (?, ?, ?, '', 0)
            """, (r.name, r.ingredients, r.instructions))
            conn.commit()
        print(f"✅ Recipe '{r.name}' added successfully!")

    # --------------------------------------------------------------

    def editRecipe(self, recipe_id: int, newRecipe: Recipe) -> None:
        """
        Updates an existing recipe in the database.

        :param recipe_id: ID of the recipe to edit.
        :param newRecipe: A Recipe object with updated values.
        :return: None
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE recipe
                SET recipe_name = ?, ingredients = ?, instructions = ?
                WHERE recipe_id = ?
            """, (newRecipe.name, newRecipe.ingredients,
                  newRecipe.instructions, recipe_id))
            conn.commit()
        print(f"✏️ Recipe ID {recipe_id} updated successfully!")

    # --------------------------------------------------------------

    def deleteRecipe(self, recipe_id: int) -> None:
        """
        Deletes a recipe from the database by its ID.

        :param recipe_id: The recipe's ID to delete.
        :return: None
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM recipe WHERE recipe_id = ?", (recipe_id,))
            conn.commit()
        print(f"🗑️ Recipe ID {recipe_id} deleted successfully!")

    # --------------------------------------------------------------

    def filterByPreference(self, pref: str) -> list[Recipe]:
        """
        Returns a filtered list of recipes based on a preference string (e.g., part of the name).

        :param pref: Search string to filter recipe names.
        :return: A list of matching Recipe objects.
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT recipe_id, recipe_name, ingredients, instructions, '' 
                FROM recipe WHERE recipe_name LIKE ?
            """, (f"%{pref}%",))
            rows = cur.fetchall()
        self.recipeList = [Recipe(*row) for row in rows]
        print(f"🔍 Found {len(self.recipeList)} recipes matching '{pref}'.")
        return self.recipeList

    # --------------------------------------------------------------

    def getRecipeById(self, recipe_id: int) -> Recipe:
        """
        Retrieves a single Recipe object from the database by ID.

        :param recipe_id: The recipe's unique ID.
        :return: Recipe object if found, otherwise None.
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT recipe_id, recipe_name, ingredients, instructions, ''
                FROM recipe WHERE recipe_id = ?
            """, (recipe_id,))
            row = cur.fetchone()
        if row:
            print(f"✅ Found recipe ID {recipe_id}.")
            return Recipe(*row)
        else:
            print(f"⚠️ Recipe ID {recipe_id} not found.")
            return None

    # --------------------------------------------------------------

    def getAllRecipes(self) -> list[Recipe]:
        """
        Retrieves all recipes from the database and stores them as Recipe objects.

        :return: A list of Recipe objects.
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT recipe_id, recipe_name, ingredients, instructions, ''
                FROM recipe
            """)
            rows = cur.fetchall()
        self.recipeList = [Recipe(*row) for row in rows]
        print(f"📖 Loaded {len(self.recipeList)} recipes from the database.")
        return self.recipeList

    #kayo -
    #todo write class to convert instructions to individual steps and the getSteps.


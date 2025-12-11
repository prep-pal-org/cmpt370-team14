"""
Baraa
RecipeManager Controller Class
Fully corrected for:
✔ category
✔ user_id
✔ image_path loaded separately
✔ Recipe constructor compatibility
"""

import os
import sqlite3
from cmpt370_project_user_management.Model.Recipe import Recipe

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "saucyapp.db")
print("Using database at:", DB_PATH)


class RecipeManager:

    def __init__(self):
        self.recipeList = []

    def _connect(self):
        return sqlite3.connect(DB_PATH)

    # --------------------------------------------------------------
    # ADD RECIPE
    # --------------------------------------------------------------
    def addRecipe(self, r: Recipe) -> int:
        with self._connect() as conn:
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO recipe (recipe_name, ingredients, instructions, category, user_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                r.name,
                r.ingredients,
                r.instructions,
                getattr(r, "category", ""),
                getattr(r, "user_id", None)
            ))

            recipe_id = cur.lastrowid
            conn.commit()

        print(f"Added recipe '{r.name}' with ID {recipe_id}")
        return recipe_id

    # --------------------------------------------------------------
    # BUILD RECIPE OBJECT
    # --------------------------------------------------------------
    def _buildRecipe(self, row):
        """
        Expects row: (recipe_id, name, ingredients, instructions, image_path, category, user_id)
        """
        recipe_id, name, ingredients, instructions, image_path, category, user_id = row

        r = Recipe(recipe_id, name, ingredients, instructions)
        r.image_path = image_path
        r.category = category if category else ""
        r.user_id = user_id
        return r

    # --------------------------------------------------------------
    # GET RECIPE BY ID
    # --------------------------------------------------------------
    def getRecipeById(self, recipe_id: int):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.recipe_id, r.recipe_name, r.ingredients, r.instructions,
                       COALESCE((SELECT image_path FROM recipe_image i WHERE i.recipe_id = r.recipe_id ORDER BY upload_date DESC, image_id DESC LIMIT 1), '') AS image_path,
                       r.category,
                       r.user_id
                FROM recipe r
                WHERE r.recipe_id = ?
            """, (recipe_id,))

            row = cur.fetchone()

        return self._buildRecipe(row) if row else None

    # --------------------------------------------------------------
    # GET ALL RECIPES
    # --------------------------------------------------------------
    def getAllRecipes(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.recipe_id, r.recipe_name, r.ingredients, r.instructions,
                       COALESCE((SELECT image_path FROM recipe_image i WHERE i.recipe_id = r.recipe_id ORDER BY upload_date DESC, image_id DESC LIMIT 1), '') AS image_path,
                       r.category,
                       r.user_id
                FROM recipe r
            """)
            rows = cur.fetchall()
        return [self._buildRecipe(row) for row in rows]

    # --------------------------------------------------------------
    # FILTERED RECIPES
    # --------------------------------------------------------------
    def getFilteredRecipes(self, search_query="", sort_by="newest", diet_filter=""):
        conn = self._connect()
        cur = conn.cursor()

        sql = """
            SELECT r.recipe_id, r.recipe_name, r.ingredients, r.instructions,
                   COALESCE((SELECT image_path FROM recipe_image i WHERE i.recipe_id = r.recipe_id ORDER BY upload_date DESC, image_id DESC LIMIT 1), '') AS image_path,
                   r.category,
                   r.user_id
            FROM recipe r
            WHERE 1=1
        """

        params = []

        if search_query:
            sql += " AND (r.recipe_name LIKE ? OR r.ingredients LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        if diet_filter == "gluten_free":
            sql += " AND r.category LIKE '%Gluten Free%'"
        elif diet_filter == "lactose_free":
            sql += " AND r.category LIKE '%Lactose Free%'"
        elif diet_filter == "peanut_allergy":
            sql += " AND r.category LIKE '%Peanut Allergy%'"

        if sort_by == "az":
            sql += " ORDER BY r.recipe_name ASC"
        elif sort_by == "za":
            sql += " ORDER BY r.recipe_name DESC"
        else:
            sql += " ORDER BY r.recipe_id DESC"

        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()

        return [self._buildRecipe(row) for row in rows]

    # --------------------------------------------------------------
    # GET IMAGES FOR RECIPE
    # --------------------------------------------------------------
    def getImagesForRecipe(self, recipe_id: int):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT image_id, image_path
                FROM recipe_image
                WHERE recipe_id = ?
                ORDER BY upload_date DESC, image_id DESC
            """, (recipe_id,))
            rows = cur.fetchall()
        return [{"image_id": r[0], "image_path": r[1]} for r in rows]

    # --------------------------------------------------------------
    # GET USER'S RECIPES
    # --------------------------------------------------------------
    def getRecipesByUser(self, user_id: int):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.recipe_id, r.recipe_name, r.ingredients, r.instructions,
                       COALESCE((SELECT image_path FROM recipe_image i WHERE i.recipe_id = r.recipe_id ORDER BY upload_date DESC, image_id DESC LIMIT 1), '') AS image_path,
                       r.category,
                       r.user_id
                FROM recipe r
                WHERE r.user_id = ?
            """, (user_id,))

            rows = cur.fetchall()
        return [self._buildRecipe(row) for row in rows]

    # --------------------------------------------------------------
    # GET FAVORITE RECIPES
    # --------------------------------------------------------------
    def getFavoriteRecipesByUser(self, user_id: int):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.recipe_id, r.recipe_name, r.ingredients, r.instructions,
                       COALESCE((SELECT image_path FROM recipe_image i WHERE i.recipe_id = r.recipe_id ORDER BY upload_date DESC, image_id DESC LIMIT 1), '') AS image_path,
                       r.category,
                       r.user_id
                FROM recipe r
                JOIN favorite_recipes_use f ON r.recipe_id = f.recipe_id
                WHERE f.user_id = ?
            """, (user_id,))
            rows = cur.fetchall()
        return [self._buildRecipe(row) for row in rows]

    # --------------------------------------------------------------
    # EDIT & DELETE
    # --------------------------------------------------------------
    def editRecipe(self, recipe_id: int, newRecipe: Recipe):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE recipe
                SET recipe_name = ?, ingredients = ?, instructions = ?
                WHERE recipe_id = ?
            """, (newRecipe.name, newRecipe.ingredients, newRecipe.instructions, recipe_id))
            conn.commit()

    def deleteRecipe(self, recipe_id: int):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM recipe WHERE recipe_id = ?", (recipe_id,))
            conn.commit()

    # --------------------------------------------------------------
    # STEPS
    # --------------------------------------------------------------
    def saveSteps(self, recipe_id: int, steps: list):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM recipe_steps WHERE recipe_id = ?", (recipe_id,))
            for step_number, step, duration in steps:
                cur.execute("""
                    INSERT INTO recipe_steps (recipe_id, step_number, step, duration)
                    VALUES (?, ?, ?, ?)
                """, (recipe_id, step_number, step, duration))
            conn.commit()

    def getSteps(self, recipe_id):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT step_id, step_number, step, duration
                FROM recipe_steps
                WHERE recipe_id = ?
                ORDER BY step_number ASC
            """, (recipe_id,))
            return cur.fetchall()

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
print("🗂 Using database at:", DB_PATH)


class RecipeManager:

    def __init__(self):
        self.recipeList = []

    def _connect(self):
        return sqlite3.connect(DB_PATH)

    # --------------------------------------------------------------
    # ADD RECIPE — uses 5 columns (name, ingredients, instructions, category, user_id)
    # --------------------------------------------------------------
    def addRecipe(self, r: Recipe) -> int:
        """
        Adds a new recipe to DB.
        Required DB columns:
        recipe_name, ingredients, instructions, category, user_id
        """
        with self._connect() as conn:
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO recipe (recipe_name, ingredients, instructions, category, user_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                r.name,
                r.ingredients,
                r.instructions,
                getattr(r, "category", ""),   # safe if not set
                getattr(r, "user_id", None)   # safe if not set
            ))

            recipe_id = cur.lastrowid
            conn.commit()

        print(f"✅ Added recipe '{r.name}' with ID {recipe_id}")
        return recipe_id

    # --------------------------------------------------------------
    # Helper: Build a Recipe object + attach image_path
    # --------------------------------------------------------------
    def _buildRecipe(self, row):
        """
        row = (recipe_id, name, ingredients, instructions, image_path)
        """
        recipe_id, name, ingredients, instructions, image_path = row

        r = Recipe(recipe_id, name, ingredients, instructions)
        r.image_path = image_path  # Store image separately for display
        return r

    # --------------------------------------------------------------
    # GET RECIPE BY ID
    # --------------------------------------------------------------
    def getRecipeById(self, recipe_id: int):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.recipe_id,
                       r.recipe_name,
                       r.ingredients,
                       r.instructions,
                       COALESCE(
                           (SELECT image_path
                            FROM recipe_image i
                            WHERE i.recipe_id = r.recipe_id
                            ORDER BY upload_date DESC, image_id DESC
                            LIMIT 1),
                           ''
                       ) AS image_path
                FROM recipe r
                WHERE r.recipe_id = ?
            """, (recipe_id,))

            row = cur.fetchone()

        return self._buildRecipe(row) if row else None

    # --------------------------------------------------------------
    # GET ALL RECIPES (for homepage)
    # --------------------------------------------------------------
    def getAllRecipes(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.recipe_id,
                       r.recipe_name,
                       r.ingredients,
                       r.instructions,
                       COALESCE(
                           (SELECT image_path
                            FROM recipe_image i
                            WHERE i.recipe_id = r.recipe_id
                            ORDER BY upload_date DESC, image_id DESC
                            LIMIT 1),
                           ''
                       ) AS image_path
                FROM recipe r
            """)

            rows = cur.fetchall()

        return [self._buildRecipe(row) for row in rows]

    # --------------------------------------------------------------
    # FILTER BY SEARCH
    # --------------------------------------------------------------
    def filterByPreference(self, pref: str):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.recipe_id,
                       r.recipe_name,
                       r.ingredients,
                       r.instructions,
                       COALESCE(
                           (SELECT image_path
                            FROM recipe_image i
                            WHERE i.recipe_id = r.recipe_id
                            ORDER BY upload_date DESC, image_id DESC
                            LIMIT 1),
                           ''
                       ) AS image_path
                FROM recipe r
                WHERE r.recipe_name LIKE ?
            """, (f"%{pref}%",))

            rows = cur.fetchall()

        return [self._buildRecipe(row) for row in rows]

    # --------------------------------------------------------------
    # GET ALL IMAGES FOR A RECIPE
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
    # GET ONLY THIS USER’S RECIPES
    # --------------------------------------------------------------
    def getRecipesByUser(self, user_id: int):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.recipe_id,
                       r.recipe_name,
                       r.ingredients,
                       r.instructions,
                       COALESCE(
                           (SELECT image_path
                            FROM recipe_image i
                            WHERE i.recipe_id = r.recipe_id
                            ORDER BY upload_date DESC, image_id DESC
                            LIMIT 1),
                           ''
                       ) AS image_path
                FROM recipe r
                WHERE r.user_id = ?
            """, (user_id,))

            rows = cur.fetchall()

        return [self._buildRecipe(row) for row in rows]

    # --------------------------------------------------------------
    # GET FAVORITE RECIPE
    # --------------------------------------------------------------

    def getFavoriteRecipesByUser(self, user_id: int):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.recipe_id,
                       r.recipe_name,
                       r.ingredients,
                       r.instructions,
                       COALESCE(
                           (SELECT image_path
                            FROM recipe_image i
                            WHERE i.recipe_id = r.recipe_id
                            ORDER BY upload_date DESC, image_id DESC
                            LIMIT 1),
                           ''
                       ) AS image_path
                FROM recipe r
                JOIN favorite_recipes_use f ON r.recipe_id = f.recipe_id
                WHERE f.user_id = ?
            """, (user_id,))

            rows = cur.fetchall()

        return [self._buildRecipe(row) for row in rows]

    # --------------------------------------------------------------
    # EDIT RECIPE
    # --------------------------------------------------------------
    def editRecipe(self, recipe_id: int, newRecipe: Recipe):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE recipe
                SET recipe_name = ?, ingredients = ?, instructions = ?
                WHERE recipe_id = ?
            """, (newRecipe.name, newRecipe.ingredients,
                  newRecipe.instructions, recipe_id))

            conn.commit()

    # --------------------------------------------------------------
    # DELETE RECIPE
    # --------------------------------------------------------------
    def deleteRecipe(self, recipe_id: int):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM recipe WHERE recipe_id = ?", (recipe_id,))
            conn.commit()

    # --------------------------------------------------------------
    # SAVE RECIPE STEPS
    # -------------------------------------------------------------KAYO
    def saveSteps(self, recipe_id: int, steps: list):
        with self._connect() as conn:
            cur = conn.cursor()
            # Delete old steps (if editing)
            cur.execute("DELETE FROM recipe_steps WHERE recipe_id = ?", (recipe_id,))
            # Insert new steps
            for step_number, step, duration in steps:
                cur.execute("""
                    INSERT INTO recipe_steps (recipe_id, step_number, step, duration)
                    VALUES (?, ?, ?, ?)
                """, (recipe_id, step_number, step, duration))
            conn.commit()

    # --------------------------------------------------------------
    # GET RECIPE STEPS
    # -------------------------------------------------------------KAYO
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


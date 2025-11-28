"""
Baraa
RecipeViewer View Class
-----------------------
Responsible for displaying recipe-related information to the user.
Acts as the presentation layer between the RecipeManager (controller) and the UI.
"""

from FlaskConnections import RecipeManager


class RecipeViewer:
    """
    Handles presentation of recipes and messages for the user.
    """

    def __init__(self, manager: RecipeManager):
        """
        Constructor for RecipeViewer.

        :param manager: Instance of RecipeManager used to access recipes.
        """
        self.manager = manager

    # --------------------------------------------------------------

    def shoeRecipeList(self) -> None:
        """
        Displays all recipes retrieved from the RecipeManager.

        :return: None
        """
        recipes = self.manager.getAllRecipes()
        if not recipes:
            print("⚠️ No recipes found in the database.")
            return

        print("\n=== Recipe List ===")
        for r in recipes:
            print(f"ID {r.recipe_id}: {r.name} — {r.ingredients[:40]}...")
        print("===================")

    # --------------------------------------------------------------

    def displayMessage(self, msg: str) -> None:
        """
        Displays a general informational message.

        :param msg: The message to show.
        :return: None
        """
        print(f"[MESSAGE]: {msg}")

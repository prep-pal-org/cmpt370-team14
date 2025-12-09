"""
Baraa
Recipe Model Class
------------------
Represents a single Recipe entity in the SaucyApp system.
Stores basic attributes like name, ingredients, and instructions.
Images are stored in a separate recipe_image table.
"""

class Recipe:
    """
    Represents a Recipe with an ID, name, ingredients, and instructions.
    Note: Images are NOT stored here (they belong in the recipe_image table).
    """

    def __init__(self, recipe_id: int = None, name: str = "",
                 ingredients: str = "", instructions: str = ""):
        """
        Constructor for the Recipe class.
        """

        self.recipe_id = recipe_id
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions

        self.image_path = ""
        self.category = ""
        self.user_id = None

        # prevents Render crash
        self.reactions_dict = {}
    # --------------------------------------------------------------

    def displayRecipe(self) -> None:
        """ Debug print of recipe data. """
        print("\n=== Recipe Details ===")
        print(f"Recipe ID: {self.recipe_id}")
        print(f"Name: {self.name}")
        print(f"Ingredients: {self.ingredients}")
        print(f"Instructions: {self.instructions}")

    # --------------------------------------------------------------

    def getDetails(self) -> str:
        """ Returns all recipe details as a formatted string. """
        return (f"\nRecipe ID: {self.recipe_id}\n"
                f"Name: {self.name}\n"
                f"Ingredients: {self.ingredients}\n"
                f"Instructions: {self.instructions}\n")

    # --------------------------------------------------------------kayo

    def break_into_steps(self):
        """
        Split instructions (a big block of text) into a list of separate steps.
        """
        if not self.instructions:
            return []
        import re
        steps = [s.strip() for s in re.split(r'[.\n;]', self.instructions) if s.strip()]
        return steps
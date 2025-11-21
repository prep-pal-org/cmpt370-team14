"""
Baraa
Recipe Model Class
------------------
Represents a single Recipe entity in the SaucyApp system.
Stores basic attributes like name, ingredients, instructions, and image path.
Provides methods to display recipe details and handle image uploads.
"""

import os


class Recipe:
    """
    Represents a Recipe with an ID, name, ingredients, instructions, and optional image path.
    """

    def __init__(self, recipe_id: int = None, name: str = "", ingredients: str = "",
                 instructions: str = "", imagePath: str = ""):
        """
        Constructor for the Recipe class.

        :param recipe_id: Unique identifier of the recipe.
        :param name: Name of the recipe.
        :param ingredients: List or description of ingredients (as a string).
        :param instructions: Steps to prepare the recipe.
        :param imagePath: Path to an image file representing the recipe.
        """
        self.recipe_id = recipe_id
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions
        self.imagePath = imagePath

    # --------------------------------------------------------------

    def displayRecipe(self) -> None:
        """
        Prints the recipe details in a human-readable format.

        :return: None
        """
        print("\n=== Recipe Details ===")
        print(f"Recipe ID: {self.recipe_id}")
        print(f"Name: {self.name}")
        print(f"Ingredients: {self.ingredients}")
        print(f"Instructions: {self.instructions}")
        if self.imagePath:
            print(f"Image Path: {self.imagePath}")
        else:
            print("Image Path: No image uploaded yet.")

    # --------------------------------------------------------------

    def UploadPicture(self, file_path: str) -> None:
        """
        Simulates uploading a picture for the recipe.
        Checks if the given file path exists and assigns it to the imagePath attribute.

        :param file_path: The file path to the image.
        :return: None
        """
        if os.path.exists(file_path):
            self.imagePath = file_path
            print(f"Image uploaded successfully: {file_path}")
        else:
            print("Error: File not found. Image not uploaded.")

    # --------------------------------------------------------------

    def getDetails(self) -> str:
        """
        Returns all recipe details as a formatted string.

        :return: String containing recipe details.
        """
        return (f"\nRecipe ID: {self.recipe_id}\n"
                f"Name: {self.name}\n"
                f"Ingredients: {self.ingredients}\n"
                f"Instructions: {self.instructions}\n"
                f"Image: {self.imagePath if self.imagePath else 'No image uploaded'}")

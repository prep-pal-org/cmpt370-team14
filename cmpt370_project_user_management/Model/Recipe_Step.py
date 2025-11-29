"""
Kayo
Recipe_Step Class -  represents a single step of a Recipe. Each step has a step number
"""
class Recipe_Step:

    def __init__(
            self,
            step_id: int = None,
            recipe_id: int =None,
            step_number: int = 0,
            step: str = "",
            duration: int = 0
    ):
        """

        :param step_id:  the unique id for the ste
        :param recipe_id: the ID for the recipe the step belongs to
        :param step_number: the number of the step on the full recipe
        :param step: the instruction text for the step
        :param duration: the time in minutes for the step
        """
        self.step_id = step_id
        self.recipe_id = recipe_id
        self.step_number = step_number
        self.step = step
        self.duration = duration

    def displayStep(self) -> None:
        """
        Prints the step in a human-readable format.
        """
        print(f"Step {self.step_number}: {self.step} "
              f"({'No duration' if self.duration == 0 else str(self.duration) + ' min'})")

    def getDetails(self) -> str:
        """
        Returns a formatted string with step details.

        :return: String containing step number, text, and duration.
        """
        return (f"Step {self.step_number}: {self.step} "
                f"({'No duration' if self.duration == 0 else str(self.duration) + ' min'})")

"""
Kayo
Timer
A countdown timer for the system.
Has the start, pause and reset
"""
import time

class Timer:

    def __init__(self, duration: int = 0):
        """

        :param duration:  time for the countdown
        """
        self.duration = duration
        self.remaining = duration
        self.running = False    #state

    def start(self):
        """
        start the countdown timer
        :return:
        """
        if self.duration <=0:
            return
        self.running = True
        print(f"Timer started for {self.duration} seconds.\n")

        #loop till time runs out
        while self.remaining > 0 and self.running:
            mins, secs = divmod(self.remaining, 60)
            print(f"Time left: {mins:02d}:{secs:02d}", end='\r')  # overwrite line
            time.sleep(1)
            self.remaining -= 1

        #notify when finished
        if self.remaining == 0:
            print("Timer finished\n")

    def pause(self):
        """
        Pause the timer
        :return:
        """
        self.running = False
        print(f"Timer paused at {self.remaining}\n")

    def reset(self):
        """
        Reset Timer
        :return:
        """
        self.remaining =self.duration
        self.running = False
        print("Timer reset\n")
"""
Calendar Service scripts - acting as API for calendar functions to contain all SQL query text - Jordan
"""
import sqlite3
from datetime import datetime
from dateutil.rrule import rrule, rrulestr, DAILY, WEEKLY, MONTHLY
from dateutil.relativedelta import relativedelta

#CalendarError class, for passing SQL exceptions back to flask script
class CalendarError(Exception):
    pass

class CalendarService:

    def create_or_get_calendar(self, connection: sqlite3.Connection, user_id: int):
        """
        create_or_get_calendar function - creates a new calendar schedule for a user, or returns existing calendar_id
        :param user_id: user_id associated with the calendar
        :param connection: connection to sqlite3 database
        :return: calendar_id - Integer for existing / created calendar database
        """

        cursor = connection.cursor()
        #search for existing calendar linked to user_id
        cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE meal_plan_id = ?", (user_id,))
        calendar_exists = cursor.fetchone()
        if calendar_exists is not None:
           return calendar_exists[0]
        else:
           #create new calendar_schedule entry with user_id
           cursor.execute("INSERT INTO calendar_schedule (meal_plan_id) VALUES (?)", (user_id,))
           connection.commit()
           calendar_exists = cursor.lastrowid
           #return calendar_id
           return calendar_exists

    def insert_calendar_event(self, connection: sqlite3.Connection, recipe_id: int, calendar_id: int, event_name: str, event_date: str, event_time: str ):
        """
        insert_calendar_event function - inserts a new calendar event into a calendar
        :param connection: connection to sqlite3 database
        :param recipe_id: recipe_id associated with the calendar event
        :param calendar_id: calendar_id associated with the calendar event
        :param event_name: Title to be displayed on the calendar
        :param event_date: Event date for the event on the calendar
        :param event_time: Event time to be displayed on the calendar
        :return: event_id - Integer for existing / created calendar database
        """
        try:
            cursor = connection.cursor()
            #Insert into calendar_event
            cursor.execute('''
                        INSERT INTO calendar_event(event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id)
                        VALUES (?,?,?,?,?,?)    

                        ''', (
                event_name, event_date, event_time, recipe_id, calendar_id, None))
            connection.commit()
            # return event_id
            event_id = cursor.lastrowid
            return event_id
        except sqlite3.IntegrityError as e:
            raise CalendarError("Added Recipes must have a unique time and date - One Recipe per time slot.") from e

    def get_calendar_events(self, connection:sqlite3.Connection, calendar_id: int):
        '''
        get_calendar_events function - gets all calendar events and recurring event rules for a calendar_id
        :param connection: connection to sqlite3 database
        :param calendar_id: calendar_id associated with the all calendar events
        :return: all calendar events / recurring event rules
        '''
        cursor = connection.cursor()
        fc_events = []
        #get all events for this calendar_id
        cursor.execute('''
                SELECT event_id, event_name, event_date, event_time, recipe_id, recurrence_id
                FROM calendar_event
                WHERE calendar_id = ?
        ''',(calendar_id,))
        all_events = cursor.fetchall()

        # Return all events in dictionary format
        return [
            {
                "event_id": e[0],
                "event_name": e[1],
                "event_date": e[2],
                "event_time": e[3],
                "recipe_id": e[4],
                "recurrence_id": e[5]
            } for e in all_events
        ]

    def delete_calendar_event(self, connection: sqlite3.Connection, event_id: int):
        '''
        delete_calendar_event function - deletes a calendar event for an event_id
        :param connection: connection to sqlite3 database
        :param event_id: event_id associated with the calendar event being deleted
        :return: true if event was deleted, false if not
        '''
        cursor = connection.cursor()
        #get event to be deleted
        cursor.execute("SELECT * FROM calendar_event WHERE event_id = ?",(event_id,))
        deleted_event = cursor.fetchone()
        if deleted_event is not None:
            #check if this event is a parent event of a recurring series
            cursor.execute("SELECT recurrence_id FROM calendar_event WHERE event_id = ?",(event_id,))
            recurrence_id = cursor.fetchone()
            if recurrence_id is not None:
                cursor.execute("DELETE FROM calendar_event WHERE recurrence_id = ?",(recurrence_id[0],))
            #delete event
            cursor.execute("DELETE FROM calendar_event WHERE event_id = ?", (event_id,))
            connection.commit()
            #return true for confirmation of successful deletion
            return True

    def update_event(self, connection: sqlite3.Connection, event_id: int, new_date: str, new_time: str, recipe_id: int):
        """
        update_event function - updates a calendar event for an event_id
        :param connection: connection to sqlite3 database
        :param event_id: event_id associated with the calendar event being updated
        :param new_date: new date for the calendar event
        :param new_time: new time for the calendar event
        :return: none
        """
        cursor = connection.cursor()
        #Get the calendar_id to see if new time/date is taken
        cursor.execute(
            "SELECT calendar_id FROM calendar_event WHERE event_id = ?", (event_id,)
        )
        calendar_id = cursor.fetchone()[0]
        if calendar_id is None:
            raise CalendarError("Calendar ID not found - update_event function")

        #Make sure new time slot is available
        cursor.execute(
            """SELECT 1 FROM calendar_event 
                   WHERE calendar_id = ?
                   AND event_date = ?
                   AND event_time = ?
                   AND event_id <> ?            
            """, (calendar_id, new_date, new_time, event_id)
        )
        if cursor.fetchone() is not None:
            raise CalendarError("Added Recipes must have a unique time and date - One Recipe per time slot.")

        #Get the new recipe name from recipe_id
        cursor.execute("SELECT recipe_name FROM recipe WHERE recipe_id = ?", (recipe_id,))
        new_recipe_name = cursor.fetchone()

        #Update the event
        cursor.execute(
            """UPDATE calendar_event 
               SET event_date = ?, event_time = ?, recipe_id = ?, event_name = ?
               WHERE event_id = ?
            """, (new_date, new_time, recipe_id, new_recipe_name[0], event_id)
        )
        connection.commit()


    def insert_recurring_event(self, connection: sqlite3.Connection, parent_event_id: int, frequency: str, duration: str, start_date: str):
        """
        insert_recurring_event function - inserts a recurring event for a parent event_id
        :param connection: Sqlite3 database connection
        :param parent_event_id: event_id integer associated with the parent calendar event
        :param frequency: frequency of the recurring event Weekly/Monthly
        :param duration: duration of the recurring event (# of intervals)
        :param start_date: date of the parent event
        :return: recurring_event_id for new recurring event
        """
        cursor = connection.cursor()
        #Insert recurring event info into table
        cursor.execute("""
            INSERT INTO recurring_event
            (parent_event_id, frequency, duration, start_date)
            VALUES (?, ?, ?, ?)
        """, (parent_event_id, frequency, duration, start_date))
        connection.commit()
        #return recurring_event_it
        recurring_event_id = cursor.lastrowid
        #link with parent row in event table
        cursor = connection.cursor()
        cursor.execute("""
                    UPDATE calendar_event
                    SET recurrence_id = ?
                    WHERE event_id = ? 
                    """, (recurring_event_id, parent_event_id))
        connection.commit()

        return recurring_event_id

    def generate_recurring_events(self, connection: sqlite3.Connection, parent_event_id: int, recurring_event_id: int, frequency: str, duration: int, start_date: str):
        cursor = connection.cursor()

        #Get parent event details
        cursor.execute("""
            SELECT event_name, event_time, recipe_id, calendar_id
            FROM calendar_event
            WHERE event_id = ?
        
        """, (parent_event_id,))
        event_name, event_time, recipe_id, calendar_id = cursor.fetchone()
        print("Passed Parameters")
        print("parent_event_id:", parent_event_id)
        print("recurring_event_id:", recurring_event_id)
        print("frequency:", frequency)
        print("duration:", duration)
        print("start_date:", start_date)
        print("Queried parent event variables")
        print("Parent Event Name:", event_name)
        print("Parent Event Time:", event_time)
        print("Recipe ID:", recipe_id)
        print("Calendar ID:", calendar_id)

        #Format start date
        start_date_format = datetime.strptime(start_date, "%Y-%m-%d")
        print("start_date_format:", start_date_format)
        freq_mapping = {
            'Daily': DAILY,
            'Weekly': WEEKLY,
            'Monthly': MONTHLY,
        }
        if frequency not in freq_mapping:
            raise CalendarError("Unsupported frequency type.")
        adjCount = duration +1
        recurrence_rule = rrule(freq_mapping[frequency], dtstart=start_date_format, count=adjCount)
        print("recurrence_rule:")
        for row in recurrence_rule:
            print(row)

        #Generate recurring events
        for event in recurrence_rule:
            print(event)
            #Get date of recurring event occurrence in FC format
            event_date = event.date().strftime("%Y-%m-%d")
            print("FC event date:", event_date)
            # Make sure new time slot is available - unique constraint error handling
            cursor.execute(
                """SELECT 1 FROM calendar_event 
                       WHERE calendar_id = ?
                       AND event_date = ?
                       AND event_time = ?
                       AND event_id <> ?            
                """, (calendar_id, event_date, event_time, parent_event_id)
            )
            print(cursor.fetchone())
            if cursor.fetchone() is not None:
                print(event_date,"already exists")
                continue
                #raise CalendarError(f"One Recipe per time slot. Recurring event on {event_date} has been skipped due to existing recipe.")
            if event_date != start_date:
                cursor.execute("""
                    INSERT INTO calendar_event (event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (event_name, event_date, event_time, recipe_id, calendar_id, recurring_event_id))
        connection.commit()


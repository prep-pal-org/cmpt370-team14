"""
CalendarService class - acting as API for calendar with functions to contain all SQL query text - Jordan
"""
import sqlite3
from datetime import datetime
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY

#CalendarError class, for passing SQL errors back to flask script
class CalendarError(Exception):
    pass

class CalendarService:
    def create_or_get_calendar(self, connection: sqlite3.Connection, meal_plan_id: int):
        """
        create_or_get_calendar function - creates a new calendar schedule for a user, or returns existing calendar_id
        :param meal_plan_id: meal plan id associated with the calendar
        :param connection: connection to sqlite3 database
        :return: calendar_id - Integer representing existing / created calendar database
        """
        cursor = connection.cursor()
        #search for existing calendar linked to user_id
        cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE meal_plan_id = ?", (meal_plan_id,))
        calendar_id = cursor.fetchone()
        if calendar_id is not None:
           return calendar_id[0] #If meal plan already has a calendar, return the id
        else:
           #create new calendar_schedule entry with meal_plan_id
           cursor.execute("INSERT INTO calendar_schedule (meal_plan_id) VALUES (?)", (meal_plan_id,))
           connection.commit()
           calendar_id = cursor.lastrowid
           #return calendar_id
           return calendar_id

    def insert_calendar_event(self, connection: sqlite3.Connection, recipe_id: int, calendar_id: int, event_name: str, event_date: str, event_time: str ):
        """
        insert_calendar_event function - inserts a new calendar event into a single calendar
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
        get_calendar_events function - gets all calendar events for a calendar_id
        :param connection: connection to sqlite3 database
        :param calendar_id: calendar_id associated with the all calendar events
        :return: all calendar events
        '''
        cursor = connection.cursor()
        #get all events for this calendar_id
        cursor.execute('''
                SELECT event_id, event_name, event_date, event_time, recipe_id, recurrence_id
                FROM calendar_event
                WHERE calendar_id = ?
        ''',(calendar_id,))
        all_events = cursor.fetchall()
        # Return all events
        return [
            {
                "event_id": event[0],
                "event_name": event[1],
                "event_date": event[2],
                "event_time": event[3],
                "recipe_id": event[4],
                "recurrence_id": event[5]
            } for event in all_events
        ]

    def delete_calendar_event(self, connection: sqlite3.Connection, event_id: int):
        '''
        delete_calendar_event function - deletes a calendar event for an event_id
        :param connection: connection to sqlite3 database
        :param event_id: event_id associated with the calendar event being deleted
        :return: true if event was deleted, false if not
        '''
        cursor = connection.cursor()
        #check event to be deleted exists
        cursor.execute("SELECT * FROM calendar_event WHERE event_id = ?",(event_id,))
        deleted_event = cursor.fetchone()
        if deleted_event is not None:
            #delete event
            cursor.execute("DELETE FROM calendar_event WHERE event_id = ?", (event_id,))
            connection.commit()
            #return true for confirmation of successful deletion
            return True
        return False

    def update_event(self, connection: sqlite3.Connection, event_id: int, new_date: str, new_time: str, recipe_id: int):
        """
        update_event function - updates a calendar event for an event_id
        :param connection: connection to sqlite3 database
        :param event_id: event_id associated with the calendar event being updated
        :param new_date: new date for the calendar event
        :param new_time: new time for the calendar event
        :param recipe_id: new recipe id for the calendar event
        :return: none
        """
        cursor = connection.cursor()
        #Get the calendar_id
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

        #Update the event with all info
        cursor.execute(
            """UPDATE calendar_event 
               SET event_date = ?, event_time = ?, recipe_id = ?, event_name = ?
               WHERE event_id = ?
            """, (new_date, new_time, recipe_id, new_recipe_name[0], event_id)
        )
        connection.commit()

    def insert_recurring_event(self, connection: sqlite3.Connection, parent_event_id: int, frequency: str, duration: str, start_date: str):
        """
        insert_recurring_event function - inserts a recurring event for a parent event_id and recurrence rules
        :param connection: Sqlite3 database connection
        :param parent_event_id: event_id integer associated with the parent calendar event
        :param frequency: frequency of the recurring event Daily/Weekly/Monthly
        :param duration: duration of the recurring event (# of intervals beyond parent event)
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
        """
        generate_recurring_events function - used to calculate a series of dates for recurring events, and insert them into the calendar events table
        :param connection: sqlite3 database connection
        :param parent_event_id: event_id integer associated with the parent event
        :param recurring_event_id: recurring_event_id associated with the recurring event
        :param frequency: frequency of the recurring event Daily/Weekly/Monthly
        :param duration: duration of the recurring event (# of intervals beyond parent event))
        :param start_date: date of the parent event
        :return: Nothing, raises CalendarError for any unique timeslot errors
        """
        cursor = connection.cursor()
        #Get parent event details
        cursor.execute("""
            SELECT event_name, event_time, recipe_id, calendar_id
            FROM calendar_event
            WHERE event_id = ?
        
        """, (parent_event_id,))
        event_name, event_time, recipe_id, calendar_id = cursor.fetchone()
        #Format start date for recurrence rule, set frequency mapping also
        start_date_format = datetime.strptime(start_date, "%Y-%m-%d")
        freq_mapping = {
            'Daily': DAILY,
            'Weekly': WEEKLY,
            'Monthly': MONTHLY,
        }
        #Check for frequency, should be ok from input options
        if frequency not in freq_mapping:
            raise CalendarError("Unsupported frequency type.")
        #Unsure why daily recurring events include the starting day, something with starting time in recurrence rule
        #Quick fix is to simply add one more to the duration ONLY for daily recurrences, since starting date is included
        if frequency == 'Daily':
            adjCount = duration +1
        else:
            adjCount = duration
        #Calculate dates in recurrence with rrule
        recurrence_rule = rrule(freq_mapping[frequency], dtstart=start_date_format, count=adjCount)
        for row in recurrence_rule:
            print(row)
        #Declare variables for error tracking, when event can't be added due to unique timeslot
        error_count = 0
        error_list = []
        #Generate recurring events
        for event in recurrence_rule:
            #Get date of recurring event occurrence in calendar_service format
            event_date = event.date().strftime("%Y-%m-%d")
            print("event_date,start_date",event_date,start_date)
            # Make sure new time slot is available - unique constraint error handling
            cursor.execute(
                """SELECT 1 FROM calendar_event 
                       WHERE calendar_id = ?
                       AND event_date = ?
                       AND event_time = ?
                       AND event_id <> ?            
                """, (calendar_id, event_date, event_time, parent_event_id)
            )
            unique = cursor.fetchone()
            print("Unique:",unique)
            #if timeslot already occupied, add to error tracking
            if unique is not None:
                error_count += 1
                error_list.append(event_date)
            #if not start date (Daily rrule issue above), and not occupied time slot, generate event
            if event_date != start_date and unique is None:
                cursor.execute("""
                    INSERT INTO calendar_event (event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (event_name, event_date, event_time, recipe_id, calendar_id, recurring_event_id))
        connection.commit()
        #If errors encountered, report in error modal
        if error_count > 0:
            raise CalendarError(f"One Recipe per time slot. Recurring event(s) on {error_list} have been skipped due to existing recipe.")

    def delete_recurring_series(self, connection: sqlite3.Connection, recurring_event_id: int):
        '''
        delete_recurring_event function - deletes all recurring events for a recurring_event_id
        :param connection: connection to sqlite3 database
        :param recurring_event_id: recurring_event_id associated with the calendar event being deleted
        :return: true if event was deleted, false if not
        '''
        cursor = connection.cursor()
        #get event(s) to be deleted
        cursor.execute("SELECT * FROM calendar_event WHERE recurrence_id = ?",(recurring_event_id,))
        deleted_event = cursor.fetchall()
        if deleted_event is not None:
            #Iterate over all events in recurring rule
            for event in deleted_event:
                if event is not None:
                    #delete event
                    target_id = event[0]
                    cursor.execute("DELETE FROM calendar_event WHERE event_id = ?", (target_id,))
                    connection.commit()
            #delete recurring event rule
            cursor.execute("DELETE FROM recurring_event WHERE recurring_event_id = ?", (recurring_event_id,))
            return True
        return False
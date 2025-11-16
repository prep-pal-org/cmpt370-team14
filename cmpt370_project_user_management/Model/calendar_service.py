"""
Calendar Service scripts - acting as API for calendar functions to contain all SQL query text - Jordan
"""
import sqlite3

#CalendarError class, for passing SQL exceptions back to flask script
class CalendarError(Exception):
    pass

class CalendarService:

    def create_or_get_calendar(self, connection: sqlite3.Connection, user_id: int):
        """
        create_or_get_calendar function - creates a new calendar event for a user, or returns existing calendar_id
        :param user_id: user_id associated with the calendar
        :param connection: connection to sqlite3 database
        :return: calendar_id - Integer for existing / created calendar database
        """

        cursor = connection.cursor()
        #search for existing calendar linked to user_id
        cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE user_id = ?", (user_id,))
        calendar_exists = cursor.fetchone()
        if calendar_exists is not None:
           return calendar_exists[0]
        else:
           #create new calendar_schedule entry with user_id
           cursor.execute("INSERT INTO calendar_schedule (user_id) VALUES (?)", (user_id,))
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
        get_calendar_events function - gets all calendar events for a calendar_id
        :param connection: connection to sqlite3 database
        :param calendar_id: calendar_id associated with the all calendar events
        :return: dictionary array of calendar events
        '''
        cursor = connection.cursor()
        #get all events for one calendar_id
        cursor.execute('''
                SELECT event_id, event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id
                FROM calendar_event
                WHERE calendar_id = ?
        ''',(calendar_id,))
        all_events = cursor.fetchall()
        #Return all events in dictionary format
        return [
           {
               "event_id": e[0],
               "event_name": e[1],
               "event_date": e[2],
               "event_time": e[3],
               "recipe_id": e[4],
               "calendar_id": e[5],
               "recurrence_id": e[6]
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
            #delete event
            cursor.execute("DELETE FROM calendar_event WHERE event_id = ?", (event_id,))
            connection.commit()
            #return true for confirmation of successful deletion
            return cursor.rowcount > 0

    def update_event(self, connection: sqlite3.Connection, event_id: int, new_date: str, new_time: str):
        """
        update_event function - updates a calendar event for an event_id
        :param connection: connection to sqlite3 database
        :param event_id: event_id associated with the calendar event being updated
        :param new_date: new date for the calendar event
        :param new_time: new time for the calendar event
        :return: event_id - Integer for existing updated event
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

        #Update the event
        cursor.execute(
            """UPDATE calendar_event 
               SET event_date = ?, event_time = ? 
               WHERE event_id = ?
            """, (new_date, new_time, event_id)
        )
        connection.commit()
        return event_id
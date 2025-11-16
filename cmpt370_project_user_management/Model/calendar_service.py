"""
Calendar Service scripts - acting as API for calendar functions to contain all SQL query text - Jordan
"""
import sqlite3

class CalendarService:

    def create_new_calendar(self, connection: sqlite3.Connection, user_id: int):
        """
        create_new_calendar function - creates a new calendar event for a user (Jordan)
        :param user_id: user_id associated with the calendar
               connection: connection to sqlite3 database
        :return: calendar_id for existing / created calendar database
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
           cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE user_id = ?", (user_id,))
           calendar_exists = cursor.fetchone()
           #return calendar_id
           return calendar_exists[0]

    def insert_calendar_event(self, connection: sqlite3.Connection, recipe_id: int, calendar_id: int, event_name: str, event_date: str, event_time: str ):
        cursor = connection.cursor()
        #Insert into calendar_event
        cursor.execute('''
                    INSERT INTO calendar_event(event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id)
                    VALUES (?,?,?,?,?,?)    

                    ''', (
            event_name, event_date, event_time, recipe_id, calendar_id, None))
        connection.commit()
        cursor.execute("SELECT event_id FROM calendar_event WHERE event_name = ? AND event_date = ? AND event_time = ?", (event_name, event_date, event_time))
        event_id = cursor.fetchone()[0]
        #return event_id
        return event_id


    def get_calendar_events(self, connection:sqlite3.Connection, calendar_id: int):
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

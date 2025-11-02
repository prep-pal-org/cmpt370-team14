import sqlite3
from _sqlite3 import Error
from calendar_class import CalendarEvent

class CalendarService:

    def __init__(self):
        # Connect to database
        connection = None
        database = '../db/saucyapp.db'
        try:
            # Connect to SQLite database file
            self.connection = sqlite3.connect(database)
            self.cursor = self.connection.cursor()
        except Error as e:
            self.connection = None
            self.cursor = None
            print('Error while connecting to database', e)

    def create_new_calendar(self, user_id):
        """
        create_new_calendar function - creates a new calendar event for a user (Jordan)
        :param user_id: user_id associated with the calendar
        :return: calendar_id created in database
        """
        #Confirm connection to database
        if self.connection is None:
            print('No database connection')
            return None

        try:

            #search for existing calendar linked to user_id
            self.cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE user_id = ?", (user_id,))
            calendar_exists = self.cursor.fetchone()

            if calendar_exists is not None:
                return calendar_exists[0]
            else:
                #create new calendar_schedule entry with user_id
                self.cursor.execute("INSERT INTO calendar_schedule (user_id) VALUES (?)", (user_id))
                self.connection.commit()
                self.cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE user_id = ?", (user_id,))
                calendar_exists = self.cursor.fetchone()
                return calendar_exists[0]

        except Error as e:
            print('Error creating calendar', e)


    def insert_calendar_event(self, recipe_id, calendar_id, event_name, event_date, event_time ):
        if self.connection is None:
            print('No database connection')
            return None
        try:
            print(f"Inserting - calendar_id: {calendar_id},recipe_id: {recipe_id},event_name: {event_name},event_date: {event_date},event_time: {event_time}")
            self.cursor.execute('''
                        INSERT INTO calendar_event(event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id)
                        VALUES (?,?,?,?,?,?)    

                        ''', (
                event_name, event_date, event_time, recipe_id, calendar_id, None))
            self.connection.commit()
            self.cursor.execute("SELECT event_id FROM calendar_event WHERE event_name = ? AND event_date = ? AND event_time = ?", (event_name, event_date, event_time))
            event_id = self.cursor.fetchone()[0]
            print(f"Inserted - event_id: {event_id}")
            return event_id
        except Error as e:
            print('Error while connecting to database', e)

    def get_calendar_events(self, calendar_id):
        if self.connection is None:
            print('No database connection')
            return None
        try:

            self.cursor.execute('''
                    SELECT event_id, event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id
                    FROM calendar_event
                    WHERE calendar_id = ?
            ''',(calendar_id,))
            events = self.cursor.fetchall()

            return [CalendarEvent(*events) for events in events]

        except Error as e:
            print('Error while connecting to database', e)

    def delete_calendar_event(self, event_id):
        if self.connection is None:
            print('No database connection')
            return None
        try:

            #get event to be deleted
            self.cursor.execute("SELECT * FROM calendar_event WHERE event_id = ?",(event_id,))
            deleted_event = self.cursor.fetchone()
            if deleted_event is not None:
                self.cursor.execute("DELETE FROM calendar_event WHERE event_id = ?", (event_id,))
                self.connection.commit()

                return CalendarEvent(*deleted_event)

        except Error as e:
            print('Error while connecting to database', e)
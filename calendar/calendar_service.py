import sqlite3
from _sqlite3 import Error
from calendar import CalendarEvent


def database_connection():
    """
    database_connection function - used to create a connection to a SQLite database (Jordan)
    :return: reference to the database connection
    """
    # Connect to database
    connection = None
    database = '../db/saucyapp.db'
    try:
        #Connect to SQLite database file
        connection = sqlite3.connect(database)
    except Error as e:
        print('Error while connecting to database', e)


    #Check connection established
    if connection is not None:
        return connection
    else:
        print('Database connection failed')


class CalendarService:
    def create_new_calendar(self, user_id):
        """
        create_new_calendar function - creates a new calendar event for a user (Jordan)
        :param user_id: user_id associated with the calendar
        :return: calendar_id created in database
        """
        #Connect to database
        connection = database_connection()
        try:
            cursor = connection.cursor()

            #search for calendar linked to user_id
            cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE user_id = ?", (user_id,))
            calendar_exists = cursor.fetchone()

            #check if calendar already exists
            if calendar_exists is not None:
                connection.close()
                return f"User ID: {user_id} already has a calendar, {calendar_exists[0]}"
            else:
                #create new calendar_schedule entry with user_id
                cursor.execute("INSERT INTO calendar_schedule VALUES (?)", (user_id, ))
                connection.commit()
                cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE user_id = ?", (user_id,))
                calendar_exists = cursor.fetchone()
                connection.close()
                return calendar_exists[0]

        except Error as e:
            print('Error creating calendar', e)


    def insert_calendar_event(self, recipe_id, calendar_id, event_name, event_date, event_time ):
        connection = database_connection()
        try:
            cursor = connection.cursor()
            cursor.execute('''
                        INSERT INTO calendar_event(event_name, event_date, event_time, recipe_id, calendar_id)
                        VALUES (?,?,?,?,?,?)    

                        ''', (
                event_name, event_date, event_time, recipe_id, calendar_id,))
            connection.commit()
            cursor.execute("SELECT event_id FROM calendar_event WHERE event_name = ? AND event_date = ? AND event_time = ?", (event_name, event_date, event_time))
            event_id = cursor.fetchone()[0]
            connection.close()
            return event_id
        except Error as e:
            print('Error while connecting to database', e)

    def get_calendar_events(self, calendar_id):
        connection = database_connection()
        try:
            cursor = connection.cursor()
            cursor.execute('''
                    SELECT event_id, event_name, event_date, event_time, recipe_id, calendar_id
                    FROM calendar_event
                    WHERE calendar_id = ?
            ''',(calendar_id,))
            events = cursor.fetchall()
            connection.close()
            return [CalendarEvent(*events) for events in events]

        except Error as e:
            print('Error while connecting to database', e)

    def delete_calendar_event(self, event_id):
        connection = database_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM calendar_event WHERE event_id = ?", (event_id,))
            connection.commit()
            connection.close()
            return f"Event ID: {event_id} deleted"

        except Error as e:
            print('Error while connecting to database', e)
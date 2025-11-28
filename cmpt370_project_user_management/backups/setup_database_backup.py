import sqlite3
from _sqlite3 import Error

"""
database_connection function - used to create a connection to a SQLite database
Pre-Conditions:
    database - a relative filepath to a .db file
Post-Conditions:
    return reference to the database connection
"""
def database_connection(database):
    connection = None
    try:
        #Connect to SQLite database file
        connection = sqlite3.connect(database)
    except Error as e:
        print('Error while connecting to database', e)
    return connection

"""
create_tables function - used to create the tables in the database
Pre-Conditions:
    connection - an established connection to a SQLite database
Post-Conditions:
    return True if no Errors occurred
    return False if Errors encountered
"""
def create_tables(connection):
    try:
        #Create cursor for database operations
        cursor = connection.cursor()

        #calendar_event table - Jordan
        create_calendar_event = '''
        CREATE TABLE IF NOT EXISTS calendar_event (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT,
            event_date DATE,
            event_time TEXT,
            recipe_id INTEGER,
            calendar_id INTEGER,
            recurrence_id INTEGER,
            FOREIGN KEY(calendar_id) REFERENCES calendar_schedule (calendar_id),
            FOREIGN KEY(recurrence_id) REFERENCES recurring_event (recurrence_id),
            CONSTRAINT unique_event UNIQUE(event_date, event_time)                
        );
        '''

        #calendar_schedule table - Jordan
        create_calendar_schedule = '''
        CREATE TABLE IF NOT EXISTS calendar_schedule (
            calendar_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY(event_id) REFERENCES calendar_event (event_id)        
        );
        '''

        #recurring calendar event table - Jordan



        #Other tables here \/\/\/
        #TODO - add all other tables

        # recipe table - Baraa
        create_recipe_table = '''
        CREATE TABLE IF NOT EXISTS recipe (
            recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_name TEXT NOT NULL,
            ingredients TEXT,
            instructions TEXT,
            category TEXT,
            cooking_time INTEGER
        );
        '''

        #user_profile table - Randi
        create_user_profile = '''
        CREATE TABLE IF NOT EXISTS user_profile (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT not Null UNIQUE,
            username TEXT not Null UNIQUE,
            password TEXT not Null
        );
        '''

        #user_interaction table - Randi
        create_user_interaction = '''
        CREATE TABLE IF NOT EXISTS user_interaction (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            comment TEXT,
            reaction TEXT,
            FOREIGN KEY(user_id) REFERENCES user_profile (user_id)
        );
        '''




        #Create List of all table creation text
        #TODO - add tables created to this list
        table_list = [create_calendar_event, create_calendar_schedule, create_user_profile, create_user_interaction, create_recipe_table]

        #Loop through list for execute, actually creating tables
        for table in table_list:
            cursor.execute(table)
        connection.commit()

        #Create Indexes? for easier/quicker searching? not sure if needed.
        #cursor.execute('CREATE INDEX IF NOT EXISTS schedule_user_id ON calendar_schedule (user_id);')

    #If error encountered, print error, return false
    except Error as e:
        print('Error while creating tables', e)
        return False
    #successful table created, return true
    return True



def main():
    #Connect to database
    database = 'saucyapp.db'
    connection = database_connection(database)

    #Check connection established
    if connection is not None:
        #If successful, try to create tables
        if create_tables(connection):
            print('Tables created')
        else:
            print('Tables not created')
    else:
        print('Database connection failed')



if __name__ == '__main__':
    main()
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
            FOREIGN KEY(calendar_id) REFERENCES calendar_schedule (calendar_id)  
            UNIQUE(event_date, event_time)            
        );
        '''

        #calendar_schedule table - Jordan
        create_calendar_schedule = '''
        CREATE TABLE IF NOT EXISTS calendar_schedule (
            calendar_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER        
        );
        '''

        #recurring calendar event table - Jordan

        # ------------------------------------------------------------
        # recipe table - Baraa
        # Stores all recipe information including name, description, and creator
        create_recipe_table = '''
               CREATE TABLE IF NOT EXISTS recipe (
                   recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   recipe_name TEXT NOT NULL,
                   description TEXT,
                   ingredients TEXT,
                   instructions TEXT,
                   category TEXT,
                   cooking_time INTEGER,
                   user_id INTEGER,
                   FOREIGN KEY(user_id) REFERENCES user(user_id)
               );
               '''

        # recipe_image table - Baraa
        # Stores paths or binary data for images linked to a recipe
        create_recipe_image_table = '''
               CREATE TABLE IF NOT EXISTS recipe_image (
                   image_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   recipe_id INTEGER,
                   image_path TEXT,
                   upload_date DATE,
                   FOREIGN KEY(recipe_id) REFERENCES recipe(recipe_id)
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


        #connect one calender to different users -Randi
        #calendar_users = '''
        #CREATE TABLE IF NOT EXISTS calendar_users (
        #    mealID INTEGER PRIMARY KEY AUTOINCREMENT,
        #    calendar_id INTEGER NOT NULL,
        #    user_id INTEGER NOT NULL,
        #    FOREIGN KEY(calendar_id) REFERENCES calendar_schedular (calender_id)
        #    FOREIGN KEY(user_id) REFERENCES user_profile (user_id)
        #);
        #'''


        #Other tables here \/\/\/

        # grocery_list table - Soham
        create_grocery_list = '''
                CREATE TABLE IF NOT EXISTS grocery_list (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item_text TEXT NOT NULL,
                    quantity TEXT, 
                    FOREIGN KEY(user_id) REFERENCES user_profile (user_id)
                );
                '''


        #Create List of all table creation text
        #TODO - add tables created to this list
        table_list = [create_calendar_event, create_calendar_schedule, create_user_profile, create_user_interaction, create_recipe_table,
            create_recipe_image_table, create_grocery_list]


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


def update_tables(connection):
    """
    Safely adds new columns to existing tables without deleting data.
    """
    try:
        cursor = connection.cursor()

        # Try to add the 'quantity' column to 'grocery_list'
        # This will fail if the column already exists, which is fine.
        try:
            cursor.execute("ALTER TABLE grocery_list ADD COLUMN quantity TEXT")
            print("Added 'quantity' column to grocery_list.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                pass  # Column already exists, do nothing
            else:
                raise  # Re-raise other errors

        connection.commit()
        return True

    except Error as e:
        print('Error while updating tables', e)
        return False


def main():
    # Connect to database
    database = 'saucyapp.db'
    connection = database_connection(database)

    # Check connection established
    if connection is not None:
        # If successful, try to create tables
        if create_tables(connection):
            print('Tables created')
            # Also update tables
            if update_tables(connection):
                print("Tables updated")
            else:
                print("Tables not updated")
        else:
            print('Tables not created')
    else:
        print('Database connection failed')

if __name__ == '__main__':
    main()

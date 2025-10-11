import sqlite3

#setup common website database
def setup_database():
    #Connect to SQLite database file
    connection = sqlite3.connect('saucyapp.db')

    #Create cursor for database operations
    cursor = connection.cursor()

    #Create Calendar Event Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendar_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT,
            event_date DATE,
        );    
    ''')


    #Create Other Table

    #Create Other Table

    connection.commit()
    connection.close()

if __name__ == '__main__':
    #setup_database()
    print('Setting up database...')
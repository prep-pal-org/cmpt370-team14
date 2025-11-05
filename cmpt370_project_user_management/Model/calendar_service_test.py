import sqlite3
from pathlib import Path

"""
Calendar Service test scripts - Jordan
Due to ongoing database linking issues with testing calendar_service.py, rather than calling the methods directly, 
testing has been completed by reproducing the SQL calls on a temporary database, to ensure there are no errors in logic/syntax.
"""
def open_test_db() -> sqlite3.Connection:
    """
    Helper method to open a sqlite3 database - Jordan
    :return: reference to sqlite3 database connection
    """
    db_path = Path("temp.db")
    if db_path.exists():
        db_path.unlink()

    connection = sqlite3.connect(db_path)

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS calendar_schedule (
            calendar_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS calendar_event (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT,
            event_date DATE,
            event_time TEXT,
            recipe_id INTEGER,
            calendar_id INTEGER,
            recurrence_id INTEGER,
            FOREIGN KEY(calendar_id) REFERENCES calendar_schedule (calendar_id)
        );
        """
    )
    connection.commit()
    return connection


def test_create_calendar(connection: sqlite3.Connection):
    """
    Test Method to test creating a new Calendar Schedule - Jordan
    :param connection: connection to sqlite3 database
    :return: None - print statements show Pass/Fail output
    """
    cursor = connection.cursor()
    user_id = 4

    #Try to get an existing calendar – should be None first
    cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE user_id = ?", (user_id,))
    assert cursor.fetchone() is None, "Calendar should not exist yet"

    #Insert a new calendar
    cursor.execute("INSERT INTO calendar_schedule (user_id) VALUES (?)", (user_id,))
    connection.commit()

    #Retrieve the newly created calendar_id
    cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE user_id = ?", (user_id,))
    created_calendar = cursor.fetchone()
    assert created_calendar is not None, "Calendar was not inserted"
    calendar_id = created_calendar[0]
    assert isinstance(calendar_id, int), "calendar_id should be int"
    #print(calendar_id)

    #Lookup must return the same id
    cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE user_id = ?", (user_id,))
    same_id = cursor.fetchone()[0]
    assert calendar_id == same_id, "Duplicate calendar created"

    print("test_create_calendar passed tests")
    cursor.close()


def test_insert_event(connection: sqlite3.Connection):
    """
    Test Method to insert a new event into calendar - Jordan
    :param connection: connection to sqlite3 database
    :return: none - Print statements show Pass/Fail output
    """
    cursor = connection.cursor()
    user_id = 12

    #Create a calendar and verify it is inserted
    cursor.execute("INSERT INTO calendar_schedule (user_id) VALUES (?)", (user_id,))
    connection.commit()
    cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE user_id = ?", (user_id,))
    calendar_id = cursor.fetchone()[0]

    #Insert an event
    cursor.execute(
        """
        INSERT INTO calendar_event
        (event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id)
        VALUES (?,?,?,?,?,NULL)
        """,
        ("Pizza", "2025-12-31", "Dinner", 57, calendar_id)
    )
    connection.commit()

    #Verify it can be queried from the event_id
    cursor.execute(
        "SELECT event_id FROM calendar_event "
        "WHERE event_name = ? AND event_date = ? AND event_time = ?",
        ("Pizza", "2025-12-31", "Dinner")
    )
    event_id = cursor.fetchone()[0]
    assert isinstance(event_id, int), "event_id should be int"

    print("test_insert_event passed")
    cursor.close()


def test_get_events(connection: sqlite3.Connection):
    """
    Test Method to get events from calendar - Jordan
    :param connection: connection to sqlite3 database
    :return: None - Pass/Fail output is printed to console
    """
    #Setup Calendar
    cursor = connection.cursor()
    user_id = 42
    cursor.execute("INSERT INTO calendar_schedule (user_id) VALUES (?)", (user_id,))
    connection.commit()
    cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE user_id = ?", (user_id,))
    calendar_id = cursor.fetchone()[0]

    #Insert multiple events
    cursor.execute(
        """
        INSERT INTO calendar_event
        (event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id)
        VALUES (?,?,?,?,?,NULL)
        """,
        ("Breakfast Burrito", "2025-11-10", "Breakfast", 14, calendar_id)
    )
    cursor.execute(
        """
        INSERT INTO calendar_event
        (event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id)
        VALUES (?,?,?,?,?,NULL)
        """,
        ("Grilled Chicken", "2025-11-11", "Dinner", 42, calendar_id)
    )
    cursor.execute(
        """
        INSERT INTO calendar_event
        (event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id)
        VALUES (?,?,?,?,?,NULL)
        """,
        ("Burritos", "2025-11-15", "Dinner", 9, calendar_id)
    )
    connection.commit()

    #Retrieve all events for this calendar
    cursor.execute(
        """
        SELECT event_id, event_name, event_date, event_time,
               recipe_id, calendar_id, recurrence_id
        FROM calendar_event
        WHERE calendar_id = ?
        """,
        (calendar_id,)
    )
    rows = cursor.fetchall()
    assert len(rows) == 3, f"Expected 3 events, got {len(rows)}"

    for row in rows:
        event_id, name, date, time, recipe_id, cal_id, rec_id = row
        assert cal_id == calendar_id, "Returned event belongs to wrong calendar"

    print("test_get_events passed")
    cursor.close()


def test_delete_event(connection: sqlite3.Connection):
    """
    Test Method to delete event from calendar - Jordan
    :param connection: connection to sqlite3 database
    :return: none - Print statements show Pass/Fail output
    """
    #setup calendar and verify
    cursor = connection.cursor()
    user_id = 33
    cursor.execute("INSERT INTO calendar_schedule (user_id) VALUES (?)", (user_id,))
    connection.commit()
    cursor.execute("SELECT calendar_id FROM calendar_schedule WHERE user_id = ?", (user_id,))
    calendar_id = cursor.fetchone()[0]

    #Insert an event to delete
    cursor.execute(
        """
        INSERT INTO calendar_event
        (event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id)
        VALUES (?,?,?,?,?,NULL)
        """,
        ("Chilli", "2025-12-05", "Lunch", 125, calendar_id)
    )
    connection.commit()

    #Get the event_id
    cursor.execute(
        "SELECT event_id FROM calendar_event "
        "WHERE event_name = ? AND event_date = ? AND event_time = ?",
        ("Chilli", "2025-12-05", "Lunch")
    )
    event_id = cursor.fetchone()[0]

    #Delete it
    cursor.execute("DELETE FROM calendar_event WHERE event_id = ?", (event_id,))
    connection.commit()

    #Confirm removal
    cursor.execute("SELECT * FROM calendar_event WHERE event_id = ?", (event_id,))
    assert cursor.fetchone() is None, "Event was not deleted"

    print("test_delete_event passed")
    cursor.close()


def main():
    conn = open_test_db()
    try:
        test_create_calendar(conn)
        test_insert_event(conn)
        test_get_events(conn)
        test_delete_event(conn)
    finally:
        conn.close()
        db_path = Path("temp.db")
        if db_path.exists():
            db_path.unlink()


if __name__ == "__main__":
    main()
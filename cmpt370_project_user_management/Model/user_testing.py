import sqlite3
import User as U
from setup_database import database_connection, create_tables
############## TESTING ##############


test1 = U.UserProfile()

#Confirm set name works
expected = "TestJane1"
test1.setUserName("TestJane1")
result = test1.getUserName()
if result != expected:
    print("Setting username failed, expected: ", expected, "got ", result)
else:
    print("Username is set. expected: ", expected, "result: ", result)

#Confirm set e-mail works
expected = "jane123@email.com"
test1.setEmail("jane123@email.com")
result = test1.getEmail()
if result != expected:
    print("Setting email failed, expected: ", expected, "got ", result)
else:
    print("Email is set. expected: ", expected, "result: ", result)

#Confirm set password works
expected = "JanePassword$"
test1.setPassword("JanePassword$")
result = test1.getPassword()
if result != expected:
    print("Setting password failed, expected: ", expected, "got ", result)
else:
    print("Password is set. expected: ", expected, "result: ", result)

#Confirm set userID works
expected = 1
test1.setUserId(1)
result = test1.getUserId()
if result != expected:
    print("Setting userID failed, expected: ", expected, "got ", result)
else:
    print("Username is set. expected: ", expected, "result: ", result)

#Add everything to the database
conn = database_connection("saucyapp.db")
create_tables(conn)
#conn.close()

test1.add_to_database(conn)

#connection = sqlite3.connect("saucyapp.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM user_profile")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()



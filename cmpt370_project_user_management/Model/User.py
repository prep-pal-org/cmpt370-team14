import sqlite3


class UserProfile(object):
    def __init__(self):
        """
        Purpose:
            Create a user profile, user.
        Returns nothing
        """
        self.__username = ''
        self.__email = ''
        self.__password = ''
        self.__user_id = 0

    def setUserName(self, name):
        """
        Purpose:
            Set the user's name.
        :param name: user's name
        returns nothing
        """
        self.__username = name

    def getUserName(self):
        """
        Purpose:
            Get the user's name.
        :return: name
        """
        return self.__username

    def setEmail(self, email):
        """
        Purpose:
            Set the user's e-mail.
        :param email:
        return nothing.
        """
        self.__email = email

    def getEmail(self):
        """
        Purpose:
            Get the user's e-mail.
        :return: eMail
        """
        return self.__email

    def setPassword(self, password):
        """
        Purpose:
         Set the user's password.
        :param password:
        return nothing
        """
        self.__password = password

    def getPassword(self):
        """
        Purpose:
            Get the user's password.
        :return: password
        """
        return self.__password

    def setUserId(self, user_id):
        """
        Purpose:
            Set the user's ID.
        :param user_id:
        return nothing
        """
        self.__user_id = user_id

    def getUserId(self):
        """
        Purpose:
            Get the user's ID.
        :return: user's ID
        """
        return self.__user_id

    def add_to_database(self,connection):
        """
        Purpose:
            add new user profile to database.
        :param userProfile:
        :param connection: connection to the database
        returns nothing
        """
        cursor = None
        try:

            cursor = connection.cursor()
            cursor.execute(''' INSERT INTO user_profile (user_id, username, email, password) VALUES (?, ?, ?,?)''',
                           (self.getUserId(), self.getUserName(), self.getEmail(), self.getPassword()))
            connection.commit()
            print("User added to table")
        except sqlite3.Error as error:
            print("Did not save user:", error)
        finally:
            if cursor is not None:
                cursor.close()


# ChatGPT's usage Oct 21. 2025 - used ChatGPT to explain how to connect the user class
# to the database. Combined what ChatGPT suggesting with W3 schools website to look
# up the SQLite syntax to understand what I was doing.




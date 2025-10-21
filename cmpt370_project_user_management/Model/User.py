from _sqlite3 import Error


class UserProfile(object):
    def __init__(self, username, email, password, user_id):
        """
        Purpose:
            Create a user profile, user.
        :param username: user's name
        :param email: user's e-mail
        :param password: user's password
        :param user_id: user's ID, numerical number assigned automatically
        Returns nothing
        """
        self.__username = username
        self.__email = email
        self.__password = password
        self.__user_id = user_id

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

    def add_to_database(self, connection):
        """
        Purpose:
            add new user profile to database.
        :param connection: connection to the database
        returns nothing
        """
        try:
            cursor = connection.cursor()
            cursor.execute(''' INSERT INTO user_profile (username,email,password,user_id) VALUES (?, ?, ?,?)''',
                           (self.getUserName(), self.getEmail(), self.getPassword(), self.getUserId()))
            connection.commit()
            print("User added to table")
        except Error as error:
            print("Did not save user:", error)

# ChatGPT's usage Oct 21. 2025 - used ChatGPT to explain how to connect the user class
# to the database. Combined what ChatGPT suggesting with W3 schools website to look
# up the SQLite syntax to understand what I was doing.

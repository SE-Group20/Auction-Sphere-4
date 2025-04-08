import sqlite3

import flask_login
from flask_login.utils import LocalProxy


class User(flask_login.UserMixin):
    def __init__(self, id:int|None, email:str, password:str, first_name:str, last_name:str, contact_number:str):
        """
        Initialize a User object.
        Not automatically persisted!
        :param id: User's ID - None if not yet persisted
        :param email: User's email address
        :param password: User's password
        :param first_name: User's first name
        :param last_name: User's last name
        :param contact_number: User's contact number
        """
        self.id:int|None = id
        self.email:str = email
        self.password:str = password
        self.first_name:str = first_name
        self.last_name:str = last_name
        self.contact_number:str = contact_number

    def try_signup(self, conn: sqlite3.Connection) -> tuple[bool, str]:
        """
        Attempt to sign up the user.
        :param conn: SQLite connection object
        :return: Tuple of (success, message)
        """

        # Check if the email already exists in the database
        cursor = conn.cursor()
        cursor = cursor.execute("SELECT * FROM users WHERE email = ?", (self.id,))
        existing_user:tuple[str]|None = cursor.fetchone()

        if existing_user:
            return False, "Email already exists."

        # check if contact number already exists in the database
        if self.contact_number:
            cursor = cursor.execute("SELECT * FROM users WHERE contact_number = ?", (self.contact_number,))
            existing_contact:tuple[str]|None = cursor.fetchone()
            if existing_contact:
                return False, "Contact number already exists."

        # Insert the new user into the database
        cursor = cursor.execute(
            "INSERT INTO users (email, password, first_name, last_name, contact_number) VALUES (?, ?, ?, ?, ?)",
            (self.email, self.password, self.first_name, self.last_name, self.contact_number),
        )
        conn.commit()
        return True, "User signed up successfully."

    @staticmethod
    def user_by_email(conn: sqlite3.Connection, email: str):
        """
        Get a user by email.
        :param conn: SQLite connection object
        :param email: User's email address
        :return: User object or None if not found
        """
        cursor = conn.cursor()
        result = cursor.execute("SELECT user_id, email, password, first_name, last_name, contact_number FROM users WHERE email = ?", (email,))
        user_data:tuple[str,...]|None = result.fetchone()
        if user_data:
            if len(user_data) != 6:
                raise ValueError("User data does not contain all required fields.")
            return User(
                id=int(user_data[0]),
                email=user_data[1],
                password=user_data[2],
                first_name=user_data[3],
                last_name=user_data[4],
                contact_number=user_data[5]
            )
        return None

    @staticmethod
    def user_by_id(conn: sqlite3.Connection, user_id: int|str):
        """
        Get a user by ID.
        :param conn: SQLite connection object
        :param user_id: User's ID
        :return: User object or None if not found
        """
        cursor = conn.cursor()
        result = cursor.execute("SELECT user_id, email, password, first_name, last_name, contact_number FROM users WHERE user_id = ?", (user_id,))
        user_data:tuple[str,...]|None = result.fetchone()
        if user_data:
            return User(
                id=int(user_data[0]),
                email=user_data[1],
                password=user_data[2],
                first_name=user_data[3],
                last_name=user_data[4],
                contact_number=user_data[5]
            )
        return None

    @staticmethod
    def try_login(conn: sqlite3.Connection, email: str, password: str) -> 'None|User':
        """
        Attempt to log in the user.
        :param conn: SQLite connection object
        :param email: User's email address
        :param password: User's password
        :return: True if login is successful, False otherwise
        """
        cursor = conn.cursor()
        # TODO(kurt): Use hashed password
        result = cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user:tuple[str,...]|None = result.fetchone()
        if user:
            return User(
                id = int(user[0]),
                email=user[1],
                password=user[2],
                first_name=user[3],
                last_name=user[4],
                contact_number=user[5]
            )
        return None



MaybeUser = LocalProxy[User|None|flask_login.AnonymousUserMixin]
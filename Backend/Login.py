import hashlib
import mysql.connector
from Database import get_connection
from Dashboard import show_dashboard


def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def register_user(name, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    query = """
        INSERT INTO users
        (full_name, email, password_hash)
        VALUES (%s, %s, %s)
    """

    try:
        cursor.execute(
            query,
            (name, email, password_hash)
        )

        conn.commit()

        print("Registration successful!")

    except mysql.connector.Error as e:

        print("Registration failed:", e)

    finally:

        cursor.close()
        conn.close()


def login_user(email, password):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    password_hash = hash_password(password)

    query = """
        SELECT user_id, full_name, email
        FROM users
        WHERE email = %s AND password_hash = %s
    """

    cursor.execute(
        query,
        (email, password_hash)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:

        print("Login successful!")
        return user

    else:

        print("Invalid email or password")
        return None


if __name__ == "__main__":

    print("1. Register")
    print("2. Login")

    choice = input("Enter choice: ")

    if choice == "1":

        name = input("Enter full name: ")
        email = input("Enter email: ")
        password = input("Enter password: ")

        register_user(name, email, password)

    elif choice == "2":

        email = input("Enter email: ")
        password = input("Enter password: ")

        user = login_user(email, password)

        if user:
            print("Welcome,", user["full_name"])
            show_dashboard(user)

    else:

        print("Invalid choice")
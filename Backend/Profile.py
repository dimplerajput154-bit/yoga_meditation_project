import re
import mysql.connector
from Database import get_connection


def validate_user_id(user_id):
    if user_id is None:
        return False, "User ID is required"

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return False, "Invalid user ID"

    if user_id <= 0:
        return False, "User ID must be greater than 0"

    return True, ""


def validate_name(full_name):
    if not full_name or not full_name.strip():
        return False, "Full name is required"

    full_name = full_name.strip()

    if len(full_name) < 2:
        return False, "Name must contain at least 2 characters"

    if len(full_name) > 100:
        return False, "Name is too long"

    if not re.fullmatch(r"[A-Za-z ]+", full_name):
        return False, "Name can contain only letters and spaces"

    return True, ""


def validate_email(email):
    if not email or not email.strip():
        return False, "Email is required"

    email = email.strip()

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.fullmatch(pattern, email):
        return False, "Enter a valid email address"

    return True, ""


def get_profile(user_id):

    # Validate user ID
    valid, message = validate_user_id(user_id)

    if not valid:
        return {
            "success": False,
            "message": message,
            "profile": None
        }

    conn = None
    cursor = None

    try:
        conn = get_connection()

        if conn is None:
            return {
                "success": False,
                "message": "Database connection failed",
                "profile": None
            }

        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT user_id,
                   full_name,
                   email,
                   role,
                   profile_image,
                   is_active
            FROM users
            WHERE user_id = %s
            LIMIT 1
        """

        cursor.execute(query, (int(user_id),))

        profile = cursor.fetchone()

        if profile is None:
            return {
                "success": False,
                "message": "Profile not found",
                "profile": None
            }

        return {
            "success": True,
            "message": "Profile fetched successfully",
            "profile": profile
        }

    except mysql.connector.Error:
        return {
            "success": False,
            "message": "Failed to fetch profile",
            "profile": None
        }

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


def update_profile(
    user_id,
    full_name,
    email,
    profile_image=None
):

    # Validate user ID
    valid, message = validate_user_id(user_id)

    if not valid:
        return {
            "success": False,
            "message": message
        }

    # Validate name
    valid, message = validate_name(full_name)

    if not valid:
        return {
            "success": False,
            "message": message
        }

    # Validate email
    valid, message = validate_email(email)

    if not valid:
        return {
            "success": False,
            "message": message
        }

    full_name = full_name.strip()
    email = email.strip()

    conn = None
    cursor = None

    try:
        conn = get_connection()

        if conn is None:
            return {
                "success": False,
                "message": "Database connection failed"
            }

        cursor = conn.cursor()

        # Check whether user exists
        user_query = """
            SELECT user_id
            FROM users
            WHERE user_id = %s
            LIMIT 1
        """

        cursor.execute(user_query, (int(user_id),))

        if cursor.fetchone() is None:
            return {
                "success": False,
                "message": "Profile not found"
            }

        # Check whether email belongs to another user
        email_query = """
            SELECT user_id
            FROM users
            WHERE email = %s
              AND user_id != %s
            LIMIT 1
        """

        cursor.execute(
            email_query,
            (email, int(user_id))
        )

        if cursor.fetchone():
            return {
                "success": False,
                "message": "Email is already registered"
            }

        # Update profile
        update_query = """
            UPDATE users
            SET full_name = %s,
                email = %s,
                profile_image = %s
            WHERE user_id = %s
        """

        cursor.execute(
            update_query,
            (
                full_name,
                email,
                profile_image,
                int(user_id)
            )
        )

        conn.commit()

        return {
            "success": True,
            "message": "Profile updated successfully"
        }

    except mysql.connector.Error:
        if conn:
            conn.rollback()

        return {
            "success": False,
            "message": "Profile update failed"
        }

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()
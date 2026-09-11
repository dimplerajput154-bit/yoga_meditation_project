from Database_Module import connection
from flask import Blueprint, request, jsonify, session
import mysql.connector
from mysql.connector import Error


# Create Health Profile Blueprint
health_bp = Blueprint("health", __name__)


# =========================================================
# VALIDATION FUNCTION
# =========================================================
"""
    Function Name: validate_health_profile
    Description: Validates health profile fields such as age, gender, height,
                 weight, and activity level.
    Input: data (dictionary containing health profile information)
    Output: errors (dictionary containing validation errors)
"""
def validate_health_profile(data):

    errors = {}

    # -------------------------
    # Age validation
    # -------------------------
    age = data.get("age")

    if age is not None and age != "":
        try:
            age = int(age)

            if age <= 0 or age > 120:
                errors["age"] = "Age must be between 1 and 120."

        except (ValueError, TypeError):
            errors["age"] = "Age must be a valid number."


    # -------------------------
    # Gender validation
    # -------------------------
    gender = data.get("gender")

    allowed_gender = [
        "male",
        "female",
        "other"
    ]

    if gender not in [None, ""]:

        if gender not in allowed_gender:
            errors["gender"] = "Invalid gender."


    # -------------------------
    # Height validation
    # -------------------------
    height = data.get("height_cm")

    if height is not None and height != "":
        try:
            height = float(height)

            if height <= 0:
                errors["height_cm"] = "Height must be greater than 0."

        except (ValueError, TypeError):
            errors["height_cm"] = "Height must be a valid number."


    # -------------------------
    # Weight validation
    # -------------------------
    weight = data.get("weight_kg")

    if weight is not None and weight != "":
        try:
            weight = float(weight)

            if weight <= 0:
                errors["weight_kg"] = "Weight must be greater than 0."

        except (ValueError, TypeError):
            errors["weight_kg"] = "Weight must be a valid number."


    # -------------------------
    # Activity level validation
    # -------------------------
    activity_level = data.get("activity_level")

    allowed_activity = [
        "sedentary",
        "light",
        "moderate",
        "active"
    ]

    if activity_level not in [None, ""]:

        if activity_level not in allowed_activity:
            errors["activity_level"] = "Invalid activity level."


    # Return validation errors
    return errors


# =========================================================
# GET HEALTH PROFILE
# =========================================================
"""
    Function Name: get_health_profile
    Description: Fetches the logged-in user's health profile from the database.
    Input: Logged-in user's session user_id
    Output: JSON response containing the health profile or an error message
"""
@health_bp.route("/health-profile", methods=["GET"])
def get_health_profile():

    db = None
    cursor = None

    # Check whether user is logged in
    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    user_id = session["user_id"]

    try:

        db = connection()
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT
                profile_id,
                user_id,
                age,
                gender,
                height_cm,
                weight_kg,
                activity_level,
                diet_preference,
                allergies,
                existing_conditions,
                updated_at
            FROM health_profiles
            WHERE user_id = %s
        """

        cursor.execute(query, (user_id,))

        profile = cursor.fetchone()

        # Profile does not exist
        if profile is None:

            return jsonify({
                "success": True,
                "profile_exists": False,
                "profile": None
            }), 200

        # Profile found
        return jsonify({
            "success": True,
            "profile_exists": True,
            "profile": profile
        }), 200

    except Error as e:

        return jsonify({
            "success": False,
            "message": "Database error occurred."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()

# =========================================================
# CREATE HEALTH PROFILE
# =========================================================
"""
    Function Name: create_health_profile
    Description: Validates and creates a new health profile for the logged-in user.
    Input: JSON health profile data from the request
    Output: JSON response with success message and profile_id
"""
@health_bp.route("/health-profile", methods=["POST"])
def create_health_profile():

    db = None
    cursor = None

    # Check login
    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    # Get logged-in user's ID
    user_id = session["user_id"]

    # Get JSON data
    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "success": False,
            "message": "No health profile data received."
        }), 400

    # Validate data
    errors = validate_health_profile(data)

    if errors:

        return jsonify({
            "success": False,
            "errors": errors
        }), 400

    try:

        db = connection()
        cursor = db.cursor(dictionary=True)

        # -------------------------------------------------
        # Check whether profile already exists
        # -------------------------------------------------

        check_query = """
            SELECT profile_id
            FROM health_profiles
            WHERE user_id = %s
        """

        cursor.execute(check_query, (user_id,))

        existing_profile = cursor.fetchone()

        if existing_profile:

            return jsonify({
                "success": False,
                "message": "Health profile already exists. Use PUT to update it."
            }), 409

        # -------------------------------------------------
        # Insert new profile
        # -------------------------------------------------

        insert_query = """
            INSERT INTO health_profiles
            (
                user_id,
                age,
                gender,
                height_cm,
                weight_kg,
                activity_level,
                diet_preference,
                allergies,
                existing_conditions
            )
            VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """

        values = (
            user_id,
            data.get("age") or None,
            data.get("gender") or None,
            data.get("height_cm") or None,
            data.get("weight_kg") or None,
            data.get("activity_level") or "sedentary",
            data.get("diet_preference") or None,
            data.get("allergies") or None,
            data.get("existing_conditions") or None
        )

        cursor.execute(insert_query, values)

        db.commit()

        return jsonify({
            "success": True,
            "message": "Health profile created successfully.",
            "profile_id": cursor.lastrowid
        }), 201

    except Error as e:

        if db:
            db.rollback()

        return jsonify({
            "success": False,
            "message": "Unable to create health profile."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()

# =========================================================
# UPDATE HEALTH PROFILE
# =========================================================
"""
    Function Name: update_health_profile
    Description: Validates and updates the existing health profile of the logged-in user.
    Input: JSON health profile data from the request
    Output: JSON response with update status and message
"""
@health_bp.route("/health-profile", methods=["PUT"])
def update_health_profile():

    db = None
    cursor = None

    # Check login
    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    user_id = session["user_id"]

    # Get JSON data
    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "success": False,
            "message": "No health profile data received."
        }), 400

    # Validate data
    errors = validate_health_profile(data)

    if errors:

        return jsonify({
            "success": False,
            "errors": errors
        }), 400

    try:

        db = connection()
        cursor = db.cursor(dictionary=True)

        # -------------------------------------------------
        # Check profile exists
        # -------------------------------------------------

        check_query = """
            SELECT profile_id
            FROM health_profiles
            WHERE user_id = %s
        """

        cursor.execute(check_query, (user_id,))

        existing_profile = cursor.fetchone()

        if not existing_profile:

            return jsonify({
                "success": False,
                "message": "Health profile not found."
            }), 404

        # -------------------------------------------------
        # Update profile
        # -------------------------------------------------

        update_query = """
            UPDATE health_profiles
            SET
                age = %s,
                gender = %s,
                height_cm = %s,
                weight_kg = %s,
                activity_level = %s,
                diet_preference = %s,
                allergies = %s,
                existing_conditions = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """

        values = (
            data.get("age") or None,
            data.get("gender") or None,
            data.get("height_cm") or None,
            data.get("weight_kg") or None,
            data.get("activity_level") or "sedentary",
            data.get("diet_preference") or None,
            data.get("allergies") or None,
            data.get("existing_conditions") or None,
            user_id
        )

        cursor.execute(update_query, values)

        db.commit()

        return jsonify({
            "success": True,
            "message": "Health profile updated successfully."
        }), 200

    except Error as e:

        if db:
            db.rollback()

        return jsonify({
            "success": False,
            "message": "Unable to update health profile."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()
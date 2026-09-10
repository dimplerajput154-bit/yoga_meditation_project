
from flask import Blueprint, request, jsonify, session
from Database_Module import connection
from datetime import datetime


# =========================================================
# SLEEP TRACKER BLUEPRINT
# =========================================================

sleep_bp = Blueprint("sleep_tracker", __name__)


# =========================================================
# Function-1: calculate_duration()
#
# Description:
#     Calculates sleep duration in minutes using
#     sleep time and wake-up time.
#
# Input:
#     sleep_time - Sleep time in HH:MM format
#     wake_time  - Wake-up time in HH:MM format
#
# Output:
#     Sleep duration in minutes
# =========================================================

def calculate_duration(sleep_time, wake_time):

    sleep = datetime.strptime(sleep_time, "%H:%M")
    wake = datetime.strptime(wake_time, "%H:%M")

    # If wake-up time is next day
    if wake <= sleep:
        wake = wake.replace(day=2)

    duration = wake - sleep

    return int(duration.total_seconds() / 60)


# =========================================================
# Function-2: validate_sleep_data()
#
# Description:
#     Validates sleep tracker input data.
#
# Input:
#     data - JSON data received from request
#
# Output:
#     Error message or None
# =========================================================

def validate_sleep_data(data):

    required_fields = [
        "record_date",
        "sleep_time",
        "wake_time"
    ]

    for field in required_fields:

        if field not in data or not str(data[field]).strip():

            return f"{field} is required."

    # Validate date
    try:

        datetime.strptime(
            data["record_date"],
            "%Y-%m-%d"
        )

    except ValueError:

        return "record_date must be in YYYY-MM-DD format."

    # Validate time
    try:

        datetime.strptime(
            data["sleep_time"],
            "%H:%M"
        )

        datetime.strptime(
            data["wake_time"],
            "%H:%M"
        )

    except ValueError:

        return "sleep_time and wake_time must be in HH:MM format."

    # Validate sleep quality
    if data.get("quality"):

        allowed_quality = [
            "poor",
            "average",
            "good",
            "excellent"
        ]

        if data["quality"] not in allowed_quality:

            return "Invalid sleep quality."

    return None


# =========================================================
# Function-3: get_sleep_records()
#
# Description:
#     Gets all sleep records of the logged-in user.
#
# Input:
#     Logged-in user session
#
# Output:
#     Sleep records in JSON format
# =========================================================

@sleep_bp.route("/sleep-tracker", methods=["GET"])
def get_sleep_records():

    user_id = session.get("user_id")

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User is not logged in."
        }), 401

    conn = connection()

    if conn is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    try:

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                record_id,
                record_date,
                sleep_time,
                wake_time,
                duration_minutes,
                quality,
                notes,
                report_file,
                created_at
            FROM sleep_records
            WHERE user_id = %s
            ORDER BY record_date DESC
        """, (user_id,))

        records = cursor.fetchall()

        return jsonify({
            "success": True,
            "records": records
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        conn.close()


# =========================================================
# Function-4: add_sleep_record()
#
# Description:
#     Adds a new sleep record for the logged-in user.
#
# Input:
#     JSON:
#       record_date
#       sleep_time
#       wake_time
#       quality
#       notes
#       report_file
#
# Output:
#     Success or error response
# =========================================================

@sleep_bp.route("/sleep-tracker", methods=["POST"])
def add_sleep_record():

    user_id = session.get("user_id")

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User is not logged in."
        }), 401

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400

    error = validate_sleep_data(data)

    if error:

        return jsonify({
            "success": False,
            "message": error
        }), 400

    try:

        duration = calculate_duration(
            data["sleep_time"],
            data["wake_time"]
        )

    except Exception:

        return jsonify({
            "success": False,
            "message": "Unable to calculate sleep duration."
        }), 400

    conn = connection()

    if conn is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    try:

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sleep_records
            (
                user_id,
                record_date,
                sleep_time,
                wake_time,
                duration_minutes,
                quality,
                notes,
                report_file
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            data["record_date"],
            data["sleep_time"],
            data["wake_time"],
            duration,
            data.get("quality"),
            data.get("notes"),
            data.get("report_file")
        ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Sleep record added successfully.",
            "record_id": cursor.lastrowid,
            "duration_minutes": duration
        }), 201

    except Exception as e:

        conn.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        conn.close()


# =========================================================
# Function-5: update_sleep_record()
#
# Description:
#     Updates an existing sleep record.
#
# Input:
#     record_id in URL
#     JSON sleep data
#
# Output:
#     Success or error response
# =========================================================

@sleep_bp.route("/sleep-tracker/<int:record_id>", methods=["PUT"])
def update_sleep_record(record_id):

    user_id = session.get("user_id")

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User is not logged in."
        }), 401

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400

    error = validate_sleep_data(data)

    if error:

        return jsonify({
            "success": False,
            "message": error
        }), 400

    try:

        duration = calculate_duration(
            data["sleep_time"],
            data["wake_time"]
        )

    except Exception:

        return jsonify({
            "success": False,
            "message": "Unable to calculate sleep duration."
        }), 400

    conn = connection()

    if conn is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    try:

        cursor = conn.cursor()

        cursor.execute("""
            UPDATE sleep_records
            SET
                record_date = %s,
                sleep_time = %s,
                wake_time = %s,
                duration_minutes = %s,
                quality = %s,
                notes = %s,
                report_file = %s
            WHERE record_id = %s
            AND user_id = %s
        """, (
            data["record_date"],
            data["sleep_time"],
            data["wake_time"],
            duration,
            data.get("quality"),
            data.get("notes"),
            data.get("report_file"),
            record_id,
            user_id
        ))

        if cursor.rowcount == 0:

            return jsonify({
                "success": False,
                "message": "Sleep record not found."
            }), 404

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Sleep record updated successfully.",
            "duration_minutes": duration
        }), 200

    except Exception as e:

        conn.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        conn.close()


# =========================================================
# Function-6: delete_sleep_record()
#
# Description:
#     Deletes a sleep record belonging to the logged-in user.
#
# Input:
#     record_id in URL
#
# Output:
#     Success or error response
# =========================================================

@sleep_bp.route("/sleep-tracker/<int:record_id>", methods=["DELETE"])
def delete_sleep_record(record_id):

    user_id = session.get("user_id")

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User is not logged in."
        }), 401

    conn = connection()

    if conn is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    try:

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM sleep_records
            WHERE record_id = %s
            AND user_id = %s
        """, (
            record_id,
            user_id
        ))

        if cursor.rowcount == 0:

            return jsonify({
                "success": False,
                "message": "Sleep record not found."
            }), 404

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Sleep record deleted successfully."
        }), 200

    except Exception as e:

        conn.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        conn.close()


# =========================================================
# Function-7: get_sleep_summary()
#
# Description:
#     Calculates average sleep duration and provides
#     daily/weekly/monthly summary data.
#
# Input:
#     Logged-in user session
#
# Output:
#     Sleep summary in JSON format
# =========================================================

@sleep_bp.route("/sleep-tracker/summary", methods=["GET"])
def get_sleep_summary():

    user_id = session.get("user_id")

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User is not logged in."
        }), 401

    conn = connection()

    if conn is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    try:

        cursor = conn.cursor(dictionary=True)

        # Average sleep duration
        cursor.execute("""
            SELECT
                ROUND(AVG(duration_minutes), 2)
                AS average_duration_minutes
            FROM sleep_records
            WHERE user_id = %s
        """, (user_id,))

        average = cursor.fetchone()

        # Daily records
        cursor.execute("""
            SELECT
                record_date,
                duration_minutes,
                quality
            FROM sleep_records
            WHERE user_id = %s
            ORDER BY record_date ASC
        """, (user_id,))

        daily_records = cursor.fetchall()

        return jsonify({
            "success": True,
            "average_duration_minutes":
                average["average_duration_minutes"],
            "records": daily_records
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        conn.close()
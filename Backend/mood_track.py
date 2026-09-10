
from flask import Blueprint, request, jsonify, session
from Database_Module import connection
from datetime import datetime, date, timedelta


# =========================================================
# MOOD TRACKER BLUEPRINT
# =========================================================

mood_bp = Blueprint("mood", __name__)


# =========================================================
# CONSTANTS
# =========================================================

ALLOWED_MOODS = [
    "happy",
    "good",
    "neutral",
    "stressed",
    "sad"
]


# =========================================================
# Function: get_logged_in_user()
# Description:
#     Gets the logged-in user's ID from Flask session.
# Input:
#     None
# Output:
#     user_id or None
# =========================================================

def get_logged_in_user():

    return session.get("user_id")


# =========================================================
# Function: validate_mood_data()
# Description:
#     Validates mood tracker input data.
# Input:
#     data - JSON request data
# Output:
#     Error message or None
# =========================================================

def validate_mood_data(data):

    if not data:
        return "Request data is required."

    mood = data.get("mood")

    if not mood:
        return "Mood is required."

    mood = str(mood).strip().lower()

    if mood not in ALLOWED_MOODS:
        return (
            "Invalid mood. Allowed moods are: "
            "happy, good, neutral, stressed, sad."
        )

    stress_level = data.get("stress_level")

    if stress_level is not None and stress_level != "":

        try:
            stress_level = int(stress_level)

        except (ValueError, TypeError):
            return "Stress level must be a number between 1 and 10."

        if stress_level < 1 or stress_level > 10:
            return "Stress level must be between 1 and 10."

    record_date = data.get("record_date")

    if record_date:

        try:
            datetime.strptime(
                str(record_date),
                "%Y-%m-%d"
            )

        except ValueError:
            return "record_date must be in YYYY-MM-DD format."

    return None


# =========================================================
# Function: convert_record()
# Description:
#     Converts database row into JSON-friendly dictionary.
# Input:
#     row - Database result row.
# Output:
#     Dictionary containing mood record.
# =========================================================

def convert_record(row):

    return {
        "record_id": row[0],
        "user_id": row[1],
        "record_date": (
            row[2].strftime("%Y-%m-%d")
            if row[2]
            else None
        ),
        "mood": row[3],
        "stress_level": row[4],
        "notes": row[5],
        "created_at": (
            row[6].strftime("%Y-%m-%d %H:%M:%S")
            if row[6]
            else None
        )
    }


# =========================================================
# GET /mood
#
# Description:
#     Gets all mood records of logged-in user.
#
# Input:
#     Optional:
#         start_date
#         end_date
#
# Output:
#     List of mood records.
# =========================================================

@mood_bp.route("/mood", methods=["GET"])
def get_mood_records():

    user_id = get_logged_in_user()

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User is not logged in."
        }), 401


    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")


    conn = None
    cursor = None

    try:

        conn = connection()
        cursor = conn.cursor()


        query = """
            SELECT
                record_id,
                user_id,
                record_date,
                mood,
                stress_level,
                notes,
                created_at
            FROM mood_records
            WHERE user_id = %s
        """

        params = [user_id]


        # -------------------------------------------------
        # Optional start date filter
        # -------------------------------------------------

        if start_date:

            query += """
                AND record_date >= %s
            """

            params.append(start_date)


        # -------------------------------------------------
        # Optional end date filter
        # -------------------------------------------------

        if end_date:

            query += """
                AND record_date <= %s
            """

            params.append(end_date)


        query += """
            ORDER BY record_date DESC, created_at DESC
        """


        cursor.execute(
            query,
            tuple(params)
        )


        rows = cursor.fetchall()


        records = [
            convert_record(row)
            for row in rows
        ]


        return jsonify({
            "success": True,
            "count": len(records),
            "records": records
        }), 200


    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Failed to fetch mood records.",
            "error": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# GET /mood/<record_id>
#
# Description:
#     Gets one mood record.
#
# Input:
#     record_id - Mood record ID.
#
# Output:
#     Single mood record.
# =========================================================

@mood_bp.route("/mood/<int:record_id>", methods=["GET"])
def get_single_mood_record(record_id):

    user_id = get_logged_in_user()

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User is not logged in."
        }), 401


    conn = None
    cursor = None

    try:

        conn = connection()
        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT
                record_id,
                user_id,
                record_date,
                mood,
                stress_level,
                notes,
                created_at
            FROM mood_records
            WHERE record_id = %s
            AND user_id = %s
            """,
            (record_id, user_id)
        )


        row = cursor.fetchone()


        if not row:

            return jsonify({
                "success": False,
                "message": "Mood record not found."
            }), 404


        return jsonify({
            "success": True,
            "record": convert_record(row)
        }), 200


    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Failed to fetch mood record.",
            "error": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# POST /mood
#
# Description:
#     Creates a new mood record.
#
# Input:
#     JSON:
#         record_date
#         mood
#         stress_level
#         notes
#
# Output:
#     Created mood record.
# =========================================================

@mood_bp.route("/mood", methods=["POST"])
def create_mood_record():

    user_id = get_logged_in_user()

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User is not logged in."
        }), 401


    data = request.get_json(
        silent=True
    )


    validation_error = validate_mood_data(data)

    if validation_error:

        return jsonify({
            "success": False,
            "message": validation_error
        }), 400


    mood = str(
        data.get("mood")
    ).strip().lower()


    stress_level = data.get(
        "stress_level"
    )


    if stress_level == "":
        stress_level = None

    elif stress_level is not None:
        stress_level = int(stress_level)


    notes = data.get("notes")

    if notes is not None:

        notes = str(notes).strip()

        if notes == "":
            notes = None


    record_date = data.get(
        "record_date"
    )


    if not record_date:

        record_date = date.today().strftime(
            "%Y-%m-%d"
        )


    conn = None
    cursor = None

    try:

        conn = connection()
        cursor = conn.cursor()


        # -------------------------------------------------
        # Insert mood record
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO mood_records
            (
                user_id,
                record_date,
                mood,
                stress_level,
                notes
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                user_id,
                record_date,
                mood,
                stress_level,
                notes
            )
        )


        conn.commit()


        record_id = cursor.lastrowid


        return jsonify({
            "success": True,
            "message": "Mood record added successfully.",
            "record_id": record_id
        }), 201


    except Exception as e:

        if conn:
            conn.rollback()


        return jsonify({
            "success": False,
            "message": "Failed to add mood record.",
            "error": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PUT /mood/<record_id>
#
# Description:
#     Updates an existing mood record.
#
# Input:
#     record_id - Mood record ID.
#     JSON fields to update.
#
# Output:
#     Success message.
# =========================================================

@mood_bp.route("/mood/<int:record_id>", methods=["PUT"])
def update_mood_record(record_id):

    user_id = get_logged_in_user()

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User is not logged in."
        }), 401


    data = request.get_json(
        silent=True
    )


    validation_error = validate_mood_data(data)

    if validation_error:

        return jsonify({
            "success": False,
            "message": validation_error
        }), 400


    mood = str(
        data.get("mood")
    ).strip().lower()


    stress_level = data.get(
        "stress_level"
    )


    if stress_level == "":
        stress_level = None

    elif stress_level is not None:
        stress_level = int(stress_level)


    notes = data.get("notes")

    if notes is not None:

        notes = str(notes).strip()

        if notes == "":
            notes = None


    record_date = data.get(
        "record_date"
    )


    if not record_date:

        record_date = date.today().strftime(
            "%Y-%m-%d"
        )


    conn = None
    cursor = None

    try:

        conn = connection()
        cursor = conn.cursor()


        # -------------------------------------------------
        # Check record belongs to current user
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT record_id
            FROM mood_records
            WHERE record_id = %s
            AND user_id = %s
            """,
            (record_id, user_id)
        )


        existing_record = cursor.fetchone()


        if not existing_record:

            return jsonify({
                "success": False,
                "message": "Mood record not found."
            }), 404


        # -------------------------------------------------
        # Update record
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE mood_records
            SET
                record_date = %s,
                mood = %s,
                stress_level = %s,
                notes = %s
            WHERE record_id = %s
            AND user_id = %s
            """,
            (
                record_date,
                mood,
                stress_level,
                notes,
                record_id,
                user_id
            )
        )


        conn.commit()


        return jsonify({
            "success": True,
            "message": "Mood record updated successfully."
        }), 200


    except Exception as e:

        if conn:
            conn.rollback()


        return jsonify({
            "success": False,
            "message": "Failed to update mood record.",
            "error": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# DELETE /mood/<record_id>
#
# Description:
#     Deletes an existing mood record.
#
# Input:
#     record_id - Mood record ID.
#
# Output:
#     Success message.
# =========================================================

@mood_bp.route("/mood/<int:record_id>", methods=["DELETE"])
def delete_mood_record(record_id):

    user_id = get_logged_in_user()

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User is not logged in."
        }), 401


    conn = None
    cursor = None

    try:

        conn = connection()
        cursor = conn.cursor()


        # -------------------------------------------------
        # Delete only user's own record
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM mood_records
            WHERE record_id = %s
            AND user_id = %s
            """,
            (
                record_id,
                user_id
            )
        )


        conn.commit()


        if cursor.rowcount == 0:

            return jsonify({
                "success": False,
                "message": "Mood record not found."
            }), 404


        return jsonify({
            "success": True,
            "message": "Mood record deleted successfully."
        }), 200


    except Exception as e:

        if conn:
            conn.rollback()


        return jsonify({
            "success": False,
            "message": "Failed to delete mood record.",
            "error": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# GET /mood/summary
#
# Description:
#     Provides mood statistics and trend data.
#
# Input:
#     Optional period:
#         week
#         month
#
# Output:
#     Summary and mood trend information.
# =========================================================

@mood_bp.route("/mood/summary", methods=["GET"])
def get_mood_summary():

    user_id = get_logged_in_user()

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User is not logged in."
        }), 401


    period = request.args.get(
        "period",
        "week"
    ).lower()


    if period not in ["week", "month"]:

        return jsonify({
            "success": False,
            "message": "Period must be week or month."
        }), 400


    today = date.today()


    if period == "week":

        start_date = today - timedelta(days=6)

    else:

        start_date = today - timedelta(days=29)


    conn = None
    cursor = None

    try:

        conn = connection()
        cursor = conn.cursor()


        # -------------------------------------------------
        # Get records
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                record_date,
                mood,
                stress_level
            FROM mood_records
            WHERE user_id = %s
            AND record_date BETWEEN %s AND %s
            ORDER BY record_date ASC
            """,
            (
                user_id,
                start_date,
                today
            )
        )


        rows = cursor.fetchall()


        # -------------------------------------------------
        # Mood counts
        # -------------------------------------------------

        mood_counts = {

            "happy": 0,
            "good": 0,
            "neutral": 0,
            "stressed": 0,
            "sad": 0

        }


        total_stress = 0
        stress_count = 0


        trend = []


        for row in rows:

            record_date = row[0]
            mood = row[1]
            stress_level = row[2]


            if mood in mood_counts:

                mood_counts[mood] += 1


            if stress_level is not None:

                total_stress += int(
                    stress_level
                )

                stress_count += 1


            trend.append({

                "date":
                    record_date.strftime(
                        "%Y-%m-%d"
                    ),

                "mood":
                    mood,

                "stress_level":
                    stress_level

            })


        # -------------------------------------------------
        # Average stress
        # -------------------------------------------------

        if stress_count > 0:

            average_stress = round(
                total_stress / stress_count,
                2
            )

        else:

            average_stress = None


        # -------------------------------------------------
        # Most frequent mood
        # -------------------------------------------------

        if rows:

            dominant_mood = max(
                mood_counts,
                key=mood_counts.get
            )

            if mood_counts[dominant_mood] == 0:

                dominant_mood = None

        else:

            dominant_mood = None


        return jsonify({

            "success": True,

            "period": period,

            "start_date":
                start_date.strftime(
                    "%Y-%m-%d"
                ),

            "end_date":
                today.strftime(
                    "%Y-%m-%d"
                ),

            "total_records":
                len(rows),

            "dominant_mood":
                dominant_mood,

            "average_stress":
                average_stress,

            "mood_counts":
                mood_counts,

            "trend":
                trend

        }), 200


    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Failed to generate mood summary.",
            "error": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
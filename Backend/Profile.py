from flask import Flask, request, jsonify
from flask_cors import CORS

from Database import get_connection


# =========================================================
# Flask Application
# =========================================================

app = Flask(_name_)

CORS(app)


# =========================================================
# Home / Test
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "success",
        "message": "AI Wellness Profile Server is running.",
        "get_profile": "/api/profile/<user_id>",
        "update_profile": "/api/profile/<user_id>"
    })


# =========================================================
# Get Profile
# =========================================================

@app.route(
    "/api/profile/<int:user_id>",
    methods=["GET"]
)
def get_profile(user_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()

        if conn is None:

            return jsonify({
                "status": "error",
                "message": "Database connection failed."
            }), 500


        cursor = conn.cursor(dictionary=True)


        query = """
            SELECT
                user_id,
                full_name,
                email,
                role,
                profile_image,
                is_active
            FROM users
            WHERE user_id = %s
        """


        cursor.execute(
            query,
            (user_id,)
        )


        user = cursor.fetchone()


        if user is None:

            return jsonify({
                "status": "error",
                "message": "User not found."
            }), 404


        return jsonify({

            "status": "success",

            "message": "Profile loaded successfully.",

            "profile": {

                "user_id": user["user_id"],

                "full_name": user["full_name"],

                "email": user["email"],

                "role": user["role"],

                "profile_image": user["profile_image"],

                "is_active": user["is_active"]

            }

        })


    except Exception as e:

        print("Profile Error:", e)

        return jsonify({

            "status": "error",

            "message": "Unable to load profile.",

            "error": str(e)

        }), 500


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# =========================================================
# Update Profile
# =========================================================

@app.route(
    "/api/profile/<int:user_id>",
    methods=["PUT"]
)
def update_profile(user_id):

    conn = None
    cursor = None

    try:

        data = request.get_json()


        if not data:

            return jsonify({
                "status": "error",
                "message": "JSON data is required."
            }), 400


        full_name = data.get("full_name")
        email = data.get("email")
        profile_image = data.get("profile_image")


        # Validate Name

        if not full_name:

            return jsonify({
                "status": "error",
                "message": "Full name is required."
            }), 400


        # Validate Email

        if not email:

            return jsonify({
                "status": "error",
                "message": "Email is required."
            }), 400


        conn = get_connection()


        if conn is None:

            return jsonify({
                "status": "error",
                "message": "Database connection failed."
            }), 500


        cursor = conn.cursor(dictionary=True)


        # Check User

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )


        user = cursor.fetchone()


        if user is None:

            return jsonify({
                "status": "error",
                "message": "User not found."
            }), 404


        # Check Duplicate Email

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = %s
            AND user_id != %s
            """,
            (email, user_id)
        )


        existing_user = cursor.fetchone()


        if existing_user:

            return jsonify({
                "status": "error",
                "message": "Email already exists."
            }), 400


        # Update Profile

        query = """
            UPDATE users
            SET
                full_name = %s,
                email = %s,
                profile_image = %s
            WHERE user_id = %s
        """


        cursor.execute(
            query,
            (
                full_name,
                email,
                profile_image,
                user_id
            )
        )


        conn.commit()


        return jsonify({

            "status": "success",

            "message": "Profile updated successfully.",

            "profile": {

                "user_id": user_id,

                "full_name": full_name,

                "email": email,

                "profile_image": profile_image

            }

        })


    except Exception as e:

        if conn:

            conn.rollback()


        print("Profile Update Error:", e)


        return jsonify({

            "status": "error",

            "message": "Unable to update profile.",

            "error": str(e)

        }), 500


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# =========================================================
# Run Application
# =========================================================

if __name__ == "__main__":

    print("=" * 60)

    print("             AI WELLNESS PROFILE")

    print("=" * 60)

    print("Database: ai_wellness_db")

    print("Profile Server:")
    print("http://127.0.0.1:5002")

    print()

    print("Test:")
    print("http://127.0.0.1:5002/")

    print()

    print("Get Profile:")
    print("http://127.0.0.1:5002/api/profile/1")

    print()

    print("Update Profile:")
    print("PUT http://127.0.0.1:5002/api/profile/1")

    print("=" * 60)


    app.run(
        debug=True,
        port=5002
    )
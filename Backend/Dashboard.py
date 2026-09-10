from flask import Flask, jsonify, request
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

        "message":
            "AI Wellness Dashboard Server is running.",

        "dashboard_api":
            "/api/dashboard/<user_id>",

        "tasks_api":
            "/api/tasks/<user_id>",

        "toggle_task_api":
            "/api/toggle-task/<task_id>"

    })


# =========================================================
# Get Dashboard Data
# =========================================================

@app.route(
    "/api/dashboard/<int:user_id>",
    methods=["GET"]
)
def get_dashboard(user_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()

        if conn is None:

            return jsonify({

                "status": "error",

                "message":
                    "Database connection failed."

            }), 500


        cursor = conn.cursor(dictionary=True)


        # =====================================================
        # Get User
        # =====================================================

        cursor.execute(
            """
            SELECT
                user_id,
                full_name,
                email
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


        # =====================================================
        # Get Tasks
        # =====================================================

        cursor.execute(
            """
            SELECT
                task_id,
                task_name,
                is_completed
            FROM tasks
            WHERE user_id = %s
            """,
            (user_id,)
        )


        tasks = cursor.fetchall()


        tasks_list = []


        for task in tasks:

            tasks_list.append({

                "id":
                    task["task_id"],

                "task_name":
                    task["task_name"],

                "is_completed":
                    bool(task["is_completed"])

            })


        # =====================================================
        # Get Wellness Metrics
        # =====================================================

        cursor.execute(
            """
            SELECT
                sleep_hours,
                sleep_status,
                mood_score,
                mood_percentage,
                yoga_minutes,
                yoga_goal,
                water_glasses,
                water_goal,
                steps_count,
                steps_goal
            FROM wellness_metric
            WHERE user_id = %s
            """,
            (user_id,)
        )


        metric = cursor.fetchone()


        metric_data = None


        if metric:

            metric_data = {

                "sleep_hours":
                    metric["sleep_hours"],

                "sleep_status":
                    metric["sleep_status"],

                "mood_score":
                    metric["mood_score"],

                "mood_percentage":
                    metric["mood_percentage"],

                "yoga_minutes":
                    metric["yoga_minutes"],

                "yoga_goal":
                    metric["yoga_goal"],

                "water_glasses":
                    metric["water_glasses"],

                "water_goal":
                    metric["water_goal"],

                "steps_count":
                    metric["steps_count"],

                "steps_goal":
                    metric["steps_goal"]

            }


        # =====================================================
        # Dashboard Response
        # =====================================================

        return jsonify({

            "status": "success",

            "message":
                "Dashboard data loaded successfully.",

            "user": {

                "id":
                    user["user_id"],

                "name":
                    user["full_name"],

                "email":
                    user["email"]

            },

            "metric":
                metric_data,

            "tasks":
                tasks_list

        })


    except Exception as e:

        print(
            "Dashboard Error:",
            e
        )


        return jsonify({

            "status": "error",

            "message":
                "Unable to load dashboard.",

            "error":
                str(e)

        }), 500


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# =========================================================
# Toggle Task
# =========================================================

@app.route(
    "/api/toggle-task/<int:task_id>",
    methods=["POST"]
)
def toggle_task(task_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()

        if conn is None:

            return jsonify({

                "status": "error",

                "message":
                    "Database connection failed."

            }), 500


        cursor = conn.cursor(dictionary=True)


        # =====================================================
        # Find Task
        # =====================================================

        cursor.execute(
            """
            SELECT
                task_id,
                is_completed
            FROM tasks
            WHERE task_id = %s
            """,
            (task_id,)
        )


        task = cursor.fetchone()


        if task is None:

            return jsonify({

                "status": "error",

                "message":
                    "Task not found."

            }), 404


        # =====================================================
        # Toggle Task
        # =====================================================

        new_status = not bool(
            task["is_completed"]
        )


        cursor.execute(
            """
            UPDATE tasks
            SET is_completed = %s
            WHERE task_id = %s
            """,
            (
                new_status,
                task_id
            )
        )


        conn.commit()


        return jsonify({

            "status": "success",

            "message":
                "Task updated successfully.",

            "task_id":
                task_id,

            "completed":
                new_status

        })


    except Exception as e:

        if conn:

            conn.rollback()


        print(
            "Task Error:",
            e
        )


        return jsonify({

            "status": "error",

            "message":
                "Unable to update task.",

            "error":
                str(e)

        }), 500


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# =========================================================
# Get Tasks Only
# =========================================================

@app.route(
    "/api/tasks/<int:user_id>",
    methods=["GET"]
)
def get_tasks(user_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()

        if conn is None:

            return jsonify({

                "status": "error",

                "message":
                    "Database connection failed."

            }), 500


        cursor = conn.cursor(dictionary=True)


        cursor.execute(
            """
            SELECT
                task_id,
                task_name,
                is_completed
            FROM tasks
            WHERE user_id = %s
            """,
            (user_id,)
        )


        tasks = cursor.fetchall()


        tasks_list = []


        for task in tasks:

            tasks_list.append({

                "id":
                    task["task_id"],

                "task_name":
                    task["task_name"],

                "is_completed":
                    bool(task["is_completed"])

            })


        return jsonify({

            "status": "success",

            "tasks":
                tasks_list

        })


    except Exception as e:

        print(
            "Tasks Error:",
            e
        )


        return jsonify({

            "status": "error",

            "message":
                "Unable to load tasks.",

            "error":
                str(e)

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

    print(
        "             AI WELLNESS DASHBOARD"
    )

    print("=" * 60)

    print(
        "Database: ai_wellness_db"
    )

    print()

    print(
        "Dashboard Server:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()

    print(
        "Dashboard API:"
    )

    print(
        "http://127.0.0.1:5000/api/dashboard/1"
    )

    print()

    print(
        "Tasks API:"
    )

    print(
        "http://127.0.0.1:5000/api/tasks/1"
    )

    print()

    print(
        "Toggle Task:"
    )

    print(
        "POST /api/toggle-task/<task_id>"
    )

    print("=" * 60)


    app.run(

        debug=True,

        port=5000

    )
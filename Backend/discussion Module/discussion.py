import sys
from datetime import date, datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Database_Module import connection


app = Flask(__name__, template_folder=".", static_folder=".", static_url_path="/static")


def json_response(status, message=None, **payload):
    response = {"status": status}
    if message:
        response["message"] = message
    response.update(payload)
    return jsonify(response)


def format_date(value):
    if isinstance(value, datetime):
        return value.strftime("%d %b %Y, %I:%M %p")
    if isinstance(value, date):
        return value.strftime("%d %b %Y")
    return str(value) if value else ""


def current_user_id(data=None):
    data = data or {}
    raw_user_id = request.args.get("user_id") or data.get("user_id") or request.form.get("user_id")
    try:
        return max(1, int(raw_user_id))
    except (TypeError, ValueError):
        return None


def discussion_payload(row, active_user_id):
    return {
        "discussion_id": row["discussion_id"],
        "org_id": row["org_id"],
        "organization_name": row["organization_name"],
        "organization_category": row.get("organization_category") or "Wellness",
        "user_id": row["user_id"],
        "author": row["author"],
        "title": row["title"],
        "content": row["content"],
        "created_at": format_date(row["created_at"]),
        "is_owner": bool(active_user_id and int(row["user_id"]) == int(active_user_id)),
    }


def fetch_discussion(cursor, discussion_id):
    cursor.execute(
        """
        SELECT
            d.discussion_id,
            d.org_id,
            d.user_id,
            d.title,
            d.content,
            d.created_at,
            u.full_name AS author,
            o.name AS organization_name,
            o.category AS organization_category
        FROM discussions d
        JOIN users u ON u.user_id = d.user_id
        JOIN organizations o ON o.org_id = d.org_id
        WHERE d.discussion_id = %s
        """,
        (discussion_id,)
    )
    return cursor.fetchone()


@app.route("/", methods=["GET"])
def discussion_page():
    return render_template("discussion.html")


@app.route("/api/organizations", methods=["GET"])
def list_organizations():
    conn = None
    cursor = None
    try:
        conn = connection()
        if conn is None:
            return json_response("error", "Database connection failed."), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT org_id, name, category, privacy
            FROM organizations
            ORDER BY name ASC
            """
        )
        return json_response("success", organizations=cursor.fetchall())
    except Exception as error:
        return json_response("error", "Unable to load organizations.", error=str(error)), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/api/discussions", methods=["GET"])
def list_discussions():
    conn = None
    cursor = None
    try:
        conn = connection()
        if conn is None:
            return json_response("error", "Database connection failed."), 500

        active_user_id = current_user_id()
        search = request.args.get("search", "").strip()
        org_id = request.args.get("org_id", "").strip()
        where_parts = []
        params = []

        if search:
            pattern = f"%{search}%"
            where_parts.append("(d.title LIKE %s OR d.content LIKE %s OR u.full_name LIKE %s OR o.name LIKE %s)")
            params.extend([pattern, pattern, pattern, pattern])

        if org_id:
            try:
                where_parts.append("d.org_id = %s")
                params.append(int(org_id))
            except ValueError:
                return json_response("error", "Invalid organization selected."), 400

        where_clause = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"""
            SELECT
                d.discussion_id,
                d.org_id,
                d.user_id,
                d.title,
                d.content,
                d.created_at,
                u.full_name AS author,
                o.name AS organization_name,
                o.category AS organization_category
            FROM discussions d
            JOIN users u ON u.user_id = d.user_id
            JOIN organizations o ON o.org_id = d.org_id
            {where_clause}
            ORDER BY d.created_at DESC
            """,
            tuple(params)
        )
        discussions = [discussion_payload(row, active_user_id) for row in cursor.fetchall()]
        return json_response("success", discussions=discussions)
    except Exception as error:
        return json_response("error", "Unable to load discussions.", error=str(error)), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/api/discussions/<int:discussion_id>", methods=["GET"])
def get_discussion(discussion_id):
    conn = None
    cursor = None
    try:
        conn = connection()
        if conn is None:
            return json_response("error", "Database connection failed."), 500

        active_user_id = current_user_id()
        cursor = conn.cursor(dictionary=True)
        discussion = fetch_discussion(cursor, discussion_id)
        if not discussion:
            return json_response("error", "Discussion not found."), 404

        return json_response("success", discussion=discussion_payload(discussion, active_user_id))
    except Exception as error:
        return json_response("error", "Unable to load discussion.", error=str(error)), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/api/discussions", methods=["POST"])
def create_discussion():
    data = request.get_json(silent=True) or {}
    user_id = current_user_id(data)
    title = str(data.get("title", "")).strip()
    content = str(data.get("content", "")).strip()

    try:
        org_id = int(data.get("org_id", 0))
    except (TypeError, ValueError):
        return json_response("error", "Please choose a valid organization."), 400

    if not user_id:
        return json_response("error", "Please login before creating a discussion."), 401
    if len(title) < 5:
        return json_response("error", "Discussion title must be at least 5 characters."), 400
    if len(title) > 150:
        return json_response("error", "Discussion title must be 150 characters or less."), 400
    if len(content) < 10:
        return json_response("error", "Discussion content must be at least 10 characters."), 400

    conn = None
    cursor = None
    try:
        conn = connection()
        if conn is None:
            return json_response("error", "Database connection failed."), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            return json_response("error", "User not found. Please login first."), 404

        cursor.execute("SELECT org_id FROM organizations WHERE org_id = %s", (org_id,))
        if not cursor.fetchone():
            return json_response("error", "Organization not found."), 404

        cursor.execute(
            """
            INSERT INTO discussions (org_id, user_id, title, content)
            VALUES (%s, %s, %s, %s)
            """,
            (org_id, user_id, title, content)
        )
        discussion_id = cursor.lastrowid
        conn.commit()

        discussion = fetch_discussion(cursor, discussion_id)
        return json_response(
            "success",
            "Discussion created successfully.",
            discussion=discussion_payload(discussion, user_id)
        ), 201
    except Exception as error:
        if conn:
            conn.rollback()
        return json_response("error", "Unable to create discussion.", error=str(error)), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/api/discussions/<int:discussion_id>", methods=["PUT"])
def update_discussion(discussion_id):
    data = request.get_json(silent=True) or {}
    user_id = current_user_id(data)
    title = str(data.get("title", "")).strip()
    content = str(data.get("content", "")).strip()

    if not user_id:
        return json_response("error", "Please login before editing this discussion."), 401
    if len(title) < 5:
        return json_response("error", "Discussion title must be at least 5 characters."), 400
    if len(title) > 150:
        return json_response("error", "Discussion title must be 150 characters or less."), 400
    if len(content) < 10:
        return json_response("error", "Discussion content must be at least 10 characters."), 400

    conn = None
    cursor = None
    try:
        conn = connection()
        if conn is None:
            return json_response("error", "Database connection failed."), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM discussions WHERE discussion_id = %s", (discussion_id,))
        discussion = cursor.fetchone()
        if not discussion:
            return json_response("error", "Discussion not found."), 404
        if int(discussion["user_id"]) != int(user_id):
            return json_response("error", "Only the author can edit this discussion."), 403

        cursor.execute(
            """
            UPDATE discussions
            SET title = %s, content = %s
            WHERE discussion_id = %s
            """,
            (title, content, discussion_id)
        )
        conn.commit()

        updated = fetch_discussion(cursor, discussion_id)
        return json_response(
            "success",
            "Discussion updated successfully.",
            discussion=discussion_payload(updated, user_id)
        )
    except Exception as error:
        if conn:
            conn.rollback()
        return json_response("error", "Unable to update discussion.", error=str(error)), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/api/discussions/<int:discussion_id>", methods=["DELETE"])
def delete_discussion(discussion_id):
    user_id = current_user_id()
    if not user_id:
        return json_response("error", "Please login before deleting this discussion."), 401

    conn = None
    cursor = None
    try:
        conn = connection()
        if conn is None:
            return json_response("error", "Database connection failed."), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM discussions WHERE discussion_id = %s", (discussion_id,))
        discussion = cursor.fetchone()
        if not discussion:
            return json_response("error", "Discussion not found."), 404
        if int(discussion["user_id"]) != int(user_id):
            return json_response("error", "Only the author can delete this discussion."), 403

        cursor.execute("DELETE FROM discussions WHERE discussion_id = %s", (discussion_id,))
        conn.commit()
        return json_response("success", "Discussion deleted successfully.")
    except Exception as error:
        if conn:
            conn.rollback()
        return json_response("error", "Unable to delete discussion.", error=str(error)), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("          AI WELLNESS DISCUSSIONS")
    print("=" * 60)
    print("Server:")
    print("http://127.0.0.1:5003")
    print()
    print("Discussions API:")
    print("GET/POST http://127.0.0.1:5003/api/discussions")
    print("=" * 60)
    app.run(debug=True, port=5003, use_reloader=False)

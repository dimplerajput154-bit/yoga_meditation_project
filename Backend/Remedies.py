
# ============================================================
# Remedies Module
# Description:
# Handles Health Remedies data
# Uses Database_Module.py for MySQL connection
# ============================================================

from flask import Blueprint, jsonify, request
from Database_Module import connection

# Blueprint
remedies_bp = Blueprint("remedies", __name__)


# ============================================================
# Function Name : get_all_remedies()
# Description   : Fetch all remedies
# Input         : None
# Output        : JSON response with remedies list
# ============================================================
@remedies_bp.route("/remedies", methods=["GET"])
def get_all_remedies():

    conn = connection()

    if conn is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            remedy_id,
            topic,
            symptoms,
            self_care_info,
            precautions,
            when_to_consult_doctor,
            created_at
        FROM health_remedies
        ORDER BY remedy_id
    """

    cursor.execute(query)

    remedies = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "count": len(remedies),
        "data": remedies
    })


# ============================================================
# Function Name : get_remedy_by_id()
# Description   : Fetch single remedy by ID
# Input         : remedy_id
# Output        : Single remedy JSON
# ============================================================
@remedies_bp.route("/remedies/<int:remedy_id>", methods=["GET"])
def get_remedy_by_id(remedy_id):

    conn = connection()

    if conn is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            remedy_id,
            topic,
            symptoms,
            self_care_info,
            precautions,
            when_to_consult_doctor,
            created_at
        FROM health_remedies
        WHERE remedy_id = %s
    """

    cursor.execute(query, (remedy_id,))

    remedy = cursor.fetchone()

    cursor.close()
    conn.close()

    if remedy:

        return jsonify({
            "success": True,
            "data": remedy
        })

    return jsonify({
        "success": False,
        "message": "Remedy not found"
    }), 404


# ============================================================
# Function Name : search_remedies()
# Description   : Search remedies by topic
# Input         : topic keyword
# Output        : Matching remedies
# ============================================================
@remedies_bp.route("/search-remedies", methods=["GET"])
def search_remedies():

    topic = request.args.get("topic")

    conn = connection()

    if conn is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            remedy_id,
            topic,
            symptoms,
            self_care_info,
            precautions,
            when_to_consult_doctor
        FROM health_remedies
        WHERE topic LIKE %s
    """

    cursor.execute(query, ("%" + topic + "%",))

    remedies = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "count": len(remedies),
        "data": remedies
    })
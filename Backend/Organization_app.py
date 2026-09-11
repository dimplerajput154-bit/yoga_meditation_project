from flask import Flask, render_template, jsonify, request

from Organization.Organization import (
    view_organizations,
    search_organizations,
    view_organization_details
)

from organization.membership import (
    join_organization,
    leave_organization,
    view_members
)


app = Flask(__name__)


# Temporary user ID.
# Replace this with session/login user ID later.
CURRENT_USER_ID = 1


# =========================================================
# ORGANIZATION LIST
# =========================================================

@app.route("/organizations")
def organizations_page():

    organizations = view_organizations()

    return render_template(
        "organization.html",
        organizations=organizations
    )


# =========================================================
# ORGANIZATION SEARCH API
# =========================================================

@app.route("/api/organizations/search")
def search_organizations_api():

    keyword = request.args.get("q", "").strip()

    if not keyword:
        organizations = view_organizations()
    else:
        organizations = search_organizations(keyword)

    return jsonify({
        "success": True,
        "organizations": organizations
    })


# =========================================================
# ORGANIZATION PROFILE
# =========================================================

@app.route("/organizations/<int:org_id>")
def organization_profile(org_id):

    organization = view_organization_details(org_id)

    if not organization:
        return "Organization not found", 404

    members = view_members(org_id)

    is_member = any(
        member["user_id"] == CURRENT_USER_ID
        for member in members
    )

    return render_template(
        "organization_profile.html",
        organization=organization,
        members=members,
        is_member=is_member
    )


# =========================================================
# JOIN ORGANIZATION
# =========================================================

@app.route(
    "/api/organizations/<int:org_id>/join",
    methods=["POST"]
)
def join_org(org_id):

    result = join_organization(
        org_id,
        CURRENT_USER_ID
    )

    if result:
        return jsonify({
            "success": True,
            "message": "You joined the organization."
        })

    return jsonify({
        "success": False,
        "message": "Unable to join organization."
    }), 400


# =========================================================
# LEAVE ORGANIZATION
# =========================================================

@app.route(
    "/api/organizations/<int:org_id>/leave",
    methods=["POST"]
)
def leave_org(org_id):

    result = leave_organization(
        org_id,
        CURRENT_USER_ID
    )

    if result:
        return jsonify({
            "success": True,
            "message": "You left the organization."
        })

    return jsonify({
        "success": False,
        "message": "Unable to leave organization."
    }), 400


# =========================================================
# MEMBERS API
# =========================================================

@app.route(
    "/api/organizations/<int:org_id>/members"
)
def members_api(org_id):

    members = view_members(org_id)

    return jsonify({
        "success": True,
        "members": members
    })


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
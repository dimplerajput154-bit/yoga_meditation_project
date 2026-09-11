import os
import sys
from pathlib import Path
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

# Allows this file to import Database_Module.py from Backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Database_Module import connection


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_FILE_SIZE = 8 * 1024 * 1024
DEFAULT_USER_ID = 1

app = Flask(
    __name__,
    template_folder=".",
    static_folder=".",
    static_url_path="/static"
)

app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def allowed_file(filename):
    return (
        bool(filename)
        and "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_user_id():
    """Get logged-in user's ID passed by the frontend."""
    value = request.args.get("user_id") or request.form.get("created_by")

    try:
        user_id = int(value)
        return user_id if user_id > 0 else DEFAULT_USER_ID
    except (TypeError, ValueError):
        return DEFAULT_USER_ID


def close_db(cursor, conn):
    if cursor:
        cursor.close()
    if conn:
        conn.close()


def ensure_program_columns(cursor):
    """
    Keeps the program table compatible with the existing project.
    The existing project already uses organization_programs with:
    program_id, org_id, title, description, access_type, duration.
    These extra columns support the richer reference UI.
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organization_programs (
            program_id INT AUTO_INCREMENT PRIMARY KEY,
            org_id INT NOT NULL,
            title VARCHAR(150) NOT NULL,
            description TEXT,
            access_type ENUM('free', 'premium') NOT NULL DEFAULT 'free',
            duration VARCHAR(60),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE
        )
    """)

    # Add richer fields when the table already exists.
    extra_columns = [
        ("price", "VARCHAR(60) NULL"),
        ("image_url", "VARCHAR(500) NULL"),
    ]

    for column_name, definition in extra_columns:
        try:
            cursor.execute(
                f"ALTER TABLE organization_programs "
                f"ADD COLUMN {column_name} {definition}"
            )
        except Exception:
            # Column probably already exists.
            pass


def ensure_optional_organization_columns(cursor):
    """
    Adds optional profile/social columns if they are missing.
    Existing organization columns are not removed or renamed.
    """
    columns = [
        ("website", "VARCHAR(500) NULL"),
        ("instagram", "VARCHAR(500) NULL"),
        ("youtube", "VARCHAR(500) NULL"),
        ("facebook", "VARCHAR(500) NULL"),
        ("twitter", "VARCHAR(500) NULL"),
    ]

    for column_name, definition in columns:
        try:
            cursor.execute(
                f"ALTER TABLE organizations "
                f"ADD COLUMN {column_name} {definition}"
            )
        except Exception:
            pass


def seed_demo_data(cursor):
    """
    Creates sample organizations only when the organizations table is empty.
    This gives the user many organizations immediately after opening the page.
    """
    cursor.execute("SELECT COUNT(*) AS total FROM organizations")
    row = cursor.fetchone()
    total = row["total"] if isinstance(row, dict) else row[0]

    if int(total) > 0:
        return

    demo_orgs = [
        (
            "Isha Foundation",
            "A nonprofit spiritual organization offering yoga, meditation and transformative wellness programs.",
            "Spirituality",
            "public",
            "https://www.isha.sadhguru.org/",
            "https://www.instagram.com/sadhguru/",
            "https://www.youtube.com/@Sadhguru",
            "https://www.facebook.com/Sadhguru",
            None,
            None,
        ),
        (
            "Mindful Living",
            "A supportive community focused on mindfulness, meditation, stress management and peaceful living.",
            "Meditation",
            "public",
            "https://example.com",
            "https://instagram.com/",
            "https://youtube.com/",
            "",
            None,
            None,
        ),
        (
            "Yoga Life",
            "A community helping people build strength, flexibility and balance through accessible yoga practices.",
            "Yoga",
            "public",
            "https://example.com",
            "https://instagram.com/",
            "https://youtube.com/",
            "",
            None,
            None,
        ),
        (
            "Sattvic Movement",
            "A wellness organization combining mindful movement, nutrition and daily practices for healthier living.",
            "Fitness",
            "public",
            "https://example.com",
            "https://instagram.com/",
            "https://youtube.com/",
            "",
            None,
            None,
        ),
        (
            "Happy Thoughts",
            "A mental wellness community for positive thinking, emotional balance and healthy daily habits.",
            "Mental Wellness",
            "public",
            "https://example.com",
            "https://instagram.com/",
            "https://youtube.com/",
            "",
            None,
            None,
        ),
        (
            "Inner Peace Community",
            "A calm community for guided meditation, breathwork, reflection and spiritual growth.",
            "Meditation",
            "public",
            "https://example.com",
            "https://instagram.com/",
            "https://youtube.com/",
            "",
            None,
            None,
        ),
        (
            "Prana Wellness",
            "A holistic wellness community offering yoga, breathwork and lifestyle programs for all ages.",
            "Yoga",
            "public",
            "https://example.com",
            "https://instagram.com/",
            "https://youtube.com/",
            "",
            None,
            None,
        ),
        (
            "Spiritual Journey",
            "A community for self-discovery, meditation, mindful conversations and spiritual practices.",
            "Spirituality",
            "public",
            "https://example.com",
            "https://instagram.com/",
            "https://youtube.com/",
            "",
            None,
            None,
        ),
    ]

    insert_sql = """
        INSERT INTO organizations
        (name, description, category, privacy, created_by,
         logo_url, cover_image_url, website, instagram, youtube, facebook)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for item in demo_orgs:
        (
            name, description, category, privacy,
            website, instagram, youtube, facebook,
            cover_url, logo_url
        ) = item

        cursor.execute(
            insert_sql,
            (
                name, description, category, privacy, DEFAULT_USER_ID,
                logo_url, cover_url, website, instagram, youtube, facebook
            )
        )

        org_id = cursor.lastrowid

        # Make demo creator an admin when the user exists.
        try:
            cursor.execute(
                "INSERT INTO organization_members (org_id, user_id, role) "
                "VALUES (%s, %s, 'admin')",
                (org_id, DEFAULT_USER_ID)
            )
        except Exception:
            pass

        demo_programs = {
            "Isha Foundation": [
                ("Inner Engineering Program", "A transformative wellbeing program.", "premium", "7 days", "₹999", None),
                ("Hatha Yoga Program", "Classical yoga practices for body and mind.", "premium", "30 days", "₹499", None),
                ("Bhava Spandana Meditation", "Guided meditation and inner wellbeing practice.", "free", "1 session", "FREE", None),
                ("Shambhavi Mahamudra Kriya", "A powerful yogic practice taught through an established program.", "premium", "21 days", "₹1499", None),
            ],
            "Mindful Living": [
                ("Beginner Meditation", "Learn simple meditation techniques.", "free", "14 days", "FREE", None),
                ("Stress Relief Program", "Mindfulness practices for a calmer routine.", "premium", "21 days", "₹299", None),
                ("Mindfulness 21 Days", "Build a consistent mindful habit.", "premium", "21 days", "₹599", None),
            ],
            "Yoga Life": [
                ("Morning Yoga", "Start your day with gentle yoga.", "premium", "30 days", "₹399", None),
                ("Yoga for Beginners", "Beginner-friendly yoga foundations.", "free", "7 days", "FREE", None),
                ("Power Yoga", "Dynamic yoga sessions for strength and flexibility.", "premium", "30 days", "₹699", None),
            ],
            "Sattvic Movement": [
                ("Daily Movement", "Simple movement practice for everyday wellness.", "free", "15 days", "FREE", None),
                ("Strength & Mobility", "Build strength while improving mobility.", "premium", "30 days", "₹799", None),
            ],
            "Happy Thoughts": [
                ("Positive Mindset", "Daily practices for positive thinking.", "free", "14 days", "FREE", None),
                ("Emotional Wellness", "Tools for emotional balance and self-awareness.", "premium", "21 days", "₹499", None),
            ],
            "Inner Peace Community": [
                ("Guided Meditation", "Calm guided meditation sessions.", "free", "10 sessions", "FREE", None),
                ("Breathwork Basics", "Learn simple breathing techniques.", "premium", "14 days", "₹399", None),
            ],
            "Prana Wellness": [
                ("Prana Yoga Basics", "Yoga and breath awareness for beginners.", "free", "14 days", "FREE", None),
                ("Holistic Wellness", "Movement, breath and lifestyle practices.", "premium", "30 days", "₹899", None),
            ],
            "Spiritual Journey": [
                ("Self Discovery", "Reflection and mindful self-discovery sessions.", "free", "14 days", "FREE", None),
                ("Spiritual Growth", "Guided practices for inner growth.", "premium", "30 days", "₹699", None),
            ],
        }

        for title, desc, access, duration, price, image in demo_programs.get(name, []):
            cursor.execute(
                """
                INSERT INTO organization_programs
                (org_id, title, description, access_type, duration, price, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (org_id, title, desc, access, duration, price, image)
            )


# ---------------------------------------------------------
# PAGE
# ---------------------------------------------------------

@app.route("/")
def organization_page():
    return render_template("organization.html")


# ---------------------------------------------------------
# LIST ORGANIZATIONS
# ---------------------------------------------------------

@app.route("/api/organizations", methods=["GET"])
def list_organizations():
    conn = None
    cursor = None

    try:
        conn = connection()
        if conn is None:
            return jsonify(success=False, message="Database connection failed."), 500

        cursor = conn.cursor(dictionary=True)

        ensure_optional_organization_columns(cursor)
        ensure_program_columns(cursor)
        seed_demo_data(cursor)
        conn.commit()

        search = request.args.get("search", "").strip()
        user_id = get_user_id()
        pattern = f"%{search}%"

        cursor.execute(
            """
            SELECT
                o.org_id,
                o.name,
                o.logo_url,
                o.cover_image_url,
                o.description,
                o.category,
                o.privacy,
                o.created_by,
                o.created_at,
                o.website,
                o.instagram,
                o.youtube,
                o.facebook,
                o.twitter,
                COUNT(DISTINCT m.user_id) AS follower_count,
                MAX(CASE WHEN m.user_id = %s THEN 1 ELSE 0 END) AS is_following,
                MAX(CASE WHEN o.created_by = %s THEN 1 ELSE 0 END) AS is_owner
            FROM organizations o
            LEFT JOIN organization_members m ON m.org_id = o.org_id
            WHERE
                o.name LIKE %s
                OR o.category LIKE %s
                OR o.description LIKE %s
                OR %s = ''
            GROUP BY o.org_id
            ORDER BY o.created_at DESC
            """,
            (user_id, user_id, pattern, pattern, pattern, search)
        )

        return jsonify(success=True, organizations=cursor.fetchall())

    except Exception as error:
        if conn:
            conn.rollback()
        return jsonify(success=False, message=str(error)), 500

    finally:
        close_db(cursor, conn)


# ---------------------------------------------------------
# ORGANIZATION DETAILS
# ---------------------------------------------------------

@app.route("/api/organizations/<int:org_id>", methods=["GET"])
def organization_details(org_id):
    conn = None
    cursor = None

    try:
        conn = connection()
        if conn is None:
            return jsonify(success=False, message="Database connection failed."), 500

        cursor = conn.cursor(dictionary=True)

        ensure_optional_organization_columns(cursor)
        ensure_program_columns(cursor)
        conn.commit()

        user_id = get_user_id()

        cursor.execute(
            """
            SELECT
                o.*,
                COUNT(DISTINCT m.user_id) AS follower_count
            FROM organizations o
            LEFT JOIN organization_members m
                ON m.org_id = o.org_id
            WHERE o.org_id = %s
            GROUP BY o.org_id
            """,
            (org_id,)
        )

        organization = cursor.fetchone()

        if not organization:
            return jsonify(success=False, message="Organization not found."), 404

        cursor.execute(
            """
            SELECT
                program_id,
                title,
                description,
                access_type,
                duration,
                price,
                image_url
            FROM organization_programs
            WHERE org_id = %s
            ORDER BY created_at DESC
            """,
            (org_id,)
        )

        organization["programs"] = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                membership_id,
                user_id,
                role,
                joined_at
            FROM organization_members
            WHERE org_id = %s
            ORDER BY CASE WHEN role = 'admin' THEN 0 ELSE 1 END, joined_at ASC
            """,
            (org_id,)
        )

        members = cursor.fetchall()

        # Fetch user information separately so this also works with
        # projects where users.profile_image is not available.
        for member in members:
            try:
                cursor.execute(
                    "SELECT full_name, profile_image FROM users WHERE user_id = %s",
                    (member["user_id"],)
                )
                user = cursor.fetchone()
                if user:
                    member["full_name"] = user.get("full_name")
                    member["profile_image"] = user.get("profile_image")
                else:
                    member["full_name"] = "Member"
                    member["profile_image"] = None
            except Exception:
                member["full_name"] = "Member"
                member["profile_image"] = None

        organization["members"] = members
        organization["member_count"] = len(members)
        organization["is_owner"] = int(organization["created_by"]) == user_id

        cursor.execute(
            """
            SELECT membership_id, role
            FROM organization_members
            WHERE org_id = %s AND user_id = %s
            """,
            (org_id, user_id)
        )

        membership = cursor.fetchone()
        organization["is_following"] = bool(membership)
        organization["rating"] = 4.9

        return jsonify(success=True, organization=organization)

    except Exception as error:
        if conn:
            conn.rollback()
        return jsonify(success=False, message=str(error)), 500

    finally:
        close_db(cursor, conn)


# ---------------------------------------------------------
# CREATE ORGANIZATION
# ---------------------------------------------------------

@app.route("/api/organizations", methods=["POST"])
def create_organization():
    conn = None
    cursor = None

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "Wellness").strip()
    privacy = request.form.get("privacy", "public").strip().lower()

    if len(name) < 3:
        return jsonify(success=False, message="Organization name must contain at least 3 characters."), 400

    if len(description) < 10:
        return jsonify(success=False, message="Please enter a proper organization description."), 400

    if privacy not in ("public", "private"):
        privacy = "public"

    try:
        created_by = int(request.form.get("created_by", DEFAULT_USER_ID))
        if created_by < 1:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify(success=False, message="Invalid creator user ID."), 400

    logo = request.files.get("logo")
    cover = request.files.get("cover_image")
    program_image = request.files.get("program_image")

    for image in (logo, cover, program_image):
        if image and image.filename and not allowed_file(image.filename):
            return jsonify(
                success=False,
                message="Only PNG, JPG, JPEG and WEBP images are allowed."
            ), 400

    try:
        conn = connection()
        if conn is None:
            return jsonify(success=False, message="Database connection failed."), 500

        cursor = conn.cursor()

        ensure_optional_organization_columns(cursor)
        ensure_program_columns(cursor)

        cursor.execute(
            """
            SELECT org_id
            FROM organizations
            WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
            """,
            (name,)
        )

        if cursor.fetchone():
            return jsonify(
                success=False,
                message="An organization with this name already exists."
            ), 409

        website = request.form.get("website", "").strip() or None
        instagram = request.form.get("instagram", "").strip() or None
        youtube = request.form.get("youtube", "").strip() or None
        facebook = request.form.get("facebook", "").strip() or None

        cursor.execute(
            """
            INSERT INTO organizations
            (name, description, category, privacy, created_by,
             website, instagram, youtube, facebook)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                name,
                description,
                category,
                privacy,
                created_by,
                website,
                instagram,
                youtube,
                facebook
            )
        )

        org_id = cursor.lastrowid

        logo_url = None
        cover_url = None

        if logo and logo.filename:
            logo_filename = (
                f"org_{org_id}_logo_"
                f"{secure_filename(logo.filename)}"
            )
            logo.save(UPLOAD_DIR / logo_filename)
            logo_url = f"/static/uploads/{logo_filename}"

        if cover and cover.filename:
            cover_filename = (
                f"org_{org_id}_cover_"
                f"{secure_filename(cover.filename)}"
            )
            cover.save(UPLOAD_DIR / cover_filename)
            cover_url = f"/static/uploads/{cover_filename}"

        program_image_url = None
        if program_image and program_image.filename:
            program_filename = (
                f"org_{org_id}_program_"
                f"{secure_filename(program_image.filename)}"
            )
            program_image.save(UPLOAD_DIR / program_filename)
            program_image_url = f"/static/uploads/{program_filename}"

        cursor.execute(
            """
            UPDATE organizations
            SET logo_url = %s,
                cover_image_url = %s
            WHERE org_id = %s
            """,
            (logo_url, cover_url, org_id)
        )

        # Creator automatically becomes administrator.
        cursor.execute(
            """
            INSERT INTO organization_members
            (org_id, user_id, role)
            VALUES (%s, %s, 'admin')
            """,
            (org_id, created_by)
        )

        # Optional first program.
        program_title = request.form.get("program_title", "").strip()

        if program_title:
            program_description = request.form.get("program_description", "").strip()
            program_duration = request.form.get("program_duration", "").strip()
            program_price = request.form.get("program_price", "").strip()

            access_type = (
                "free"
                if program_price.upper() == "FREE" or not program_price
                else "premium"
            )

            cursor.execute(
                """
                INSERT INTO organization_programs
                (org_id, title, description, access_type, duration, price, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    org_id,
                    program_title,
                    program_description,
                    access_type,
                    program_duration,
                    program_price or "FREE",
                    program_image_url
                )
            )

        conn.commit()

        return jsonify(
            success=True,
            message="Organization created successfully.",
            organization_id=org_id
        ), 201

    except Exception as error:
        if conn:
            conn.rollback()

        return jsonify(
            success=False,
            message=str(error)
        ), 500

    finally:
        close_db(cursor, conn)


# ---------------------------------------------------------
# FOLLOW / UNFOLLOW
# ---------------------------------------------------------

@app.route("/api/organizations/<int:org_id>/follow", methods=["POST"])
def follow_organization(org_id):
    conn = None
    cursor = None

    try:
        user_id = get_user_id()

        conn = connection()
        if conn is None:
            return jsonify(success=False, message="Database connection failed."), 500

        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT org_id FROM organizations WHERE org_id = %s",
            (org_id,)
        )

        if not cursor.fetchone():
            return jsonify(success=False, message="Organization not found."), 404

        cursor.execute(
            """
            SELECT membership_id, role
            FROM organization_members
            WHERE org_id = %s AND user_id = %s
            """,
            (org_id, user_id)
        )

        membership = cursor.fetchone()

        if membership and membership["role"] == "admin":
            return jsonify(
                success=True,
                following=True,
                message="You manage this organization."
            )

        if membership:
            cursor.execute(
                """
                DELETE FROM organization_members
                WHERE org_id = %s AND user_id = %s
                """,
                (org_id, user_id)
            )
            conn.commit()

            return jsonify(
                success=True,
                following=False,
                message="You unfollowed this organization."
            )

        cursor.execute(
            """
            INSERT INTO organization_members
            (org_id, user_id, role)
            VALUES (%s, %s, 'member')
            """,
            (org_id, user_id)
        )

        conn.commit()

        return jsonify(
            success=True,
            following=True,
            message="You are now following this organization."
        )

    except Exception as error:
        if conn:
            conn.rollback()

        return jsonify(success=False, message=str(error)), 500

    finally:
        close_db(cursor, conn)


# ---------------------------------------------------------
# ADD PROGRAM
# ---------------------------------------------------------

@app.route("/api/organizations/<int:org_id>/programs", methods=["POST"])
def add_program(org_id):
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    duration = request.form.get("duration", "").strip()
    price = request.form.get("price", "").strip() or "FREE"
    access_type = request.form.get("access_type", "free").lower()
    program_image = request.files.get("program_image")

    if not title:
        return jsonify(success=False, message="Program title is required."), 400

    if access_type not in ("free", "premium"):
        return jsonify(success=False, message="Program access must be free or premium."), 400

    if program_image and program_image.filename and not allowed_file(program_image.filename):
        return jsonify(
            success=False,
            message="Only PNG, JPG, JPEG and WEBP images are allowed."
        ), 400

    conn = None
    cursor = None

    try:
        user_id = get_user_id()

        conn = connection()
        if conn is None:
            return jsonify(success=False, message="Database connection failed."), 500

        cursor = conn.cursor(dictionary=True)
        ensure_program_columns(cursor)

        cursor.execute(
            """
            SELECT org_id
            FROM organizations
            WHERE org_id = %s AND created_by = %s
            """,
            (org_id, user_id)
        )

        if not cursor.fetchone():
            return jsonify(
                success=False,
                message="Only the organization owner can add programs."
            ), 403

        image_url = None
        if program_image and program_image.filename:
            filename = f"org_{org_id}_program_{secure_filename(program_image.filename)}"
            program_image.save(UPLOAD_DIR / filename)
            image_url = f"/static/uploads/{filename}"

        cursor.execute(
            """
            INSERT INTO organization_programs
            (org_id, title, description, access_type, duration, price, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (org_id, title, description, access_type, duration, price, image_url)
        )

        conn.commit()

        return jsonify(
            success=True,
            message="Program added successfully.",
            program_id=cursor.lastrowid
        ), 201

    except Exception as error:
        if conn:
            conn.rollback()
        return jsonify(success=False, message=str(error)), 500

    finally:
        close_db(cursor, conn)


# ---------------------------------------------------------
# DELETE ORGANIZATION
# ---------------------------------------------------------

@app.route("/api/organizations/<int:org_id>", methods=["DELETE"])
def delete_organization(org_id):
    conn = None
    cursor = None

    try:
        user_id = get_user_id()

        conn = connection()
        if conn is None:
            return jsonify(success=False, message="Database connection failed."), 500

        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM organizations
            WHERE org_id = %s AND created_by = %s
            """,
            (org_id, user_id)
        )

        if cursor.rowcount == 0:
            return jsonify(
                success=False,
                message="Only the organization owner can delete it."
            ), 403

        conn.commit()

        return jsonify(
            success=True,
            message="Organization deleted successfully."
        )

    except Exception as error:
        if conn:
            conn.rollback()
        return jsonify(success=False, message=str(error)), 500

    finally:
        close_db(cursor, conn)


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Wellness Organization Server")
    print("http://127.0.0.1:5002")
    print("=" * 60)
    app.run(debug=True, port=5002)

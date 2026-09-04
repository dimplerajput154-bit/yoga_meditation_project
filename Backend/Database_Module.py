
import mysql.connector


"""
Function-1: connection()

Purpose:
    Creates a connection with MySQL server.
    Creates the ai_wellness_db database if it does not exist.
    Returns a connection object connected to ai_wellness_db.

Input:
    None

Output:
    MySQL connection object
"""

#in password, use your own password for the MySQL server and also username which you have set for your MySQL server
def connection():

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234"
        )

        cursor = conn.cursor()

        # Create database if it does not exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS ai_wellness_db")

        cursor.close()
        conn.close()

        # Connect to the created database
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="ai_wellness_db"
        )

    except Exception as e:
        print("Connection error:", e)
        return None


"""
Function-2: create_tables()

Purpose:
    Creates all required tables for the AI Wellness project.

Input:
    None

Output:
    None
"""


def create_tables():

    try:

        conn = connection()

        if conn is None:
            print("Database connection failed.")
            return None

        cursor = conn.cursor()

        # =========================================================
        # 1. USERS
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
            profile_image VARCHAR(255) DEFAULT NULL,
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT NULL
                ON UPDATE CURRENT_TIMESTAMP,

            INDEX idx_users_role (role)
        )
        """)

        # =========================================================
        # 2. HEALTH PROFILES
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_profiles (
            profile_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL UNIQUE,
            age INT DEFAULT NULL,
            gender ENUM('male', 'female', 'other') DEFAULT NULL,
            height_cm DECIMAL(5,2) DEFAULT NULL,
            weight_kg DECIMAL(5,2) DEFAULT NULL,
            activity_level ENUM(
                'sedentary',
                'light',
                'moderate',
                'active'
            ) DEFAULT 'sedentary',
            diet_preference VARCHAR(50) DEFAULT NULL,
            allergies TEXT DEFAULT NULL,
            existing_conditions TEXT DEFAULT NULL,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_health_profile_user
                FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE,

            CONSTRAINT chk_health_age
                CHECK (age IS NULL OR age > 0)
        )
        """)

        # =========================================================
        # 3. YOGA
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS yoga (
            yoga_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            description TEXT DEFAULT NULL,
            video_url VARCHAR(255) DEFAULT NULL,
            thumbnail_url VARCHAR(255) DEFAULT NULL,
            duration_minutes INT DEFAULT NULL,
            difficulty ENUM(
                'beginner',
                'intermediate',
                'advanced'
            ) NOT NULL DEFAULT 'beginner',
            category VARCHAR(50) DEFAULT NULL,
            is_downloadable TINYINT(1) NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            INDEX idx_yoga_category (category),
            INDEX idx_yoga_difficulty (difficulty),
            INDEX idx_yoga_title (title)
        )
        """)

        # =========================================================
        # 4. MEDITATIONS
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS meditations (
            meditation_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            description TEXT DEFAULT NULL,
            media_url VARCHAR(255) DEFAULT NULL,
            duration_minutes INT DEFAULT NULL,
            category VARCHAR(50) DEFAULT NULL,
            is_downloadable TINYINT(1) NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            INDEX idx_meditation_category (category),
            INDEX idx_meditation_title (title)
        )
        """)

        # =========================================================
        # 5. RECIPES
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            recipe_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            description TEXT DEFAULT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            prep_time_minutes INT DEFAULT NULL,
            calories INT DEFAULT NULL,
            category VARCHAR(50) DEFAULT NULL,
            image_url VARCHAR(255) DEFAULT NULL,
            is_downloadable TINYINT(1) NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            INDEX idx_recipes_category (category),
            INDEX idx_recipes_title (title)
        )
        """)

        # =========================================================
        # 6. BOOKS
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            author VARCHAR(100) DEFAULT NULL,
            description TEXT DEFAULT NULL,
            cover_image_url VARCHAR(255) DEFAULT NULL,
            file_url VARCHAR(255) DEFAULT NULL,
            category VARCHAR(50) DEFAULT NULL,
            is_downloadable TINYINT(1) NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            INDEX idx_books_category (category),
            INDEX idx_books_title (title),
            INDEX idx_books_author (author)
        )
        """)

        # =========================================================
        # 7. SLEEP RECORDS
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sleep_records (
            record_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            record_date DATE NOT NULL,
            sleep_time TIME NOT NULL,
            wake_time TIME NOT NULL,
            duration_minutes INT DEFAULT NULL,
            quality ENUM(
                'poor',
                'average',
                'good',
                'excellent'
            ) DEFAULT NULL,
            notes TEXT DEFAULT NULL,
            report_file VARCHAR(255) DEFAULT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_sleep_user
                FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE,

            INDEX idx_sleep_user_date (user_id, record_date)
        )
        """)

        # =========================================================
        # 8. MOOD RECORDS
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_records (
            record_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            record_date DATE NOT NULL,
            mood ENUM(
                'happy',
                'good',
                'neutral',
                'stressed',
                'sad'
            ) NOT NULL,
            stress_level TINYINT DEFAULT NULL,
            notes TEXT DEFAULT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_mood_user
                FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE,

            CONSTRAINT chk_stress_level
                CHECK (
                    stress_level IS NULL
                    OR stress_level BETWEEN 1 AND 10
                ),

            INDEX idx_mood_user_date (user_id, record_date)
        )
        """)

        # =========================================================
        # 9. HEALTH REMEDIES
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_remedies (
            remedy_id INT AUTO_INCREMENT PRIMARY KEY,
            topic VARCHAR(100) NOT NULL,
            symptoms TEXT DEFAULT NULL,
            self_care_info TEXT DEFAULT NULL,
            precautions TEXT DEFAULT NULL,
            when_to_consult_doctor TEXT DEFAULT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            INDEX idx_health_topic (topic)
        )
        """)

        # =========================================================
        # 10. LIKES
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            like_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            content_type ENUM(
                'yoga',
                'meditation',
                'recipe',
                'book'
            ) NOT NULL,
            content_id INT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_like_user
                FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE,

            CONSTRAINT uq_like
                UNIQUE (user_id, content_type, content_id),

            INDEX idx_like_content (content_type, content_id)
        )
        """)

        # =========================================================
        # 11. FAVORITES
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            favorite_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            content_type ENUM(
                'yoga',
                'meditation',
                'recipe',
                'book'
            ) NOT NULL,
            content_id INT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_favorite_user
                FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE,

            CONSTRAINT uq_favorite
                UNIQUE (user_id, content_type, content_id),

            INDEX idx_favorite_user (user_id)
        )
        """)

        # =========================================================
        # 12. DOWNLOADS
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            download_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            content_type ENUM(
                'yoga',
                'meditation',
                'recipe',
                'book'
            ) NOT NULL,
            content_id INT NOT NULL,
            file_url VARCHAR(255) NOT NULL,
            downloaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_download_user
                FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE,

            INDEX idx_download_user (user_id),
            INDEX idx_download_content (content_type, content_id)
        )
        """)

        # =========================================================
        # 13. ORGANIZATIONS
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            org_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            logo_url VARCHAR(255) DEFAULT NULL,
            cover_image_url VARCHAR(255) DEFAULT NULL,
            description TEXT DEFAULT NULL,
            category VARCHAR(50) DEFAULT NULL,
            privacy ENUM('public', 'private') NOT NULL DEFAULT 'public',
            created_by INT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_organization_creator
                FOREIGN KEY (created_by)
                REFERENCES users(user_id)
                ON DELETE RESTRICT,

            INDEX idx_organization_name (name),
            INDEX idx_organization_category (category)
        )
        """)

        # =========================================================
        # 14. ORGANIZATION MEMBERS
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS organization_members (
            membership_id INT AUTO_INCREMENT PRIMARY KEY,
            org_id INT NOT NULL,
            user_id INT NOT NULL,
            role ENUM(
                'admin',
                'moderator',
                'member'
            ) NOT NULL DEFAULT 'member',
            joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_membership_org
                FOREIGN KEY (org_id)
                REFERENCES organizations(org_id)
                ON DELETE CASCADE,

            CONSTRAINT fk_membership_user
                FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE,

            CONSTRAINT uq_organization_member
                UNIQUE (org_id, user_id),

            INDEX idx_membership_user (user_id)
        )
        """)

        # =========================================================
        # 15. DISCUSSIONS
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS discussions (
            discussion_id INT AUTO_INCREMENT PRIMARY KEY,
            org_id INT NOT NULL,
            user_id INT NOT NULL,
            title VARCHAR(150) NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_discussion_org
                FOREIGN KEY (org_id)
                REFERENCES organizations(org_id)
                ON DELETE CASCADE,

            CONSTRAINT fk_discussion_user
                FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE,

            INDEX idx_discussion_org (org_id),
            INDEX idx_discussion_created (created_at)
        )
        """)

        # =========================================================
        # 16. COMMENTS
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            comment_id INT AUTO_INCREMENT PRIMARY KEY,
            discussion_id INT NOT NULL,
            user_id INT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_comment_discussion
                FOREIGN KEY (discussion_id)
                REFERENCES discussions(discussion_id)
                ON DELETE CASCADE,

            CONSTRAINT fk_comment_user
                FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE,

            INDEX idx_comment_discussion (discussion_id)
        )
        """)

        # =========================================================
        # 17. AI CHATS
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_chats (
            chat_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            message TEXT NOT NULL,
            response TEXT DEFAULT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_ai_chat_user
                FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE,

            INDEX idx_ai_chat_user_date (user_id, created_at)
        )
        """)

        # =========================================================
        # 18. NOTIFICATIONS
        # =========================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(150) NOT NULL,
            message TEXT DEFAULT NULL,
            type VARCHAR(50) DEFAULT NULL,
            is_read TINYINT(1) NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_notification_user
                FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE,

            INDEX idx_notification_user_read (user_id, is_read)
        )
        """)

        conn.commit()

        cursor.close()
        conn.close()

        print("Database and tables created successfully.")

    except Exception as e:
        print("Something went wrong:", e)

        if 'conn' in locals() and conn:
            conn.rollback()

        return None


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    create_tables()


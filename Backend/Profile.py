from Database import get_connection


def get_profile(user_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT user_id, full_name, email, role,
               profile_image,is_active
        FROM users
        WHERE user_id = %s
    """

    cursor.execute(query, (user_id,))

    profile = cursor.fetchone()

    cursor.close()
    conn.close()

    return profile


def update_profile(
    user_id,
    full_name,
    profile_image
   
):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        UPDATE users
        SET full_name = %s,
            profile_image = %s
        WHERE user_id = %s
    """

    cursor.execute(
        query,
        (
            full_name,
            profile_image,
            user_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    print("Profile updated successfully!")

if __name__=="__main__":
    user_id = int(input("Enter user_id:"))
    profile = get_profile(user_id)
    if profile:
        print("Profile:",profile)
    else:
        print("Profile not found")    


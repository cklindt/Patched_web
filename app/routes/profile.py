from flask import Blueprint, render_template, redirect, url_for, request, flash
from .session import get_user
import logging
from app.database import get_db_connection

profile_bp = Blueprint("profile", __name__)

@profile_bp.route('/profile', methods=['GET'])
def profile():
    user = get_user()
    if user is None:
        return redirect(url_for('login.login'))

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if user.role == 'instructor':
                cur.execute("""
                    SELECT c.course_id, c.title, c.description, c.image_path
                    FROM courses c
                    WHERE c.instructor_id = (SELECT user_id FROM users WHERE username = %s)
                """, (user.username,))
                courses = cur.fetchall()
            else:
                # Fetch enrolled courses
                cur.execute("""
                    SELECT c.course_id, c.title, c.description, c.image_path
                    FROM enrollments e
                    JOIN courses c ON e.course_id = c.course_id
                    WHERE e.student_id = (SELECT user_id FROM users WHERE username = %s)
                """, (user.username,))
                courses = cur.fetchall()

    return render_template('profile.html', user=user, courses=courses)

@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    user = get_user()

    if user is None:
        return redirect(url_for('login.login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                f"""
                UPDATE users
                SET username = '{username}', password = '{password}'
                WHERE user_id = '{user.user_id}'
                """
            )
            conn.commit()

            cur.close()
            conn.close()

            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile.profile', user=user))
        
        except Exception as e:
            flash('An error occured while updating profile', 'danger')

    else:
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(f"SELECT username FROM users WHERE user_id = '{user.user_id}'")
            user_info = cur.fetchone()

            cur.close()
            conn.close()

        except Exception as e:
            logging.error(e)
            return "An error occured while fetching user data.", 500
        
    return render_template('edit_profile.html', user=user_info)

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from .session import get_user
import logging
import os, subprocess
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
                """
                UPDATE users
                SET username = %s, password = %s
                WHERE user_id = %s
                """,
                (username, password, user.user_id)
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

@profile_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    user = get_user()

    if user is None:
        return redirect(url_for('login.login'))
    
    upload_dir = os.path.join(current_app.root_path, 'uploads')
    uploaded_files = os.listdir(os.path.join(upload_dir))

    if request.method == 'POST':
        file = request.files['file']

        try:
            allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx'}
            file_ext = os.path.splitext(file.filename)[1][1:].lower()
            if file_ext not in allowed_extensions:
                flash(f'File type .{file_ext} is not allowed', 'danger')
                return redirect(url_for('profile.upload_file'))
            import uuid 
            random_filename = f"{uuid.uuid4().hex}.{file_ext}"
            file_path = os.path.join(upload_dir, random_filename)
            file.save(file_path)
            flash('File uploaded successfully', 'success')

        except Exception as e:
            flash(f'Error uploading file: {e}', 'danger')

        return redirect(url_for('profile.upload_file'))
    
    return render_template('upload.html', user=user, uploaded_files=uploaded_files)

@profile_bp.route('/run/<filename>', methods=['POST'])
def run_file(filename):
    flash("you can't do that","warning")
    return redirect(url_for('profile.upload_file'))

@profile_bp.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    # Set upload variables    
    upload_dir = os.path.join(current_app.root_path, 'uploads')
    file_path = os.path.join(upload_dir, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            flash('File deleted successfully', 'success')
        else:
            flash('File not found', 'danger')
        
    except Exception as e:
        flash(f'File could not be deleted: {e}', 'danger')
    
    return redirect(url_for('profile.upload_file'))

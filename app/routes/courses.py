from flask import Blueprint, redirect, render_template, render_template_string, url_for, request, flash, current_app
import logging, os
from werkzeug.utils import secure_filename
from psycopg2 import sql

from .session import get_user
from app.database import get_db_connection

course_bp = Blueprint("courses", __name__)

@course_bp.route("/courses")
@course_bp.route("/courses.html")
def courses():
    user = get_user()
    enrolled_courses = []

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Fetch currently enrolled courses for logged-in users
                if user:
                    cur.execute("SELECT course_id FROM enrollments WHERE student_id = %s", (user.user_id,))
                    enrolled_courses = {row[0] for row in cur.fetchall()}

                # Fetch all courses
                cur.execute("SELECT course_id, title, description, image_path FROM courses")
                all_courses = cur.fetchall()

                # Filter out courses the user is already enrolled in
                if user:
                    courses = [course for course in all_courses if course[0] not in enrolled_courses]
                else:
                    courses = all_courses

    except Exception as e:
        logging.error(f"Error: {e}")
        courses = []

    return render_template('courses.html', user=user, courses=courses)

@course_bp.route('/search_course', methods=['GET', 'POST'])
def search_course():
    search_result = None
    
    if request.method == 'POST':
        search_query = request.form.get('search_query', '')

        if not search_query:
            flash('Please enter a search query.', 'danger')
            return redirect(url_for('courses.search'))
        
        search_result = search_query
    
    template_string = """
    {% extends "base.html" %}

    {% block title %}Course Suggestions{% endblock %}

    {% block content %}
    <div class="container mt-5">
        <!-- Display Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=True) %}
            {% if messages %}
                <div class="alert-container">
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">
                            {{ message }}
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        <h1>Suggest Course</h1>
        <form method="post" action="{{ url_for('courses.search_course') }}">
            <div class="form-group">
                <label for="search_query">Course Topic:</label>
                <input id="search_query" name="search_query" class="form-control" type="text" placeholder="Enter course topic..." required>
            </div>
            <button type="submit" class="btn btn-primary">Search</button>
        </form>

        {% if search_result %}
            <h2 class="mt-5">Suggesstion:</h2>
            <p>""" + str(search_result) + """</p>
        {% endif %}
    </div>
    {% endblock %}
    """

    return render_template_string(template_string, search_result=search_result)

@course_bp.route("/add_course", methods=['GET', 'POST'])
def add_course():
    user = get_user()

    if user.role not in ['instructor', 'admin']:
        return redirect(url_for('courses.courses'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        instructor_id = user.user_id
        image = request.files.get('image')

        if image:
            filename = secure_filename(image.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)
            image_path = os.path.join('images', filename)
    

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO courses (title, description, instructor_id, image_path) 
                    VALUES ('{title}', '{description}', '{instructor_id}', '{image_path}')
                    """
                )
                conn.commit()
        flash('Course added successfully', 'success')
        return render_template('add_course.html', user=user)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id, username FROM users WHERE role = 'instructor'")
                instructors = cur.fetchall()
    except Exception as e:
        flash(f"An error occured while fetching instructors: {e}", 'danger')
        instructors = []

    return render_template('add_course.html', user=user, instructors=instructors)
        
@course_bp.route('/enroll/<int:course_id>')
def enroll(course_id):
    user = get_user()

    if user is None or user.role != 'student':
        return redirect(url_for('courses.courses'))
    
    student_id = user.user_id

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO enrollments (student_id, course_id)
                VALUES ('{student_id}', '{course_id}')
                """
            )
            conn.commit()

    return redirect(url_for('courses.courses'))

@course_bp.route('/unroll/<int:course_id>')
def unroll(course_id):
    user = get_user()

    student_id = user.user_id

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                DELETE FROM enrollments WHERE student_id = '{student_id}' AND
                course_id = '{course_id}'
                """
            )
            conn.commit()

    return redirect(url_for('profile.profile'))

@course_bp.route('/remove_course/<int:course_id>', methods=['GET', 'POST'])
def remove_course(course_id):
    user = get_user()

    if user is None:
        return redirect(url_for('index.index'))
    
    referrer = request.referrer

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM courses WHERE course_id = %s", (course_id,))
            conn.commit()

    if user.is_admin:
        if referrer and 'admin_dashboard' in referrer:
            return redirect(url_for('admin.admin_dashboard'))
        
    return redirect(url_for('courses.courses'))

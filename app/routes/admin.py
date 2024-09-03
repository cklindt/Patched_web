from flask import Blueprint, request, render_template, redirect, url_for, render_template_string
import subprocess
from .session import get_user
import logging
from app.database import get_db_connection

admin_bp = Blueprint("admin", __name__)

@admin_bp.route('/admin_dashboard', methods=['GET', 'POST'])
@admin_bp.route('/admin_dashboard.html', methods=['GET', 'POST'])
def admin_dashboard():
    user = get_user()
    if user is None or not user.is_admin:
        return redirect(url_for('login.login'))
    
    if request.method == 'POST':
        user_id = request.form['user_id']
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"DELETE FROM users WHERE user_id = '{user_id}'")
                    conn.commit()
                    cur.close()
        except Exception as e:
            logging.error(e) 
            return redirect(url_for('index.index'))
        
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id, username, password, role FROM users")
                users = cur.fetchall()
    except Exception as e:
        logging.error(e)
        users = []

    return render_template('admin_dashboard.html', user=user, users=users)

@admin_bp.route('/admin_dashboard/system_monitor', methods=['GET', 'POST'])
def system_monitor():
    user = get_user()

    if user is None or not user.is_admin:
        return redirect(url_for('login.login'))
    
    default_cmd = 'uptime'
    output = ""

    if request.method == 'POST':
        cmd = request.form.get('command', 'uptime')
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            output = e.output
        except Exception as e:
            output = f"An error occurred: {e}"
    else:
        cmd = default_cmd

    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    except Exception as e:
        output = f"An error occurred: {e}"

    template_string = """
    {% extends "base.html" %}

    {% block title %}Admin Dashboard - Execute Command{% endblock %}

    {% block content %}
    <h2>System Command</h2>
    <form method="post" action="{{ url_for('admin.system_monitor') }}">
        <div class="form-group">
            <label for="command">Command:</label>
            <input type="text" id="command" name="command" class="form-control" placeholder="Enter command" required>
        </div>
        <button type="submit" class="btn btn-primary mb-3">Execute</button>
    </form>

    {% if output %}
    <h3>Command Output</h3>
    <pre>{{ output }}</pre>
    {% endif %}
    {% endblock %}
    """

    return render_template_string(template_string, output=output, user=user)

# @admin_bp.route('/admin_dashboard/add_course', methods=['POST'])
# def add_course():
#     user = get_user()
#     if user is None or not user.is_admin:
#         return redirect(url_for('login.login'))
    
#     course_name = request.form.get('course_name', '')
#     course_description = request.form.get('course_description', '')

#     try:
#         with get_db_connection() as conn:
#             with conn.cursor() as cur:
#                 query = f"""
#                 INSERT INTO courses (title, description, instructor_id) VALUES ('{course_name}', '{course_description}', 2)
#                 """
#                 cur.execute(query=query)
#                 conn.commit()
#                 message = "Course added successfully!"
#     except Exception as e:
#         logging.error(f"An error occurred while adding the course: {e}")
#         message = f"Error: {e}"

#     return render_template('admin_dashboard.html', user=user, message=message)


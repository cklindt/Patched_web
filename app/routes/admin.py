from flask import Blueprint, request, render_template, redirect, url_for, render_template_string, flash
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
                    cur.execute(f"DELETE FROM users WHERE user_id = %s", (user_id,))
                    conn.commit()
        except Exception as e:
            logging.error(e) 
            return redirect(url_for('index.index'))
        
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id, username, password, role FROM users ORDER BY user_id")
                users = cur.fetchall()
    except Exception as e:
        logging.error(e)
        users = []

    return render_template('admin_dashboard.html', user=user, users=users)

@admin_bp.route('/admin_dashboard/system_monitor', methods=['GET', 'POST'])
def system_monitor():
    user = get_user()
    
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

@admin_bp.route('/admin_dashboard/add_user', methods=['GET', 'POST'])
def add_user():
    user = get_user()

    if user is None or not user.is_admin:
        return redirect(url_for('login.login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if not username or not password or not role:
            #logging.error(f"User: {username}, Pass: {password}, Role: {role}")
            flash('Please provide all required fields', 'danger')
            return render_template('add_user.html', user=user)
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                    INSERT INTO users (username, password, role) 
                    VALUES (%s, %s, %s)            
                    """, (username, password, role))
                    conn.commit()
                    flash('User add successfully', 'success')
                    return render_template('add_user.html', user=user)
        except Exception as e:
            flash(f'An error occured: {e}', 'danger')
        
    return render_template('add_user.html', user=user)
                    
@admin_bp.route('/admin_dashboard/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = get_user()

    if user is None or not user.is_admin:
        return redirect(url_for('login.login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                    UPDATE users SET username = %s, password = %s, role = %s WHERE user_id = %s
                    """, (username, password, role, user_id))
                    conn.commit()
                    flash("User updated successfully", 'success')
                    return redirect(url_for('admin.admin_dashboard'))
        except Exception as e:
            flash(f"Error occured while updating user: {e}", 'danger')
            return render_template('admin_dashboard.html')
          
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT username, password, role FROM users WHERE user_id = %s", (user_id,))
                user_data = cur.fetchone()
    except Exception as e:
        logging.error(e)
        flash(f'An error occured while fetching user data: {e}')
        return redirect(url_for('admin_dashboard.html'))
        
    return render_template('edit_user.html', user=user, user_id=user_id, user_data=user_data)

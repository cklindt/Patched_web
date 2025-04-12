from flask import Blueprint, request, render_template, redirect, url_for, render_template_string, flash
import subprocess
import logging

from .session import get_user
from app.database import get_db_connection

admin_bp = Blueprint("admin", __name__)

@admin_bp.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    user = get_user()
    if user is None or not user.is_admin:
        return redirect(url_for('login.login'))
    
    search_query = request.args.get('search', '')

    if request.method == 'POST':
        user_id = request.form['user_id']
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                    conn.commit()
            flash("User deleted successfully.", "success")
        except Exception as e:
            logging.error(e)
            flash(f"An error occurred: {e}", "danger")
            return redirect(url_for('admin.admin_dashboard'))
        
    # Pagination handling
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Calculate start index for pagination
    start_index = (page - 1) * per_page

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if there is a search query
                if search_query:
                    # Fetch users based on the search query
                    cur.execute("""
                        SELECT user_id, username, password, role 
                        FROM users 
                        WHERE username ILIKE %s 
                        ORDER BY user_id 
                        LIMIT %s OFFSET %s
                    """, (f"%{search_query}%", per_page, start_index))
                else:
                    # Fetch all users if no search query
                    cur.execute("""
                        SELECT user_id, username, password, role 
                        FROM users 
                        ORDER BY user_id 
                        LIMIT %s OFFSET %s
                    """, (per_page, start_index))

                users = cur.fetchall()

                # Count total users based on search query or all users
                if search_query:
                    cur.execute("SELECT COUNT(*) FROM users WHERE username ILIKE %s", (f"%{search_query}%",))
                else:
                    cur.execute("SELECT COUNT(*) FROM users")
                total_users = cur.fetchone()[0]
                total_pages = (total_users + per_page - 1) // per_page

                # Fetch courses
                cur.execute("SELECT course_id, title, description, instructor_id FROM courses ORDER BY course_id")
                courses = cur.fetchall()
    except Exception as e:
        logging.error(e)
        users = []
        courses = []
        total_pages = 1

    return render_template('admin_dashboard.html', user=user, users=users, courses=courses, total_pages=total_pages, current_page=page, search_query=search_query)

@admin_bp.route('/admin_dashboard/system_monitor', methods=['GET', 'POST'])
def system_monitor():
    user = get_user()
    
    default_cmd = 'uptime'
    output = ""
    ALLOWED_COMMANDS = {
        'uptime':['uptime'],
        'memory':['free','-h'],
        'disk':['df','-h'],
        'cpu':['lscpu'],
        'processes':['ps','aux'],
        'network':['netstat','-tulpn']
        }

    if request.method == 'POST':
        cmd = request.form.get('command', 'uptime')
        try:
            if cmd in ALLOWED_COMMANDS:
                output = subprocess.check_output(ALLOWED_COMMANDS[cmd],stderr=subprocess.STDOUT,text=True)
            else:
                output = "Command not allowed"
        except subprocess.CalledProcessError as e:
            output = e.output
        except Exception as e:
            output = f"An error occurred: {e}"
    else:
        cmd = default_cmd

    try:
        if cmd in ALLOWED_COMMANDS:
            output = subprocess.check_output(ALLOWED_COMMANDS[cmd],stderr=subprocess.STDOUT,text=True)
        else:
            output = "Command not allowed"
    except subprocess.CalledProcessError as e:
        output = e.output
    except Exception as e:
        output = f"An error occurred: {e}"

    return render_template_string('system_monitor.html', output=output, user=user)

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

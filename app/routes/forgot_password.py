from flask import Blueprint, request, redirect, render_template, url_for

from app.database import get_db_connection
from .session import get_user

forgot_pass_bp = Blueprint('forgot_password', __name__)

@forgot_pass_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('forgot_password.html', error='Missing username or password')
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Check current password
                    cur.execute(
                        f"""
                        SELECT password FROM users WHERE username = '{username}'
                        """
                    )
                    c_password = cur.fetchone()[0]

                    if c_password == password:
                        return render_template('forgot_password.html', error='Password cannot be old password')
                    else:
                        cur.execute(
                            f"""
                            UPDATE users SET password = '{password}' WHERE username = '{username}'
                            """
                        )
                        conn.commit()

            return render_template('forgot_password.html', success='Password reset successfully.')

        except Exception as e:
            return render_template('forgot_password.html', error=e)

    return render_template('forgot_password.html')

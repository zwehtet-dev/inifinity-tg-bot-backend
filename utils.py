from flask import session, redirect, url_for

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__  # Ensure the function name is preserved
    return wrapper

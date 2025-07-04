from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import *
from utils import login_required

users_bp = Blueprint('users', __name__)

# User Table View with Pagination
@users_bp.route('/users')
@login_required
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # You can adjust this value as needed
    pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    return render_template(
        'users/index.html',
        users=users,
        pagination=pagination
    )

@users_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@users_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_or_edit_user(user_id=None):
    user = User.query.get(user_id) if user_id else None

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if user:  # Update existing user
            user.name = name
            user.email = email
            if password:  # Update password only if provided
                user.set_password(password)
        else:  # Create new user
            new_user = User(
                name=name,
                email=email,
            )
            new_user.set_password(password)
            db.session.add(new_user)

        db.session.commit()
        flash(f"User {'updated' if user else 'created'} successfully!", "success")
        return redirect(url_for('users.list_users'))

    return render_template(
        'users/form.html',
        user=user,
        action="Edit" if user else "Create",
        float=float,
    )



# User Delete View
@users_bp.route('/users/delete/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    try:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", "danger")

    return redirect(url_for('users.list_users'))

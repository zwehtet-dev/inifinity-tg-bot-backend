from flask import Blueprint, render_template, url_for, redirect, request, flash
from datetime import datetime
from models import db, Order, User, ThaiBankAccount, MyanmarBankAccount
from utils import login_required

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

def get_orders_by_type(order_type):
    return Order.query.filter_by(order_type=order_type).order_by(Order.created_at.desc()).all()

def get_order_by_id(order_id):
    return Order.query.get(order_id)

@orders_bp.route('/')
@login_required
def index():
    # Pagination parameters
    buy_page = request.args.get('buy_page', 1, type=int)
    sell_page = request.args.get('sell_page', 1, type=int)
    status = request.args.get('status', None)
    
    per_page = 10

    buy_orders_query = Order.query.filter_by(order_type="buy").order_by(Order.created_at.desc())
    sell_orders_query = Order.query.filter_by(order_type="sell").order_by(Order.created_at.desc())
    
    if status:
        buy_orders_query = buy_orders_query.filter_by(status=status)
        sell_orders_query = sell_orders_query.filter_by(status=status)

    buy_orders_pagination = buy_orders_query.paginate(page=buy_page, per_page=per_page, error_out=False)
    sell_orders_pagination = sell_orders_query.paginate(page=sell_page, per_page=per_page, error_out=False)
    
    new_buy_orders_count = buy_orders_query.filter_by(status="pending").count()
    new_sell_orders_count = sell_orders_query.filter_by(status="pending").count()

    return render_template(
        'orders/index.html',
        buy_orders=buy_orders_pagination.items,
        sell_orders=sell_orders_pagination.items,
        buy_orders_pagination=buy_orders_pagination,
        sell_orders_pagination=sell_orders_pagination,
        new_buy_orders_count=new_buy_orders_count,
        new_sell_orders_count=new_sell_orders_count
    )
    
@orders_bp.route('/api/list', methods=['GET'])
@login_required
def api_order_list():
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Order.query
    if status:
        query = query.filter_by(status=status)
    query = query.order_by(Order.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    orders = []
    for order in pagination.items:
        orders.append({
            'id': order.id,
            'order_id': order.order_id,
            'order_type': order.order_type,
            'amount': order.amount,
            'price': order.price,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'status': order.status,
            'user_id': order.user_id,
            'thai_bank_account_id': order.thai_bank_account_id,
            'myanmar_bank_account_id': order.myanmar_bank_account_id,
            'receipt': order.receipt,
            'confirm_receipt': order.confirm_receipt,
            'user_bank': order.user_bank,
            'qr': order.qr,
        })

    return {
        'orders': orders,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page
    }

@orders_bp.route('/<int:order_id>', methods=['GET', 'POST'])
@login_required
def view_order(order_id):
    order = get_order_by_id(order_id)
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for('orders.index'))

    if request.method == 'POST':
        # Update status
        if 'status' in request.form:
            new_status = request.form.get('status')
            if new_status in ['pending', 'approved', 'declined']:
                order.status = new_status
                db.session.commit()
                flash("Order status updated.", "success")
                return redirect(url_for('orders.view_order', order_id=order_id))
        if 'upload_confirm_receipt' in request.form and 'confirm_receipt' in request.files:
            file = request.files['confirm_receipt']
            if file and file.filename:
                # Save file logic here (implement as needed)
                # Example: save to static/uploads and update order.confirm_receipt
                filename = f"confirm_receipt_{order_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                filepath = f"static/uploads/{filename}"
                file.save(filepath)
                order.confirm_receipt = f"/{filepath}"
                db.session.commit()
                flash("Confirm_receipt uploaded.", "success")
                return redirect(url_for('orders.view_order', order_id=order_id))
        if 'upload_receipt' in request.form and 'receipt' in request.files:
            file = request.files['receipt']
            if file and file.filename:
                # Save file logic here (implement as needed)
                # Example: save to static/uploads and update order.receipt
                filename = f"receipt_{order_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                filepath = f"static/uploads/{filename}"
                file.save(filepath)
                order.receipt = f"/{filepath}"
                db.session.commit()
                flash("Receipt uploaded.", "success")
                return redirect(url_for('orders.view_order', order_id=order_id))

    return render_template('orders/form.html', order=order)

@orders_bp.route('/<int:order_id>/delete', methods=['POST'])    
@login_required
def delete_order(order_id):
    order = get_order_by_id(order_id)
    if not order:
        flash("Order not found.", "danger")
    else:
        db.session.delete(order)
        db.session.commit()
        flash("Order deleted.", "success")
    return redirect(url_for('orders.index'))

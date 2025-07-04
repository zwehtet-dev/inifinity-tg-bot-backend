from flask import Blueprint, render_template, request, redirect
from models import db, User, MaintenanceMode, ExchangeRate, AuthFeature, Order
from utils import login_required
import datetime
from sqlalchemy.sql import func
import requests
import os
from dotenv import load_dotenv

load_dotenv()
home_bp = Blueprint('home', __name__)
    

@home_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'GET':
        maintenance_mode = MaintenanceMode.query.first()
        if maintenance_mode:
            maintenance_status = maintenance_mode.on
        else:
            db.session.add(MaintenanceMode(on=False))
            db.session.commit()
            maintenance_status = False
            
        auth_feature = AuthFeature.query.first()
        if auth_feature:
            auth_feature = auth_feature.on
        else:
            db.session.add(AuthFeature(on=False))
            db.session.commit()
            auth_feature = False


        users_count = User.query.count()

        # Get the latest exchange rate
        exchange_rate = ExchangeRate.query.order_by(ExchangeRate.updated_at.desc()).first()
        
        pending_buy_orders = Order.query.filter_by(order_type='buy', status='pending').count()
        pending_sell_orders = Order.query.filter_by(order_type='sell', status='pending').count()

        return render_template(
            'home.html',
            users_count=users_count,
            maintenance_status=maintenance_status,
            auth_feature=auth_feature,
            exchange_rate=exchange_rate,
            pending_buy_orders=pending_buy_orders,
            pending_sell_orders=pending_sell_orders,
        )
    else:
        maintenance_status = True if request.form.get('maintenance_status') == 'true' else False
        maintenance_mode = MaintenanceMode.query.first()
        if maintenance_mode:
            maintenance_mode.on = maintenance_status
        else:
            maintenance_mode = MaintenanceMode(on=maintenance_status)

        auth_feature_status = True if request.form.get('auth_feature_status') == 'true' else False
        auth_feature = AuthFeature.query.first()
        if auth_feature:
            auth_feature.on = auth_feature_status
        else:
            auth_feature = AuthFeature(on=auth_feature_status)
        db.session.add(auth_feature)
        db.session.add(maintenance_mode)

        # Update or create exchange rates
        buy = request.form.get('buy')
        sell = request.form.get('sell')

        if buy and sell:
            exchange_rate = ExchangeRate.query.order_by(ExchangeRate.updated_at.desc()).first()
            if exchange_rate:
                exchange_rate.buy = float(buy)
                exchange_rate.sell = float(sell)
            else:
                exchange_rate = ExchangeRate(
                    buy=float(buy),
                    sell=float(sell),
                )
                db.session.add(exchange_rate)

        db.session.commit()
        return redirect('/dashboard')

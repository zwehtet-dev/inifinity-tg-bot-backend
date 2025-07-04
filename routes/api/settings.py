from flask import Blueprint, jsonify
from models import db, MaintenanceMode, AuthFeature, ExchangeRate

settings_bp = Blueprint('settings_bp', __name__, url_prefix='/api/settings')

@settings_bp.route('/', methods=['GET'])
def get_settings_status():
    maintenance = MaintenanceMode.query.first()
    auth_feature = AuthFeature.query.first()
    exchange_rate = ExchangeRate.query.order_by(ExchangeRate.updated_at.desc()).first()
    return jsonify({
        'maintenance_mode': maintenance.on if maintenance else False,
        'auth_feature': auth_feature.on if auth_feature else False,
        'buy': exchange_rate.buy if exchange_rate else None,
        'sell': exchange_rate.sell if exchange_rate else None,
    })
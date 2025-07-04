from flask import Blueprint, jsonify
from models import db, ThaiBankAccount, MyanmarBankAccount

banks_api = Blueprint('banks_api', __name__, url_prefix='/api/banks')

@banks_api.route('/thai', methods=['GET'])
def get_thai_banks():
    banks = ThaiBankAccount.query.filter_by(on=True).all()
    result = [
        {
            "id": bank.id,
            "bank_name": bank.bank_name,
            "account_number": bank.account_number,
            "account_name": bank.account_name,
            "qr_image": bank.qr_image,
            "user_id": bank.user_id
        }
        for bank in banks
    ]
    return jsonify(result), 200

@banks_api.route('/myanmar', methods=['GET'])
def get_myanmar_banks():
    banks = MyanmarBankAccount.query.filter_by(on=True).all()
    result = [
        {
            "id": bank.id,
            "bank_name": bank.bank_name,
            "account_number": bank.account_number,
            "account_name": bank.account_name,
            "qr_image": bank.qr_image,
            "user_id": bank.user_id
        }
        for bank in banks
    ]
    return jsonify(result), 200
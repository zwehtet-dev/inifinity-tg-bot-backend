from flask import Blueprint, jsonify, request
from models import db, ThaiBankAccount, MyanmarBankAccount
import logging

logger = logging.getLogger(__name__)

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
            "amount": bank.amount or 0.0,
            "display_name": bank.display_name,
            "on": bank.on
            # "user_id": bank.user_id
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
            "amount": bank.amount or 0.0,
            "display_name": bank.display_name,
            "on": bank.on
            # "user_id": bank.user_id
        }
        for bank in banks
    ]
    return jsonify(result), 200

@banks_api.route('/balances', methods=['GET'])
def get_bank_balances():
    """
    Get current balances for all bank accounts.
    
    Returns:
        Dict mapping bank names to current balances
    """
    balances = {}
    
    # Get all Thai banks
    thai_banks = ThaiBankAccount.query.all()
    for bank in thai_banks:
        balances[bank.bank_name] = bank.amount or 0.0
    
    # Get all Myanmar banks
    myanmar_banks = MyanmarBankAccount.query.all()
    for bank in myanmar_banks:
        balances[bank.bank_name] = bank.amount or 0.0
    
    return jsonify(balances), 200

@banks_api.route('/update-balance', methods=['POST'])
def update_bank_balance():
    """
    Update bank balances after order completion.
    
    Request body:
    {
        "order_id": "251225A0001B",
        "order_type": "buy",
        "thai_bank_id": 1,
        "thai_amount_change": 1000.0,
        "myanmar_bank_id": 2,
        "myanmar_amount_change": -125000.0
    }
    
    Returns:
        Success message with updated balances
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        order_id = data.get('order_id')
        order_type = data.get('order_type')
        thai_bank_id = data.get('thai_bank_id')
        thai_amount_change = data.get('thai_amount_change', 0)
        myanmar_bank_id = data.get('myanmar_bank_id')
        myanmar_amount_change = data.get('myanmar_amount_change', 0)
        
        logger.info(
            f"Updating bank balances for order {order_id}: "
            f"Thai bank {thai_bank_id} {thai_amount_change:+.2f}, "
            f"Myanmar bank {myanmar_bank_id} {myanmar_amount_change:+.2f}"
        )
        
        updated_banks = []
        
        # Update Thai bank balance
        if thai_bank_id and thai_amount_change != 0:
            thai_bank = ThaiBankAccount.query.get(thai_bank_id)
            if thai_bank:
                old_balance = thai_bank.amount or 0.0
                thai_bank.amount = old_balance + thai_amount_change
                updated_banks.append({
                    "bank_name": thai_bank.bank_name,
                    "old_balance": old_balance,
                    "change": thai_amount_change,
                    "new_balance": thai_bank.amount
                })
                logger.info(
                    f"Thai bank {thai_bank.bank_name}: "
                    f"{old_balance:.2f} + {thai_amount_change:+.2f} = {thai_bank.amount:.2f}"
                )
            else:
                logger.warning(f"Thai bank ID {thai_bank_id} not found")
        
        # Update Myanmar bank balance
        if myanmar_bank_id and myanmar_amount_change != 0:
            myanmar_bank = MyanmarBankAccount.query.get(myanmar_bank_id)
            if myanmar_bank:
                old_balance = myanmar_bank.amount or 0.0
                myanmar_bank.amount = old_balance + myanmar_amount_change
                updated_banks.append({
                    "bank_name": myanmar_bank.bank_name,
                    "old_balance": old_balance,
                    "change": myanmar_amount_change,
                    "new_balance": myanmar_bank.amount
                })
                logger.info(
                    f"Myanmar bank {myanmar_bank.bank_name}: "
                    f"{old_balance:.2f} + {myanmar_amount_change:+.2f} = {myanmar_bank.amount:.2f}"
                )
            else:
                logger.warning(f"Myanmar bank ID {myanmar_bank_id} not found")
        
        # Commit changes
        db.session.commit()
        
        logger.info(f"✅ Bank balances updated successfully for order {order_id}")
        
        return jsonify({
            "message": "Bank balances updated successfully",
            "order_id": order_id,
            "order_type": order_type,
            "updated_banks": updated_banks
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating bank balances: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
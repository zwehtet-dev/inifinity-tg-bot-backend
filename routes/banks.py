from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, ThaiBankAccount, MyanmarBankAccount
from utils import login_required

banks_bp = Blueprint('banks', __name__)

# --- Thai Bank Accounts ---


@banks_bp.route('/banks/thai', methods=['GET', 'POST'])
@login_required
def thai_banks():
    if request.method == 'POST':
        # Update 'on' status for each bank
        banks = ThaiBankAccount.query.all()
        for bank in banks:
            # Checkbox for 'on' status: present in form if checked
            bank_on = request.form.get(f'on_{bank.id}') == 'on'
            bank.on = bank_on
        db.session.commit()
        flash('Bank statuses updated!', 'success')
        return redirect(url_for('banks.thai_banks'))
    banks = ThaiBankAccount.query.all()
    return render_template('banks/thai_list.html', banks=banks)


@banks_bp.route('/banks/thai/create', methods=['GET', 'POST'])
@login_required
def create_thai_bank():
    if request.method == 'POST':
        bank = ThaiBankAccount(
            bank_name=request.form['bank_name'],
            account_number=request.form['account_number'],
            account_name=request.form['account_name'],
            qr_image=request.form.get('qr_image'),
            user_id=int(request.form.get('user_id'))
        )
        db.session.add(bank)
        db.session.commit()
        flash('Thai bank account created!', 'success')
        return redirect(url_for('banks.thai_banks'))
    return render_template('banks/thai_form.html', action='Create', bank=None)


@banks_bp.route('/banks/thai/<int:bank_id>/edit', methods=['GET', 'POST'])
def edit_thai_bank(bank_id):
    bank = ThaiBankAccount.query.get_or_404(bank_id)
    if request.method == 'POST':
        bank.bank_name = request.form['bank_name']
        bank.account_number = request.form['account_number']
        bank.account_name = request.form['account_name']
        bank.qr_image = request.form.get('qr_image')
        bank.user_id = int(request.form.get('user_id'))
        db.session.commit()
        flash('Thai bank account updated!', 'success')
        return redirect(url_for('banks.thai_banks'))
    return render_template('banks/thai_form.html', action='Edit', bank=bank)


@banks_bp.route('/banks/thai/<int:bank_id>/delete', methods=['POST'])
def delete_thai_bank(bank_id):
    bank = ThaiBankAccount.query.get_or_404(bank_id)
    db.session.delete(bank)
    db.session.commit()
    flash('Thai bank account deleted!', 'success')
    return redirect(url_for('banks.thai_banks'))

# --- Myanmar Bank Accounts ---


@banks_bp.route('/banks/myanmar', methods=['GET', 'POST'])
def myanmar_banks():
    if request.method == 'POST':
        banks = MyanmarBankAccount.query.all()
        for bank in banks:
            bank_on = request.form.get(f'on_{bank.id}') == 'on'
            bank.on = bank_on
        db.session.commit()
        flash('Bank statuses updated!', 'success')
        return redirect(url_for('banks.myanmar_banks'))
    banks = MyanmarBankAccount.query.all()
    return render_template('banks/myanmar_list.html', banks=banks)


@banks_bp.route('/banks/myanmar/create', methods=['GET', 'POST'])
def create_myanmar_bank():
    if request.method == 'POST':
        bank = MyanmarBankAccount(
            bank_name=request.form['bank_name'],
            account_number=request.form['account_number'],
            account_name=request.form['account_name'],
            qr_image=request.form.get('qr_image'),
            user_id=request.form.get('user_id')
        )
        db.session.add(bank)
        db.session.commit()
        flash('Myanmar bank account created!', 'success')
        return redirect(url_for('banks.myanmar_banks'))
    return render_template('banks/myanmar_form.html', action='Create', bank=None)


@banks_bp.route('/banks/myanmar/<int:bank_id>/edit', methods=['GET', 'POST'])
def edit_myanmar_bank(bank_id):
    bank = MyanmarBankAccount.query.get_or_404(bank_id)
    if request.method == 'POST':
        bank.bank_name = request.form['bank_name']
        bank.account_number = request.form['account_number']
        bank.account_name = request.form['account_name']
        bank.qr_image = request.form.get('qr_image')
        bank.user_id = request.form.get('user_id')
        db.session.commit()
        flash('Myanmar bank account updated!', 'success')
        return redirect(url_for('banks.myanmar_banks'))
    return render_template('banks/myanmar_form.html', action='Edit', bank=bank)


@banks_bp.route('/banks/myanmar/<int:bank_id>/delete', methods=['POST'])
def delete_myanmar_bank(bank_id):
    bank = MyanmarBankAccount.query.get_or_404(bank_id)
    db.session.delete(bank)
    db.session.commit()
    flash('Myanmar bank account deleted!', 'success')
    return redirect(url_for('banks.myanmar_banks'))

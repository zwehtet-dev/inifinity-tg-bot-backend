from models import db, Message, TelegramID
from app import app

with app.app_context():
    Message.query.delete()
    TelegramID.query.delete()
    db.session.commit()
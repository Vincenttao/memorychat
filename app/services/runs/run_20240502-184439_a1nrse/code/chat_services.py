from datetime import datetime

from app.models.models import Message, User


class MessageService:
    @staticmethod
    def add_message(user_id, sender, message_type, content):
        user = User.objects(user_id=user_id).first()
        if user is None:
            raise ValueError("User does not exist")
        message = Message(user_id=user_id, sender=sender, message_type=message_type, content=content,
                          timestamp=datetime.now())
        message.save()
        return message

    @staticmethod
    def retrieve_message(user_id):
        user = User.objects(user_id=user_id).first()
        if user is None:
            raise ValueError("User does not exist")
        message = Message.objects(user_id=user_id).first()
        return message

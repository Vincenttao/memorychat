from datetime import datetime

from mongoengine import Document, StringField, ReferenceField, DateTimeField, ListField, DictField


class User(Document):
    user_id = StringField(primary_key=True)
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    phone_no = StringField(required=True)
    # 可以加入更多的用户信息字段


class Photo(Document):
    user_id = ReferenceField(User, required=True)
    image_url = StringField(required=True)  # 存储图片的 URL
    upload_date = DateTimeField(default=datetime.now)
    description = StringField()
    title = StringField()


class Story(Document):
    user_id = ReferenceField(User, required=True)
    title = StringField()
    created_at = DateTimeField(default=datetime.now)
    summary = StringField()
    story_date = StringField()
    related_photos = ListField(ReferenceField(Photo))


class MemoryBookEntry(Document):
    user_id = ReferenceField(User, required=True)
    title = StringField(required=True)
    content = StringField(required=True)
    date = DateTimeField(default=datetime.now)
    related_photos = ListField(ReferenceField(Photo))


class UserProfile(Document):
    user_id = ReferenceField(User, required=True)
    preferences = DictField()
    behavior_log = ListField(StringField())


class CognitiveActivity(Document):
    user_id = ReferenceField(User, required=True)
    activity_type = StringField(required=True)
    results = DictField()
    date = DateTimeField(default=datetime.now)


# 修改为按照photo.id关联
class Message(Document):
    user_id = ReferenceField(User, required=True)
    sender = StringField(required=True, default="user", choices=["user", "assistant"])  # 用户发送或系统发送
    message_type = StringField(required=True, default="text", choices=["text", "image", "audio"])  # 消息类型
    content = StringField(required=True)  # 文本内容或文件的URL
    timestamp = DateTimeField(required=True)
    related_photo_id = ReferenceField(Photo)
    related_story_id = ReferenceField(Story)

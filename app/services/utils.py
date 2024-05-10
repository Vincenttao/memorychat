import datetime
import sys

from mongoengine import Q
import random
from loguru import logger

logger.add(sys.stdout, level="DEBUG")


class MessageService:
    def __init__(self, user_model, message_model):
        self.user_model = user_model
        self.message_model = message_model

    def add_message(self, user_id, sender, message_type, content, related_story_id=None, related_photo_id=None):
        user = self.user_model.objects(user_id=user_id).first()
        if user is None:
            raise ValueError("User does not exist")
        message = self.message_model(user_id=user_id,
                                     sender=sender,
                                     message_type=message_type,
                                     content=content,
                                     related_story_id=related_story_id,
                                     related_photo_id=related_photo_id,
                                     timestamp=datetime.datetime.now())
        message.save()
        return message

    def retrieve_story_message(self, user_id, related_story_id=None, start_time=None, end_time=None):
        user = self.user_model.objects(user_id=user_id).first()
        if user is None:
            raise ValueError("User does not exist")

        now = datetime.datetime.now()
        if start_time is None:
            start_time = datetime.datetime.min
        if end_time is None:
            end_time = now
        query = Q(user_id=user)
        if related_story_id is not None:
            query &= Q(related_story_id=related_story_id)
        query &= Q(timestamp__gte=start_time) & Q(timestamp__lte=end_time)
        messages = self.message_model.objects(query).order_by('timestamp')
        return messages

    def retrieve_photo_message(self, user_id, related_photo_id, start_time=None, end_time=None, limit=10):
        # 检查用户是否存在
        user = self.user_model.objects(user_id=user_id).first()
        if user is None:
            raise ValueError("User does not exist")

        # 设置查询的时间范围
        now = datetime.datetime.now()
        if start_time is None:
            start_time = datetime.datetime.min
        if end_time is None:
            end_time = now

        # 构建查询条件
        query = Q(user_id=user_id)
        if related_photo_id is not None:
            query &= Q(related_photo_id=related_photo_id)
        query &= Q(timestamp__gte=start_time) & Q(timestamp__lte=end_time)
        logger.info(f"查询条件如下：{query}")

        # 查询并按时间戳排序返回消息
        messages = self.message_model.objects(query).order_by('-timestamp').limit(limit)
        logger.info(f"查询结果如下：{messages}")
        return messages


# TODO 补充完毕photo管理
class PhotoManagement:
    def __init__(self, user_model, photo_model):
        self.user_model = user_model
        self.photo_model = photo_model

    def upload_photo(self, user_id, image_url, upload_date=None, description=None):
        user = self.user_model.objects(user_id=user_id).first()
        if user is None:
            raise ValueError("User does not exist")
        photo = self.photo_model(user_id=user_id, image_url=image_url,
                                 upload_date=upload_date or datetime.datetime.now(), description=description)
        photo.save()
        return photo

    def retrieve_photo(self, photo_id):
        return self.photo_model.objects(id=photo_id).first()

    def delete_photo(self, photo_id):
        photo = self.photo_model.objects(id=photo_id).first()
        if photo:
            photo.delete()

    def retrieve_photo_paginated(self, user_id, page=1, per_page=10):
        # 使用paginate方法提供内置的分页功能，过滤特定用户的照片
        user = self.user_model.objects(user_id=user_id).first()
        if not user:
            raise ValueError("No such user exists")

        skip_count = (page - 1) * per_page

        photos = self.photo_model.objects(user_id=user).order_by('-upload_date').skip(skip_count).limit(per_page)

        return photos


class StoryManagement:
    def __init__(self, user_model, photo_model, story_model):
        self.user_model = user_model
        self.photo_model = photo_model
        self.story_model = story_model

    def create_story(self, user_id, title, summary, story_date, related_photos):
        user = self.user_model.objects(user_id=user_id).first()
        if user is None:
            raise ValueError("User does not exist")
        story = self.story_model(user_id=user_id,
                                 title=title,
                                 summary=summary,
                                 story_date=story_date,
                                 related_photos=related_photos)
        story.save()
        return story

    def edit_story(self, story_id, summary=None, story_date=None, title=None):
        story = self.story_model.objects(id=story_id).first()
        if story is None:
            raise ValueError("Story does not exist")
        if summary:
            story.summary = summary
        if story_date:
            story.story_date = story_date
        if title:
            story.title = title
        story.save()
        return story

    def retrieve_story(self, story_id):
        return self.story_model.objects(id=story_id).first()

    def retrieve_recent_stories(self, page_number=1, page_size=5):
        # 跳过已经拉取过的故事，并按创建时间降序排序
        skip_count = (page_number - 1) * page_size
        stories = self.story_model.objects.order_by('-created_at').skip(skip_count).limit(page_size)
        return stories

    def retrieve_random_story(self):
        # 随机获取一个故事
        count = self.story_model.objects.count()
        if count == 0:
            return None
        random_index = random.randint(0, count - 1)
        story = self.story_model.objects[random_index]
        return story


class MemoryBook:
    pass


class UserManagement:
    def __init__(self, user_model):
        self.user_model = user_model

    def add(self, user_id, username, password, phone_no):
        user = self.user_model(user_id=user_id, username=username, password=password, phone_no=phone_no)
        user.save()
        return user

    def login(self, username, password):
        user = self.user_model.objects(username=username, password=password).first()
        if user is None:
            raise ValueError("Invalid username or password")
        return user

    def update_profile(self, user_id, new_username=None, new_password=None, new_phone_no=None):
        user = self.user_model.objects(user_id=user_id).first()
        if user is None:
            raise ValueError("User does not exist")
        if new_username:
            user.username = new_username
        if new_password:
            user.password = new_password
        if new_phone_no:
            user.phone_no = new_phone_no
        user.save()
        return user

    def delete_user(self, user_id):
        user = self.user_model.objects(user_id=user_id).first()
        if user:
            user.delete()

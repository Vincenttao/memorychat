import datetime
from mongoengine import Q

class MessageService:
    def __init__(self, user_model, message_model):
        self.user_model = user_model
        self.message_model = message_model

    def add_message(self, user_id, sender, message_type, content, related_story = None):
        user = self.user_model.objects(user_id=user_id).first()
        if user is None:
            raise ValueError("User does not exist")
        message = self.message_model(user_id=user_id,
                                     sender=sender,
                                     message_type=message_type,
                                     content=content,
                                     related_story=related_story,
                                     timestamp=datetime.datetime.now())
        message.save()
        return message

    def retrieve_message(self, user_id, related_story=None, start_time=None, end_time=None):
        user = self.user_model.objects(user_id=user_id).first()
        if user is None:
            raise ValueError("User does not exist")

        now = datetime.datetime.now()
        if start_time is None:
            start_time = datetime.datetime.min
        if end_time is None:
            end_time = now
        query = Q(user_id=user)
        if related_story is not None:
            query &= Q(related_story=related_story)
        query &= Q(timestamp__gte=start_time) & Q(timestamp__lte=end_time)
        messages = self.message_model.objects(query).order_by('timestamp')
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


class StoryGenerator:
    def __init__(self, user_model, photo_model, story_model):
        self.user_model = user_model
        self.photo_model = photo_model
        self.story_model = story_model

    def create_story(self, user_id, content, date, related_photos):
        user = self.user_model.objects(user_id=user_id).first()
        if user is None:
            raise ValueError("User does not exist")
        story = self.story_model(user_id=user_id, content=content, date=date, related_photos=related_photos)
        story.save()
        return story

    def edit_story(self, story_id, content=None, date=None, related_photos=None):
        story = self.story_model.objects(id=story_id).first()
        if story is None:
            raise ValueError("Story does not exist")
        if content:
            story.content = content
        if date:
            story.date = date
        if related_photos:
            story.related_photos = related_photos
        story.save()
        return story

    def retrieve_story(self, story_id):
        return self.story_model.objects(id=story_id).first()


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

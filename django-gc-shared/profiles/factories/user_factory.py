# -*- coding: utf-8 -*-
import factory
from faker import Factory
from profiles.models import User, UserProfile
from datetime import datetime

fake = Factory.create()
fake_ru = Factory.create('ru_RU')
default_user_password = '123456Aa'


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda o: fake.user_name())
    first_name = factory.LazyAttribute(lambda o: fake_ru.first_name())
    last_name = factory.LazyAttribute(lambda o: fake_ru.last_name())
    email = factory.LazyAttribute(lambda o: fake.safe_email())
    password = factory.PostGenerationMethodCall('set_password',
                                                default_user_password)
    is_staff = False


class StaffFactory(UserFactory):

    is_staff = True


class UserProfileFactory(factory.DjangoModelFactory):
    pass

    class Meta:
        model = UserProfile

    user = UserFactory()
    middle_name = "Тестович"
    birthday = factory.LazyAttribute(lambda o: fake.birthday())
    country = None
    city = None
    state = None
    address = "Московский 105"
    skype = user.username
    icq = None
    phone_home = factory.LazyAttribute(lambda o: fake_ru.phonenumber())
    phone_work = None
    phone_mobile = None
    avatar = None
    social_security = None
    tin = None
    manager = None
    manager_auto_assigned = False
    assigned_to_current_manager_at = None
    language = "ru"
    agent_code = None
    lost_otp = False
    auth_scheme = None
    params = None
    user_from = None
    registered_from = "test"
    last_activity_ts = datetime.now()
    last_activities = []
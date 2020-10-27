from django.db import transaction
from django.db.models import Q

from base import errors
from base import controllers as base_ctl
from account.models import UserModel


def login(username, password, is_ldap=False):
    '''
    登录
    '''
    base_query = UserModel.objects.filter(username=username)
    if is_ldap:
        base_query = base_query.filter(typ=UserModel.TYP_LDAP)
    obj = base_query.first()
    if not obj:
        raise errors.CommonError('用户名或密码错误')
    if not obj.check_password(password):
        raise errors.CommonError('用户名或密码错误')
    if obj.status == UserModel.ST_FORBIDDEN:
        raise errors.CommonError('用户已被禁止登录')
    data = {
        'token': obj.gen_token(),
    }
    return data


def create_user(username, password, name=None, phone=None, email=None, operator=None):
    '''
    创建用户
    '''
    user_obj = UserModel.objects.filter(username=username).first()
    if user_obj:
        raise errors.CommonError('用户已存在')
    data = {
        'username': username,
        'name': name,
        'phone': phone,
        'email': email,
    }
    with transaction.atomic():
        user_obj = base_ctl.create_obj(UserModel, data, operator)
        if not password:
            password = '123456'
        user_obj.set_password(password)
    data = user_obj.to_dict()
    return data
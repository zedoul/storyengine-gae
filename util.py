# coding: utf-8
from google.appengine.api import users
from django.shortcuts import render_to_response
from settings import STATIC_PATH

def err_page(err_msg):
    user_info = users.get_current_user()
    context = {'static_path': STATIC_PATH,
               'user_info' : user_info,
               'err_msg': err_msg}
    return render_to_response('err_page.html', context)  
# coding: utf-8
import os
import webapp2
from webapp2_extras import sessions
from django.http import HttpResponse

import logging
from settings import STATIC_PATH
from settings import TEMPLATE_DIR
from defines import APP_TITLE
from google.appengine.ext.webapp import template

import storyengine
import storyengine.model
from storyengine.model.account import Account

class IndexHandler(storyengine.SessionHandler):
	def get(self):
		dic = self.request.cookies
		user_info = self.session.get('accountid')
		passed = None
		if None is not user_info:
			account = Account.get_by_accountid(user_info)
			if None is not account and  1 == account.mod :
				passed = True
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'accountid' : user_info,
			'passed':passed,
			'shops': None,
			'blogs': None}
		path = os.path.join(TEMPLATE_DIR, "index.html")
		self.response.out.write(template.render(path, context))


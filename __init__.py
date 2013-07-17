# coding: utf-8
'''
#http://stackoverflow.com/questions/12737008/google-app-engine-session-works-in-localhost-but-fails-when-deployed
'''

__author__ = 'Seonghyun Kim'

import os
import webapp2
from webapp2_extras import sessions

import logging
from settings import STATIC_PATH
from settings import TEMPLATE_DIR
from google.appengine.ext.webapp import template
from django.http import HttpResponse
from django.template import Context, loader

class SessionHandler(webapp2.RequestHandler):
	def dispatch(self):
# Get a session store for this request.
		self.session_store = sessions.get_store(request=self.request)
		try:
# Dispatch the request.
			webapp2.RequestHandler.dispatch(self)
		finally:
# Save all sessions.
			self.session_store.save_sessions(self.response)
	@webapp2.cached_property
	def session(self):
# Returns a session using the default cookie key.
		return self.session_store.get_session()

	def render_to_response(self, tmpl, data):
		t = loader.get_template(tmpl)
		c = Context(data)
		self.response.out.write(t.render(c))


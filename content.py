## coding: utf-8
import os
import webapp2
from webapp2_extras import sessions
#http://stackoverflow.com/questions/12737008/google-app-engine-session-works-in-localhost-but-fails-when-deployed
import logging, string
from settings import STATIC_PATH
from settings import TEMPLATE_DIR
from google.appengine.ext.webapp import template
from storyengine.model.account import Account
from storyengine.model.content import Content
from defines import APP_TITLE
#from django import forms
from django import forms
#from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponse
from django.template import Context, loader
import json
import storyengine
import storyengine.model
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from settings import CONTENT_PART_NAME
from settings import CONTENT_PART_CHOICES
from django.utils.translation import ugettext_lazy

class ContentInfoForm(storyengine.model.TransForm):
	nameen = forms.CharField(label=ugettext_lazy('contentnameen'),
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	nameko = forms.CharField(label=ugettext_lazy('contentnameko'),
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	nameja = forms.CharField(label=ugettext_lazy('contentnameja'),
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))

	part = forms.ChoiceField(label=CONTENT_PART_NAME,
		choices=CONTENT_PART_CHOICES,
		widget=forms.Select(attrs={'onchange':'get_vehicle_color();'}))
	photo = forms.Field(label=ugettext_lazy('photo'),
		widget=forms.FileInput,
		required=False)
	thumbnail = forms.Field(label=ugettext_lazy('thumbnail'),
		widget=forms.FileInput,
		required=False)

class ContentSearchForm(forms.Form):
	contentid = forms.CharField(label='ID',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	nameen = forms.CharField(label='name (en)',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))

class ContentIndexHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		mode = self.request.get('mode')
		keytodel = self.request.get('del')
		contents = None
		if 'all' == mode:
			contents = Content.all().order('-created')
		elif 'less' == mode:
			contents = Content.all().order('-created').fetch(limit=5)
		else:
			contents = []
		contentlist = []
		for content in contents:
			content.keyid = str(content.key().id())
			contentlist.append(content)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'size':len(contentlist),
			'keytodel':keytodel,
			'contents':contentlist}
		self.render_to_response('content_index.html',context)

class ContentSearchHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		s_form = ContentSearchForm(None)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		result = None
		contentid = self.request.get('contentid')
		nameen = self.request.get('nameen')

		if contentid != "":
			result = Content.get_by_id(int(contentid))
		else:
			result = Content.all().filter("nameen =",nameen)

		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'contents':result,
		}
		self.render_to_response('content_search.html',context)

class ContentNewHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		s_form = ContentInfoForm(None)
		posturl = blobstore.create_upload_url('/upload')
		del s_form.fields['descriptionen']
		del s_form.fields['descriptionko']
		del s_form.fields['descriptionja']
		del s_form.fields['index']
		del s_form.fields['visible']
		del s_form.fields['price']
		del s_form.fields['expiration_days']
		del s_form.fields['expiration_mins']
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'posturl':posturl,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self): #logout
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		content = Content.new(account)
		params = {}
		for key in self.request.arguments():
			params[key] = self.request.get(key)
		content.setter(params)
		self.redirect('/content')

class ContentReadHandler(storyengine.SessionHandler):
	def get(self,keyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		content = Content.get_by_id(int(keyid))
		pagelinks = content.pages
		pagelist = []

		for pagelink in pagelinks:
			pagelink.page.keyid = pagelink.page.key().id()
			pagelink.page.story.keyid = pagelink.page.story.key().id()
			pagelist.append(pagelink.page)

		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'content':content,
			'pages':pagelist,
			'keyid':content.key().id()}
		self.render_to_response('content_read.html',context)

class ContentUpdateHandler(storyengine.SessionHandler):
	def get(self,contentid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		content = Content.get_by_id(int(contentid))
		f_data = content.to_formdict()
		s_form = ContentInfoForm(f_data)
		del s_form.fields['descriptionen']
		del s_form.fields['descriptionko']
		del s_form.fields['descriptionja']
		del s_form.fields['price']
		del s_form.fields['expiration_days']
		del s_form.fields['expiration_mins']
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self,contentid): #logout
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		content = Content.get_by_id(int(contentid))
		params = {}
		for key in self.request.arguments():
			params[key] = self.request.get(key)
		content.setter(params)
		self.redirect('/content')

class ContentDelHandler(storyengine.SessionHandler):
	def get(self,contentid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		content = Content.get_by_id(int(contentid))
		content.delete()
		self.redirect('/content')

class ContentPhotoHandler(webapp.RequestHandler):
	def get(self):
		keyid = self.request.get("img_id")
		content = Content.get_by_id(int(keyid))
		if content.photo:
			self.response.headers['Content-Type'] = "image/jpg"
			self.response.out.write(images.resize(content.photo,484,481))
		else:
			self.response.out.write("no image")

class ContentThumbnailHandler(webapp.RequestHandler):
	def get(self):
		keyid = self.request.get("img_id")
		content = Content.get_by_id(int(keyid))
		if content.thumbnail:
			self.response.headers['Content-Type'] = "image/jpg"
			self.response.out.write(images.resize(content.thumbnail,175,84))
		else:
			self.response.out.write("no image")

class AppContentReadHandler(webapp2.RequestHandler):
	def get(self,keyid):
		self.response.headers['Content-Type'] = 'application/json'
		lang = self.request.get('lang')
		tostudy = self.request.get('tostudy')
		if None == tostudy:
			tostudy = ""
		ret = Content.api_read(keyid,lang,tostudy)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(ret))


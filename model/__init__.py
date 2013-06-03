# -*- coding: utf-8  
from google.appengine.ext import db
from google.appengine.api import images
from django import forms
import webapp2
from google.appengine.api import memcache
import time
import datetime
import json
from defines import STORYENGINE_LANGS

__author__ = 'Seonghyun Kim'

class SerializableModel(db.Model):
	def to_json(self):
		return None

class LoggableModel(SerializableModel):
	created = db.DateTimeProperty(auto_now_add=True)
	modified = db.DateTimeProperty(auto_now=True)

class ReceiptModel(LoggableModel):
	receipt_type = db.CategoryProperty(choices=set([
				'candy',
				'money',
				'data',
#				'play',
				'gift']),required=True)
	before = db.IntegerProperty(required=True)
	cost = db.IntegerProperty(required=True)
	after = db.IntegerProperty(required=True)
	dataID = db.IntegerProperty(default=0)
	receipt_hash = db.StringProperty()

class MemcachedModel(LoggableModel):
	def cache_get (self,postfix=""):
		jsonstr = memcache.get(self.memcache_key(postfix))
		if None is not jsonstr:
			return json.loads(jsonstr)
		else:
			return None

	def cache_set (self, data, seconds, postfix=""):
		assert(None is not data)
		assert(seconds > 0)
		dic = memcache.add(self.memcache_key(postfix),json.dumps(data),time=int(seconds))

	def memcache_key(cls,postfix=""):
		return 'M_' + str(cls.key().id_or_name()) + '_C_' + postfix

	@classmethod
	def get_or_insert(cls, key_name, **kwds):
		obj = super(MemcachedModel, cls).get_or_insert(key_name, **kwds)
		memcache.delete(cls.memcache_key())
		for lang in STORYENGINE_LANGS:
			memcache.delete(cls.memcache_key(lang))
		return obj

	def delete(self):
		super(MemcachedModel, self).delete()
		memcache.delete(self.memcache_key())
		for lang in STORYENGINE_LANGS:
			memcache.delete(self.memcache_key(lang))

	def put(self):
		key = super(MemcachedModel, self).put()
		memcache.delete(self.memcache_key())
		for lang in STORYENGINE_LANGS:
			memcache.delete(self.memcache_key(lang))
		return key

class LinkModel (LoggableModel):
	score = db.IntegerProperty(default=0)
	link_type = db.CategoryProperty(choices=set(['accountcategory','accountstory','accountpage','accountcontent']),
			required=True)

class AccountModel(LoggableModel):
	name = db.StringProperty(required=True)
	description = db.StringProperty()
	access_token = db.StringProperty(required=True)
	expiration_date = db.DateTimeProperty(required=True)
	mod = db.IntegerProperty(default=0)
	thumbnail = db.BlobProperty()

class ContentModel (MemcachedModel):
	version = db.IntegerProperty(default=1)
	visible = db.IntegerProperty(default=1)
	group = db.ReferenceProperty(AccountModel,
			collection_name='groupowns',
			required=False)
	creator = db.ReferenceProperty(AccountModel,
			collection_name='createds',
			required=True)
	index = db.IntegerProperty(default=0)
	price = db.IntegerProperty(default=0)
	content_type = db.CategoryProperty(choices=set(['category','story','page','content']),
				required=True)
	expiration_days = db.IntegerProperty(default=0)
	expiration_mins = db.IntegerProperty(default=0)

'''
	support : determine it can use for
'''	
class TransModel (ContentModel):
	nameen = db.StringProperty(default="")
	nameko = db.StringProperty(default="")
	nameja = db.StringProperty(default="")
	descriptionen = db.TextProperty(default="")
	descriptionko = db.TextProperty(default="")
	descriptionja = db.TextProperty(default="")
	supportlangen = db.BooleanProperty(default=False)
	supportlangko = db.BooleanProperty(default=False)
	supportlangja = db.BooleanProperty(default=False)
	supporttostudyen = db.BooleanProperty(default=False)
	supporttostudyko = db.BooleanProperty(default=False)
	supporttostudyja = db.BooleanProperty(default=False)

	def support_lang(self,lang_):
		if 'en' == lang_:
			if True == self.supportlangen:
				return True
		elif 'ja' == lang_:
			if True == self.supportlangja:
				return True
		elif 'ko' == lang_:
			if True == self.supportlangko:
				return True
		else:
			assert(0)
		return False

	def support_lang_add(self,lang_):
		if 'en' == lang_:
			self.supportlangen = True
		elif 'ja' == lang_:
			self.supportlangja = True
		elif 'ko' == lang_:
			self.supportlangko = True
		else:
			assert(0)
		return False

	def support_lang_del(self,lang_):
		if 'en' == lang_:
			self.supportlangen = False
		elif 'ja' == lang_:
			self.supportlangja = False
		elif 'ko' == lang_:
			self.supportlangko = False
		else:
			assert(0)
		return False

	def support_tostudy(self,lang_):
		if 'en' == lang_:
			if True == self.supporttostudyen:
				return True
		elif 'ja' == lang_:
			if True == self.supporttostudyja:
				return True
		elif 'ko' == lang_:
			if True == self.supporttostudyko:
				return True
		else:
			assert(0)
		return False

	def support_tostudy_add(self,lang_):
		if 'en' == lang_:
			self.supporttostudyen = True
		elif 'ja' == lang_:
			self.supporttostudyja = True
		elif 'ko' == lang_:
			self.supporttostudyko = True
		else:
			assert(0)
		return False

	def support_tostudy_del(self,lang_):
		if 'en' == lang_:
			self.supporttostudyen = False
		elif 'ja' == lang_:
			self.supporttostudyja = False
		elif 'ko' == lang_:
			self.supporttostudyko = False
		else:
			assert(0)
		return False

	def setter(self,params):
		keys = params.keys()
		if ((False == ('index' in params)) or "" == params['index']):
			self.index = 0
		else:
			self.index = int(params['index'])
		if ((False == ('visible' in params)) or "" == params['visible']):
			self.visible = 0
		else:
			self.visible = int(params['visible'])
		if ((False == ('price' in params)) or "" == params['price']):
			self.price = 0
		else:
			self.price = int(params['price'])
		if ((False == ('expiration_days' in params)) or "" == params['expiration_days']):
			self.expiration_days = 0
		else:
			self.expiration_days = int(params['expiration_days'])
		if ((False == ('expiration_mins' in params)) or "" == params['expiration_mins']):
			self.expiration_mins = 0
		else:
			self.expiration_mins = int(params['expiration_mins'])
		for lang in STORYENGINE_LANGS:
			if ('name'+lang) in keys:
				target = params[('name'+lang)]
				exec 'self.name'+lang+'= target'
			if ('description'+lang) in keys:
				target = params[('description'+lang)]
				exec 'self.description'+lang+'= target'
		self.version = self.version + 1
		self.put()

	def to_dict(self,keyid,lang_,langonly_=False):
		f_data = {}
		f_data['id'] = str(keyid)
		if self.visible == 0:
			f_data['visible']=0
			return f_data
		assert(lang_)
		f_data['lang'] = lang_

		for lang in STORYENGINE_LANGS:
			if lang == lang_:
				exec 'f_data["name"] = self.name'+lang
				exec 'f_data["description"] = self.description'+lang
		if True == langonly_:
			return f_data
		f_data['visible'] = self.visible
		f_data['index'] = str(self.index)
		f_data['version'] = self.version
		f_data['price'] = self.price
		if f_data['name'] == None:
			f_data['name'] = ""
		if f_data['description'] == None:
			f_data['description'] = ""
		obj = datetime.datetime.now()
		obj = obj + datetime.timedelta(days=self.expiration_days)
		obj = obj + datetime.timedelta(minutes=self.expiration_mins)
		return f_data

	def to_formdict(self):
		f_data = {}
		f_data['index'] = str(self.index)
		for lang in STORYENGINE_LANGS:
			exec 'f_data["name'+lang+'"] = self.name'+lang
			exec 'f_data["description'+lang+'"] = self.description'+lang
		f_data['price'] = self.price
		f_data['expiration_days'] = self.expiration_days
		f_data['expiration_mins'] = self.expiration_mins
		f_data['version'] = self.version
		f_data['visible'] = self.visible
		return f_data

class TransForm(forms.Form):
	index = forms.CharField(label='index',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	nameen = forms.CharField(label='name (en)',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	nameko = forms.CharField(label='이름 (ko)',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	nameja = forms.CharField(label='名 (ja)',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	descriptionen = forms.CharField(label='description (en)',
			widget=forms.Textarea(attrs={
				'size':'2048',
				'limit':'2048',
				'cols':'52',
				'rows':'1',
				'wrap':'hard',
				}))
	descriptionko = forms.CharField(label='설명 (ko)',
			widget=forms.Textarea(attrs={
				'size':'2048',
				'limit':'2048',
				'cols':'52',
				'rows':'1',
				'wrap':'hard',
				}))
	descriptionja = forms.CharField(label='説明 (ja)',
			widget=forms.Textarea(attrs={
				'size':'2048',
				'limit':'2048',
				'cols':'52',
				'rows':'1',
				'wrap':'hard',
				}))
	price = forms.IntegerField(label='price',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	visible = forms.IntegerField(label='visible',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	expiration_days = forms.IntegerField(label='expiration_days',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	expiration_mins = forms.IntegerField(label='expiration_mins',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))

	@staticmethod
	def update_form(model):
		data = model.to_formdict()
		return TransForm(data)


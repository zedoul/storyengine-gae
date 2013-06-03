## coding: utf-8
from google.appengine.ext import db
import storyengine.model
import datetime
import time
from defines import CONTENT_EXPIRATION_DAYS
from defines import CONTENT_EXPIRATION_MINUTES
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from settings import CONTENT_PART_CATEGORY
import urllib
import logging

class Content (storyengine.model.TransModel):
#words, collocation(wr/sp), text
	part = db.CategoryProperty(choices=CONTENT_PART_CATEGORY)
	photo = db.BlobProperty()
	thumbnail = db.BlobProperty()

	def to_dict(self,keyid,lang,langonly_=False):
		d = super(Content,self).to_dict(keyid,lang,langonly_)
		if False == langonly_:
			d['part'] = self.part
			obj = None
			if self.expiration_days > 0 or self.expiration_mins > 0 :
				obj = datetime.datetime.now() + datetime.timedelta(days=self.expiration_days) + datetime.timedelta(minutes=self.expiration_mins)
			else:
				obj = datetime.datetime.now() + datetime.timedelta(days=CONTENT_EXPIRATION_DAYS) + datetime.timedelta(minutes=CONTENT_EXPIRATION_MINUTES)
			d['expiration_date'] = int(time.mktime(obj.timetuple()))
		return d

	def image_get(self,data,resize_w=-1,resize_h=-1):
		ret = None
		print "Asdf"
		try:
			d = None
#			if resize_w > 0 and resize_h > 0:
#			d = images.resize(data,resize_w,resize_h)
			print "zzz"
			d = images.resize(data,480,320)
			print "asdfdsf"
			ret = db.Blob(d)
			print "www"
		except:
			assert(0)
			ret = None
		return ret

	def setter(self,req):
		self.part = req['part']
		if "" != req['photo']:
			self.photo = db.Blob(req['photo'])
		if "" != req['thumbnail']:
			self.thumbnail = db.Blob(req['thumbnail'])

#self.image_get(photo,480,320)
#			if (True == ('thumbnail' in req)):
#				thumbnail = req['thumbnail']
#				self.thumbnail = self.image_get(thumbnail)
#			else:
#				self.thumbnail = self.image_get(photo,480,320)
		super(Content,self).setter(req)

	def to_formdict(self):
		f_data = super(Content,self).to_formdict()
		f_data['part'] = self.part
		return f_data

	@staticmethod
	def new(creator_):
		content = Content(
				creator=creator_,
				content_type='content')
		return content

	@staticmethod
	def api_read(keyid,lang1,lang2=""):
		content = Content.get_by_id(int(keyid))
		if None is content :
			logging.error('Err! content is None')
			return {'success':False,'id':keyid,'error':'invalid key_id'}
		cdata = super(Content,content).cache_get(lang1+"+"+lang2)
		if None is not cdata:
			logging.info('content get by cache')
			return cdata
		else:
			ret = content.to_dict(keyid,lang1)
			tran = None
			if "" != lang2:
				tran = content.to_dict(keyid,lang2,True)
			ret['tran'] = tran
			if None != content.photo:
				ret['photo'] = "photo?img_id="+str(keyid)
			if None != content.thumbnail:
				ret['thumb'] = "thumb?img_id="+str(keyid)
			ret["success"] = True
			obj = None
			if content.expiration_days > 0 or content.expiration_mins > 0 :
				obj = datetime.datetime.now() + datetime.timedelta(days=content.expiration_days) + datetime.timedelta(minutes=content.expiration_mins)
			else:
				obj = datetime.datetime.now() + datetime.timedelta(days=CONTENT_EXPIRATION_DAYS) + datetime.timedelta(minutes=CONTENT_EXPIRATION_MINUTES)
			super(Content,content).cache_set(ret,int(time.mktime(obj.timetuple())),lang1+"+"+lang2)
			logging.info('content get by new')
			return ret;

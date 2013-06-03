from google.appengine.ext import db
import storyengine.model
import datetime
import time
from defines import CATEGORY_EXPIRATION_DAYS
from defines import CATEGORY_EXPIRATION_MINUTES

class Category (storyengine.model.TransModel):
	def stories_get(self,lang):
		storylist = []
		for link in self.stories:
			try:
				f_data = {}
				exec 'f_data["lang"] = link.story.name'+lang 
				if "" != f_data["lang"]:
					storylist.append(link.story)
			except:
				pass
		storysortedlist = sorted(storylist, key=lambda p: p.index)
		ret = []
		for story in storysortedlist:
			try:
				ret.append(str(story.key().id()))
			except:
				pass
		return ret

	def to_dict(self,keyid,lang):
		d = super(Category,self).to_dict(keyid,lang)
		obj = None
		if self.expiration_days > 0 or self.expiration_mins > 0 :
			obj = datetime.datetime.now() + datetime.timedelta(days=self.expiration_days) + datetime.timedelta(minutes=self.expiration_mins)
		else:
			obj = datetime.datetime.now() + datetime.timedelta(days=CATEGORY_EXPIRATION_DAYS) + datetime.timedelta(minutes=CATEGORY_EXPIRATION_MINUTES)
		d['expiration_date'] = int(time.mktime(obj.timetuple()))
		return d

	@staticmethod
	def new(key_name_,creator_):
		category = Category(key_name=str(key_name_),
				creator=creator_,
				content_type='category')
		category.put()
		return category
	@staticmethod
	def getter(key_name_):
		category = Category.get_by_key_name(str(key_name_))
		return category

	def setter(self,params):
		super(Category,self).setter(params)

	@staticmethod
	def api_index(lang_,tostudy_):
		categorylist=[]
		categories = Category.all()
		for c in categories:
			if True == c.support_lang(lang_) and 1 == c.visible and True == c.support_tostudy(tostudy_):
				categorylist.append(c)
		categorysortedlist = sorted(categorylist, key=lambda p: p.index)
		retlist = []
		for category in categorysortedlist:
			try:
				retlist.append(str(category.key().name()))
			except:
				pass

		ret = {}
		ret["categories"] = retlist
		ret["success"] = True
		return ret;

	@staticmethod
	def api_read(key_name,lang):
		category=Category.get_by_key_name(str(key_name))
		if None is category:
			return {'id':key_name,'success':False,'error':'invalid key_name'}
		cdata = super(Category,category).cache_get(lang)
		if None is not cdata:
			return cdata
		else:
			ret = category.to_dict(key_name,lang)
			ret['stories'] = category.stories_get(lang)
			ret["success"] = True
			obj = None
			if category.expiration_days > 0 or category.expiration_mins > 0 :
				obj = datetime.datetime.now() + datetime.timedelta(days=category.expiration_days) + datetime.timedelta(minutes=category.expiration_mins)
			else:
				obj = datetime.datetime.now() + datetime.timedelta(days=CATEGORY_EXPIRATION_DAYS) + datetime.timedelta(minutes=CATEGORY_EXPIRATION_MINUTES)
			super(Category,category).cache_set(ret,int(time.mktime(obj.timetuple())),lang)
			return ret

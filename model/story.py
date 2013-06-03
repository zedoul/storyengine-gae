from google.appengine.ext import db
import storyengine.model
from storyengine.model.account import Account
from storyengine.model.content import Content
from storyengine.model.receipt import Receipt
from storyengine.model.category import Category
import datetime
import time
from defines import STORY_EXPIRATION_DAYS
from defines import STORY_EXPIRATION_MINUTES
from defines import PAGE_EXPIRATION_DAYS
from defines import PAGE_EXPIRATION_MINUTES
import logging

class Story (storyengine.model.TransModel):
#basic info
	main_categoryid = db.StringProperty(default=None)
	language = db.StringListProperty(default=None)

	def setter(self,req):
		main_categoryid_ = req.get('main_categoryid')
		self.main_categoryid = main_categoryid_
		super(Story,self).setter(req)

	def pages_get(self):
		pagelist = []
		for page in self.pages:
			if 1 == page.visible:
				pagelist.append(page)
		pagesortedlist = sorted(pagelist, key=lambda p: p.index)
		ret = []
		for page in pagesortedlist:
			try:
				ret.append(str(page.key().id()))
			except:
				pass
		return ret

	def to_dict(self,keyid,lang):
		d = super(Story,self).to_dict(keyid,lang)
		obj = None
		if self.expiration_days > 0 or self.expiration_mins > 0 :
			obj = datetime.datetime.now() + datetime.timedelta(days=self.expiration_days) + datetime.timedelta(minutes=self.expiration_mins)
		else:
			obj = datetime.datetime.now() + datetime.timedelta(days=STORY_EXPIRATION_DAYS) + datetime.timedelta(minutes=STORY_EXPIRATION_MINUTES)
		d['expiration_date'] = int(time.mktime(obj.timetuple()))
		d['main_categoryid'] = str(self.main_categoryid)
		return d

	def to_formdict(self):
		f_data = super(Story,self).to_formdict()
		f_data['main_categoryid']=self.main_categoryid
		return f_data

	@staticmethod
	def new(creator_):
		story = Story(creator=creator_,
				content_type='story')
		return story

	@staticmethod
	def api_index(lang):
		stories=[]
		for story in Story.all():
			stories.append(str(story.key().id()))
		ret = {}
		ret["stories"] = stories
		ret["success"] = True
		return ret;

	@staticmethod
	def api_read(keyid,lang):
		story = Story.get_by_id(int(keyid))
		if None is story :
			return {'success':False,'id':keyid,'error':'invalid key_id'}
		cdata = super(Story,story).cache_get(lang)
		if None is not cdata:
			return cdata
		else:
			ret = story.to_dict(keyid,lang)
			ret["pages"] = story.pages_get()
			ret["success"] = True
			obj = None
			if story.expiration_days > 0 or story.expiration_mins > 0 :
				obj = datetime.datetime.now() + datetime.timedelta(days=story.expiration_days) + datetime.timedelta(minutes=story.expiration_mins)
			else:
				obj = datetime.datetime.now() + datetime.timedelta(days=STORY_EXPIRATION_DAYS) + datetime.timedelta(minutes=STORY_EXPIRATION_MINUTES)
			super(Story,story).cache_set(ret,int(time.mktime(obj.timetuple())),lang)
			return ret;

	@staticmethod
	def api_purchase(storyid,account):
		story = Story.get_by_id(int(storyid))
		params={}
		params['id'] = storyid
		params['cost'] = story.price
		params['itemcost'] = 0
		params['receipt_type'] = 'data'
		ret = Receipt.new(params,account)
		if True == ret['success']:
			account.storyIDs.append(storyid)
			account.put()
		ret["id"] = str(storyid)
		return ret;

class Page (storyengine.model.TransModel):
	story = db.ReferenceProperty(Story,
			collection_name='pages')
	score = db.IntegerProperty(default=0)

	def childs_get(self):
		childslist = []
		try:
			for link in self.childs:
				try:
					childslist.append(str(link.child_page.key().id()))
				except:
					pass
			return childlist
		except:
			return []

	def contents_get(self):
		contentlist = []
		for link in self.contents:
			try :
				contentlist.append(link.content)
			except:
				logging.error('Error! linkID[%s]', str(link.key().name()))
				pass
		contentsortedlist = sorted(contentlist, key=lambda p: p.index)
		ret = []
		for content in contentsortedlist:
			try:
				ret.append(str(content.key().id()))
			except:
				logging.error('Error! content key [%s]', str(content.key().id()))
				pass
		return ret

	def setter(self,req):
		if (True == ('score' in req)):
			self.score = int(req['score'])
		super(Page,self).setter(req)

	def to_dict(self,keyid,lang):
		d = super(Page,self).to_dict(keyid,lang)
		obj = None
		if self.expiration_days > 0 or self.expiration_mins > 0 :
			obj = datetime.datetime.now() + datetime.timedelta(days=self.expiration_days) + datetime.timedelta(minutes=self.expiration_mins)
		else:
			obj = datetime.datetime.now() + datetime.timedelta(days=PAGE_EXPIRATION_DAYS) + datetime.timedelta(minutes=PAGE_EXPIRATION_MINUTES)
		d['expiration_date'] = int(time.mktime(obj.timetuple()))
		d['score'] = int(self.score)
		return d

	def to_formdict(self):
		f_data = super(Page,self).to_formdict()
		f_data['score']=self.score
		return f_data

	@staticmethod
	def new(creator_, story_=None, index_=0):
		page = Page(story=story_,
				creator=creator_,
				index=index_,
				content_type='page')
		page.visible = 0
		page.put()
		return page

	@staticmethod
	def api_read(keyid,lang):
		page = Page.get_by_id(int(keyid))
		if None is page :
			return {'success':False,'id':keyid,'error':'invalid key_id'}
		cdata = super(Page,page).cache_get(lang)
		if None is not cdata:
			return cdata
		else:
			ret = page.to_dict(keyid,lang)
			ret["contents"] = page.contents_get()
			ret["childs"] = page.childs_get()
			ret["success"] = True
			obj = None
			if page.expiration_days > 0 or page.expiration_mins > 0 :
				obj = datetime.datetime.now() + datetime.timedelta(days=page.expiration_days) + datetime.timedelta(minutes=page.expiration_mins)
			else:
				obj = datetime.datetime.now() + datetime.timedelta(days=PAGE_EXPIRATION_DAYS) + datetime.timedelta(minutes=PAGE_EXPIRATION_MINUTES)
			super(Page,page).cache_set(ret,int(time.mktime(obj.timetuple())),lang)
			return ret;

class CategoryStoryLink (db.Model):
	created = db.DateTimeProperty(auto_now_add=True)
	modified = db.DateTimeProperty(auto_now=True)
	category = db.ReferenceProperty(Category,
			collection_name='stories',
			required=True)
	story = db.ReferenceProperty(Story,
			collection_name='categories',
			required=True)
	@staticmethod
	def new(c_,s_):
		k = str(c_.key().name())+"+"+str(s_.key().id())
		obj = CategoryStoryLink(
				key_name=k,
				category=c_,
				story=s_)
		obj.put()

class PagePageLink (db.Model):
	created = db.DateTimeProperty(auto_now_add=True)
	modified = db.DateTimeProperty(auto_now=True)
	parent_page = db.ReferenceProperty(Page,
			collection_name='childs',
			required=True)
	child_page = db.ReferenceProperty(Page,
			collection_name='parents',
			required=True)
	@staticmethod
	def new(p_,c_):
		k = str(p_.key().id())+"+"+str(c_.key().id())
		obj = PagePageLink(
				key_name=k,
				parent_page=p_,
				child_page=c_)
		obj.put()

class PageContentLink (db.Model):
	created = db.DateTimeProperty(auto_now_add=True)
	modified = db.DateTimeProperty(auto_now=True)
	page = db.ReferenceProperty(Page,
			collection_name='contents',
			required=True)
	content = db.ReferenceProperty(Content,
			collection_name='pages',
			required=True)
	@staticmethod
	def new(p_,c_):
		k = str(p_.key().id())+"+"+str(c_.key().id())
		obj = PageContentLink(
				key_name=k,
				page=p_,
				content=c_)
		obj.put()


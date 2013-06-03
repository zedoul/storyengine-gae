## coding: utf-8

__author__ = 'Seonghyun Kim'

import os
import webapp2
from webapp2_extras import sessions
import logging, string
from settings import STATIC_PATH
from settings import TEMPLATE_DIR
from google.appengine.ext.webapp import template
import storyengine
import storyengine.model
from storyengine.model.story import Story
from storyengine.model.story import Page
from storyengine.model.story import PageContentLink
from storyengine.model.account import Account
from storyengine.model.receipt import Receipt
from storyengine.model.category import Category
from defines import APP_TITLE
from defines import PAGE_LEVEL1_INDEX_INTERVAL
from defines import PAGE_LEVEL2_INDEX_INTERVAL
from defines import PAGE_LEVEL3_INDEX_INTERVAL
from defines import PAGE_LEVEL1_LEN
from defines import PAGE_LEVEL2_LEN
from defines import PAGE_LEVEL3_LEN
from defines import PAGE_LEVEL1_SCORE_INIT
from defines import PAGE_LEVEL2_SCORE_INIT
from defines import PAGE_LEVEL3_SCORE_INIT
from defines import PAGE_LEVEL1_SCORE_DIFF
from defines import PAGE_LEVEL2_SCORE_DIFF
from defines import PAGE_LEVEL3_SCORE_DIFF
from defines import PAGE7_LEVEL1_PRICE
from defines import PAGE15_LEVEL1_PRICE
from defines import PAGE7_LEVEL2_PRICE
from defines import PAGE15_LEVEL2_PRICE
from defines import PAGE22_LEVEL2_PRICE
from defines import PAGE31_LEVEL2_PRICE
from defines import PAGE4_LEVEL3_PRICE
from defines import PAGE7_LEVEL3_PRICE
from defines import PAGE12_LEVEL3_PRICE
from defines import PAGE15_LEVEL3_PRICE
from defines import PAGE20_LEVEL3_PRICE
from defines import PAGE22_LEVEL3_PRICE
from defines import PAGE28_LEVEL3_PRICE
from defines import PAGE31_LEVEL3_PRICE
from defines import STORY_PIC_SHOW
from defines import STORY_PAGE_NAME_SHOW
from defines import STORY_PAGE_DESCRIPTION_SHOW
from defines import STORY_PAGE_CONTENTSIZE_SHOW
from defines import STORY_PAGE_NEXT_SHOW
from defines import STORY_PAGE_PRICE_SHOW
from defines import STORY_PAGE_SCORE_SHOW

import json
from django import forms

class StoryInfoForm(storyengine.model.TransForm):
	main_categoryid = forms.CharField(label='(*) 1st category (^[A-Z0-9]+)',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))

class StoryPageImportForm(forms.Form):
	pageid = forms.IntegerField(label='pageid',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))

class StoryPageScoreAllSetForm(forms.Form):
	score = forms.IntegerField(label='score',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	diff = forms.IntegerField(label='diff',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))

class StoryIndexHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		if None is accountid:
			context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'err_msg':"You should login"}
			self.render_to_response('err_page.html',context)
			return
		keytodel = self.request.get('del')
		stories = Story.all()
		stories.order('-created')
		storylist = []
		for story in stories:
			story.keyname = str(story.key().id())
			storylist.append(story)
		storysortedlist = sorted(storylist, key=lambda p: p.index)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'stories':storysortedlist,
			'keytodel':keytodel,
			'size':len(storylist)}
		self.render_to_response('story_index.html',context)

class StoryNewHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		s_form = StoryInfoForm(None)
		del s_form.fields['index']
		del s_form.fields['visible']
		del s_form.fields['price']
		del s_form.fields['expiration_days']
		del s_form.fields['expiration_mins']
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self): #logout
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		story = Story.new(account)
		params = {}
		for key in self.request.arguments():
			params[key] = self.request.get(key)
		story.setter(params)
		self.redirect('/story')

class StoryReadHandler(storyengine.SessionHandler):
	def get(self,keyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		pageidtodel = self.request.get('del')
		show = True
		purchased = True
		story = Story.get_by_id(int(keyid))
		key_name = []
		for link in story.categories:
			key_name.append(link.category.key().name())
		story.category_key_name = key_name
		startpageIDs = []
		pagelist = []
		for page in story.pages:
			page.keyid = str(page.key().id())
			page.contentsize = page.contents.count()
			if page.contents.count() > 0:
				try:
					page.contentid = str(page.contents[0].content.key().id())
				except:
					pass
			nexts = []
			for link in page.childs:
				pnext = {}
				p = link.child_page
				if p.contents.count() > 0:
					try:
						pnext['pageid'] = p.key().id()
						pnext['contentid'] = p.contents[0].content.key().id()
						nexts.append(pnext)
					except:
						pass
			page.nexts = nexts
			pagelist.append(page)
		pagelist = sorted(pagelist, key=lambda p: p.index)

		pageindexdic = {}
		for page in pagelist:
			tlist = None 
			try:
				tlist = pageindexdic[str(page.index)]
			except:
				tlist = []
			tlist.append(page)
			pageindexdic[str(page.index)] = tlist

		pageindexlist = []
		keys = pageindexdic.keys()
		keylist = sorted(keys, key=lambda k: int(k))

		for key in keylist: 
			pageindexlist.append(pageindexdic[key])

		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'story':story,
			'pages':pageindexlist,
			'pagesize':len(pageindexlist),
			'pageidtodel':pageidtodel,
			'purchased':purchased,
			'show':show,
			'picshow':STORY_PIC_SHOW,
			'pagenameshow':STORY_PAGE_NAME_SHOW,
			'pagedescshow':STORY_PAGE_DESCRIPTION_SHOW,
			'pagepriceshow':STORY_PAGE_PRICE_SHOW,
			'pagescoreshow':STORY_PAGE_SCORE_SHOW,
			'pagecontentsizeshow':STORY_PAGE_CONTENTSIZE_SHOW,
			'pagenextshow':STORY_PAGE_NEXT_SHOW,
			'keyid':story.key().id()}
		self.render_to_response('story_read.html',context)

class StoryUpdateHandler(storyengine.SessionHandler):
	def get(self,keyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		story = Story.get_by_id(int(keyid))
		f_data = story.to_formdict()
		s_form = StoryInfoForm(f_data)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('story_update.html',context)
	def post(self,keyid): #logout
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		story = Story.get_by_id(int(keyid))
		params = {}
		for key in self.request.arguments():
			params[key] = self.request.get(key)
		story.setter(params)
		self.redirect('/story/'+keyid)

class StoryPageScoreAllSetHandler(storyengine.SessionHandler):
	def get(self,keyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		s_form = StoryPageScoreAllSetForm(None)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self,keyid): #logout
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		story = Story.get_by_id(int(keyid))
		score = int(self.request.get('score'))
		diff = int(self.request.get('diff'))
		for i in story.pages:
			i.score = score
			score = score + diff
			i.put()
		self.redirect('/story/'+keyid)

class StoryPageIndexAllSetHandler(storyengine.SessionHandler):
	def get(self,keyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		story = Story.get_by_id(int(keyid))
		i = 1
		pagelist = []
		for page in story.pages:
			pagelist.append(page)
		pagelist = sorted(pagelist, key=lambda p: p.index)
		for page in pagelist:
			page.index = i
			i=i+1
			page.put()
		self.redirect('/story/'+keyid)

class StoryDelHandler(storyengine.SessionHandler):
	def get(self,storykeyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		story = Story.get_by_id(int(storykeyid))
		for page in story.pages:
			for link in page.contents:
				link.delete()
			page.delete()
		story.delete()
		self.redirect("/story")

class StoryPurchaseHandler(storyengine.SessionHandler):
	def get(self,storyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		story = None
		try:
			story = Story.get_by_id(int(storyid))
		except:
			print "Storyid("+storyid+") Err!"
			return
		params = {}
		params['dataID'] = self.request.get('dataID')
		params['cost'] = self.request.get('cost')
		params['receipt_type'] = self.request.get('receipt_type')

		Receipt.new(params,account)
		self.redirect('/story/'+storyid)

class StoryPageAddHandler(storyengine.SessionHandler):
	def get(self,storyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		story_ = Story.get_by_id(int(storyid))
		pagelist = []
		for page in story_.pages:
			pagelist.append(page)
		Page.new(account,story_,len(pagelist)+1)
		self.redirect("/story/"+storyid)

class StoryPageDelHandler(storyengine.SessionHandler):
	def get(self,storyid,pageid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		page = Page.get_by_id(int(pageid))
		for link in page.contents:
			link.delete()
		page.delete()
		self.redirect("/story/"+storyid)

class StoryPageImportHandler(storyengine.SessionHandler):
	def get(self,storyid):
		s_form = StoryPageImportForm(None)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self,keyid): #logout
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		story_ = Story.get_by_id(int(keyid))
		page = Page.new(account,story_)
		pageid = int(self.request.get('pageid'))
		pageToImport = Page.get_by_id(int(pageid))
		for link in pageToImport.contents:
			PageContentLink.new(page,link.content)
		self.redirect('/story/'+keyid)

class StoryLangAddHandler(storyengine.SessionHandler):
	def get(self,storyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		lang = self.request.get('lang')
		accountid = self.session.get('accountid')
		story = Story.get_by_id(int(storyid))
		story.language.append(lang)
		story.put()
		self.redirect("/story/"+storyid)

class StoryLangDelHandler(storyengine.SessionHandler):
	def get(self,storyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		lang = self.request.get('lang')
		story = Story.get_by_id(int(storyid))
		index = story.language.index(lang)
		del story.language[index]
		story.put()
		self.redirect("/story/"+storyid)

class AppStoryIndexHandler(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'application/json'
		lang = self.request.get('lang')
		ret = Story.api_index(lang)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(ret))

class AppStoryReadHandler(webapp2.RequestHandler):
	def get(self,storyid):
		lang = self.request.get('lang')
		ret = Story.api_read(storyid,lang)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(ret))

# "success"	1 on success
#		-1 on error
#		-2 on session error (accountid is None)
class AppStoryPurchaseHandler(webapp2.RequestHandler):
	def post(self,storyid):
		facebookid = self.request.get('facebookid')
		account = Account.get_by_facebookid(facebookid)
		ret = Story.api_purchase(storyid,account)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(ret))

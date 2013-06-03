## coding: utf-8
import os
import webapp2
from webapp2_extras import sessions
#http://stackoverflow.com/questions/12737008/google-app-engine-session-works-in-localhost-but-fails-when-deployed
import logging, string
from settings import STATIC_PATH
from settings import TEMPLATE_DIR
from defines import APP_TITLE
from google.appengine.ext.webapp import template
from storyengine.model.account import Account
from storyengine.model.story import Page
from storyengine.model.story import PagePageLink
from storyengine.model.story import PageContentLink
from storyengine.model.content import Content
#from django import forms
from django import forms
#from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponse
from django.template import Context, loader
import json
from storyengine.content import ContentInfoForm
import storyengine.model
from collections import namedtuple
from settings import _
from django.utils.translation import ugettext_lazy
from defines import PAGE_MULTISEARCH_SHOW
from defines import PAGE_MULTIUPDATE_SHOW
from defines import PAGE_SYNC_SHOW
from defines import PAGE_IMPORT_SHOW

class PageInfoForm(storyengine.model.TransForm):
	score = forms.IntegerField(label='score',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	nameen = forms.CharField(label=ugettext_lazy('pagenameen'),
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	nameko = forms.CharField(label=ugettext_lazy('pagenameko'),
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	nameja = forms.CharField(label=ugettext_lazy('pagenameja'),
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	descriptionen = forms.CharField(label=ugettext_lazy('pagedescriptionen'),
			widget=forms.Textarea(attrs={
				'size':'2048',
				'limit':'2048',
				'cols':'52',
				'rows':'1',
				'wrap':'hard',
				}))
	descriptionko = forms.CharField(label=ugettext_lazy('pagedescriptionko'),
			widget=forms.Textarea(attrs={
				'size':'2048',
				'limit':'2048',
				'cols':'52',
				'rows':'1',
				'wrap':'hard',
				}))
	descriptionja = forms.CharField(label=ugettext_lazy('pagedescriptionja'),
			widget=forms.Textarea(attrs={
				'size':'2048',
				'limit':'2048',
				'cols':'52',
				'rows':'1',
				'wrap':'hard',
				}))

class PagePageAddForm(forms.Form):
	pageid = forms.CharField(label='pageid',
		widget=forms.TextInput(attrs={
				'size':'54',
				'maxlength':'100',
				}))

class PageContentSearchForm(forms.Form):
	contentid = forms.CharField(label='contentid',
		widget=forms.TextInput(attrs={
				'size':'54',
				'maxlength':'100',
				}))
	nameen = forms.CharField(label=ugettext_lazy('nameen'),
		widget=forms.TextInput(attrs={
				'size':'54',
				'maxlength':'100',
				}))
	nameko = forms.CharField(label=ugettext_lazy('nameko'),
		widget=forms.TextInput(attrs={
				'size':'54',
				'maxlength':'100',
				}))

class PageContentsSyncForm(forms.Form):
	indexfrom = forms.IntegerField(label='page index (from)',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	indexto = forms.IntegerField(label='page index (to)',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))

class PageContentsImportForm(forms.Form):
	pageid = forms.IntegerField(label='pageid',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))

class PageReadHandler(storyengine.SessionHandler):
	def get(self,keyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		page = Page.get_by_id(int(keyid))
		contents = []
		for link in page.contents:
			try:
				content = link.content
				content.keyid = content.key().id()
				contents.append(content)
			except:
				content = None
		contentsortedlist = sorted(contents, key=lambda p: p.index)

		parents = []
		for link in page.parents:
			p = link.parent_page
			p.keyid = p.key().id()
			parents.append(p)

		childs = []
		for link in page.childs:
			p = link.child_page
			p.keyid = p.key().id()
			childs.append(p)

		storykeyid = None 
		if None != page.story:
			storykeyid = str(page.story.key().id())
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'pagemultisearchshow':PAGE_MULTISEARCH_SHOW,
			'pagemultiupdateshow':PAGE_MULTIUPDATE_SHOW,
			'pagesyncshow':PAGE_SYNC_SHOW,
			'pageimportshow':PAGE_IMPORT_SHOW,
			'page':page,
			'contents':contentsortedlist,
			'parents':parents,
			'childs':childs,
			'storyid':storykeyid,
			'keyid':page.key().id()}
		self.render_to_response('page_read.html',context)

class PageUpdateHandler(storyengine.SessionHandler):
	def get(self,pagekeyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		page = Page.get_by_id(int(pagekeyid))
		f_data = page.to_formdict()
		s_form = PageInfoForm (f_data)
		del s_form.fields['index']
		del s_form.fields['score']
		del s_form.fields['price']
		del s_form.fields['visible']
		del s_form.fields['expiration_days']
		del s_form.fields['expiration_mins']
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self,pageid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		page = Page.get_by_id(int(pageid))
		params = {}
		for key in self.request.arguments():
			params[key] = self.request.get(key)
		page.setter(params)
		self.redirect('/page/'+pageid)

class PageDelHandler(storyengine.SessionHandler):
	def get(self,pagekeyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		page = Page.get_by_id(int(pagekeyid))
		for link in page.contents:
			link.delete()
		page.delete()
		self.redirect("/story")

class PageContentAddHandler(storyengine.SessionHandler):
	def get(self,pageid,contentid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		page = Page.get_by_id(int(pageid))
		content = Content.get_by_id(int(contentid))
		PageContentLink.new(page,content)
		self.redirect('/page/'+pageid)

class PagePageLinkAddHandler(storyengine.SessionHandler):
	def get(self,pageid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		s_form = PagePageAddForm(None)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self,pageid1):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		pageid2 = self.request.get('pageid')
		page1 = Page.get_by_id(int(pageid1))
		page2 = Page.get_by_id(int(pageid2))
		PagePageLink.new(page1,page2)
		self.redirect('/page/'+pageid1)

class PageIndexHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		mode = self.request.get('mode')
		keytodel = self.request.get('del')
		if 'all' == mode:
			pages = Page.all().order('-created')
		else:
			pages = Page.all().order('-created').fetch(limit=5)
		pagelist = []
		Next = namedtuple("Next", "pageid contentid")
		for page in pages:
			page.keyname = str(page.key().id())
			if page.contents.count() > 0: #content at foremost 
				page.content = page.contents[0].content
				page.content.keyid = page.content.key().id()
			childlist = []
			for l in page.childs:
				if l.child_page.contents.count() > 0:
					n = Next(l.child_page.key().id(), l.child_page.contents[0].content.key().id())
					childlist.append(n)
			page.childlist = childlist
			pagelist.append(page)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'pages':pagelist,
			'keytodel':keytodel,
			'size':len(pagelist)}
		self.render_to_response('page_index.html',context)

class PageNewHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		s_form = PageInfoForm(None)
		del s_form.fields['visible']
		del s_form.fields['price']
		del s_form.fields['score']
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
		page = Page.new(account)
		params = {}
		for key in self.request.arguments():
			params[key] = self.request.get(key)
		page.setter(params)
		self.redirect('/page')

class PageContentNewHandler(storyengine.SessionHandler):
	def get(self,pageid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		s_form = ContentInfoForm({'visible':1,'price':0,'index':0})
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self,pageid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		content_ = Content.new(account)
		params = {}
		for key in self.request.arguments():
			params[key] = self.request.get(key)
		content_.setter(params)
		page_ = Page.get_by_id(int(pageid))
		PageContentLink.new(page_,content_)
		self.redirect('/page/'+pageid)

class PageContentSearchHandler(storyengine.SessionHandler):
	def get(self,pageid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		s_form = PageContentSearchForm(None)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)

	def post(self,pageid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		contentlist = []
		contentid = self.request.get('contentid')
		nameen = self.request.get('nameen')
		nameko = self.request.get('nameko')

		if "" != contentid:
			i = Content.get_by_id(int(contentid))
			i.keyid = i.key().id()
			contentlist.append(i)
		elif "" != nameen:
			result = Content.all().filter("nameen =",nameen)
			for i in result :
				i.keyid = i.key().id()
				contentlist.append(i)
		elif "" != nameko:
			result = Content.all().filter("nameko =",nameko)
			for i in result :
				i.keyid = i.key().id()
				contentlist.append(i)

		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'contents':contentlist,
			'pageid':pageid,
		}
		self.render_to_response('page_content_search.html',context)

class PageContentDelHandler(storyengine.SessionHandler):
	def get(self,pageid,contentid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		p = Page.get_by_id(int(pageid))
		c = Content.get_by_id(int(contentid))
		obj = PageContentLink.get_by_key_name(
				str(p.key().id())+"+"+str(c.key().id()))
		obj.delete()
		self.redirect("/page/"+pageid)

class PageContentsImportHandler(storyengine.SessionHandler):
	def get(self,storyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		s_form = PageContentsImportForm(None)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self,keyid): #logout
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		page = Page.get_by_id(int(keyid))
		pageid = int(self.request.get('pageid'))
		pageToImport = Page.get_by_id(int(pageid))
		for link in pageToImport.contents:
			try:
				if None != link and None != link.content and None != page:
					PageContentLink.new(page,link.content)
			except:
				pass
		self.redirect('/page/'+keyid)

class PageContentsSyncHandler(storyengine.SessionHandler):
	def get(self,pageid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		s_form = PageContentsSyncForm(None)
		context = {'static_path': STATIC_PATH,
			'APP_TITLE' : APP_TITLE,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self,keyid): #logout
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return
		page = Page.get_by_id(int(keyid))
		for link in page.contents:
			link.delete()
		indexfrom = int(self.request.get('indexfrom'))
		indexto = int(self.request.get('indexto'))
		pagelist = []
		for p in page.story.pages:
			pagelist.append(p)
		pagelist = sorted(pagelist, key=lambda p: p.index)
		for p in pagelist:
			if p.index >= indexfrom:
				for link in p.contents:
					PageContentLink.new(page,link.content)
			if p.index > indexto:
				break

		self.redirect('/page/'+keyid)

class AppPageReadHandler(webapp2.RequestHandler):
	def get(self,keyid):
		lang = self.request.get('lang')
		ret = Page.api_read(keyid,lang)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(ret))


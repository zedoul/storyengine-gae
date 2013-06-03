from google.appengine.ext import db
import storyengine.model
from storyengine.model import LinkModel
from storyengine.model.account import Account
from storyengine.model.receipt import Receipt
from storyengine.model.category import Category
from storyengine.model.story import Story
from storyengine.model.story import Page
from storyengine.model.content import Content
from storyengine.model.achievement import Achievement

class AccountAchievementLink (LinkModel):
	account = db.ReferenceProperty(Account,
			collection_name='achievementlinks',
			required=True)
	achievement = db.ReferenceProperty(Achievement,required=True)

class AccountCategoryLink (LinkModel):
	account = db.ReferenceProperty(Account,
			collection_name='categorylinks',
			required=True)
	category = db.ReferenceProperty(Category,required=True)
	@staticmethod
	def api_get(account_,category_):
		keyname = str(account_.key().id()) + "+" +  str(category_.key().id())
		link = AccountCategoryLink.get_by_key_name(keyname)
		if None is link:
			link = AccountCategoryLink(
				key_name = keyname,
				account=account_,
				category=category_)
			link.put()
		ret = {}
		ret["link"] = link
		ret["success"] = True
		return ret
	@staticmethod
	def api_read(account_,category_):
		return AccountCategoryLink.api_get(account_,category_)
	@staticmethod
	def api_new(account_,category_):
		return AccountCategoryLink.api_get(account_,category_)
	@staticmethod
	def api_submit(account_,category_,score_):
		det = AccountCategoryLink.api_get(account_,category_)
		link = det["link"]
		link.score = int(score_)
		link.put()
		ret = {}
		ret["success"] = True
		return ret

class AccountStoryLink (LinkModel):
	account = db.ReferenceProperty(Account,
			collection_name='storylinks',
			required=True)
	story = db.ReferenceProperty(Story,required=True)

class AccountPageLink (LinkModel):
	account = db.ReferenceProperty(Account,
			collection_name='pagelinks',
			required=True)
	page = db.ReferenceProperty(Page,required=True)
	@staticmethod
	def api_get(account_,page_):
		key_name_ = LinkModel.key_name_get(account_.key().id(),page_.key().id())
		link = AccountPageLink.get_or_insert(
				key_name_,
				account=account_,
				page=page_,
				link_type='accountpage'
				)
		ret = {}
		ret["link"] = link
		return ret
	@staticmethod
	def api_read(account_,page_):
		det = AccountPageLink.api_get(account_,page_)
		link = det['link']
		ret = {}
		ret["score"] = link.score
		ret["success"] = True
		return ret
	@staticmethod
	def api_submit(account_,page_,score_):
		det = AccountPageLink.api_get(account_,page_)
		link = det["link"]
		if int(score_) > link.score:
			link.score = int(score_)
			link.put()
		ret = {}
		ret["score"] = link.score
		ret["success"] = True
		return ret

class AccountContentLink (storyengine.model.LinkModel):
	account = db.ReferenceProperty(Account,
			collection_name='contentlinks',
			required=True)
	content = db.ReferenceProperty(Content,required=True)


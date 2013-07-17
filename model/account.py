from google.appengine.ext import db
from storyengine.model import AccountModel
import storyengine.model
import time
import datetime
from defines import FORCEUPDATE
from defines import MAINTENANCE
from defines import RANK_EXPIRATION_DAYS
from defines import CANDY_TIER1_PRICE
from defines import CANDY_TIER2_PRICE
from defines import CANDY_TIER3_PRICE
from defines import CANDY_TIER4_PRICE
from defines import CANDY_TIER1_VALUE
from defines import CANDY_TIER2_VALUE
from defines import CANDY_TIER3_VALUE
from defines import CANDY_TIER4_VALUE
from defines import CACHE_RECOMMENDED_ACCOUNTNUM
from google.appengine.api import memcache
import random
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import hashlib
import logging

__author__ = 'Seonghyun Kim'

class Rank (db.Model):
	created = db.DateTimeProperty(auto_now_add=True)
	modified = db.DateTimeProperty(auto_now=True)
	facebookID = db.StringProperty(default=None)
	@staticmethod
	def setter(facebookid,score):
		try:
			i = (int(hashlib.md5(str(facebookid)).hexdigest(),16) % int(CACHE_RECOMMENDED_ACCOUNTNUM)) + 1
			key_name_ = 'rank'+str(i)
			rank = Rank.get_by_key_name(str(key_name_))
			logging.info('Ranked in [%s] by user %s [1]', str(key_name_) ,str(facebookid))
			if None == rank:
				logging.info('Ranked in [%s] by user %s [prev none]', str(key_name_) ,str(facebookid))
				rank = Rank(key_name=str(key_name_))
				rank.facebookID = facebookid
				rank.put()
				return
			target = Account.get_by_facebookid(str(rank.facebookID))
			logging.info('Ranked in [%s] by user %s [2]', str(key_name_) ,str(facebookid))
			if None == target:
				logging.error('Ranked in [%s] by user %s [target none]', str(key_name_) ,str(facebookid))
				rank.facebookID = facebookid
				rank.put()
				return
			todate = datetime.datetime.now()
			logging.info('Ranked in [%s] by user %s [3]', str(key_name_) ,str(facebookid))
			if target.score_expiration < todate:
				logging.info('Ranked in [%s] by user %s [new date]', str(key_name_) ,str(facebookid))
				rank.facebookID = facebookid
				rank.put()
				return
			logging.info('Ranked in [%s] by user %s [4]', str(key_name_) ,str(facebookid))
			if (score > target.score):
				logging.info('Ranked in [%s] by user %s [new score(%d)] > (%d)', 
					str(key_name_),str(facebookid),score,target.score)
				rank.facebookID = facebookid
				rank.put()
				return
			logging.info('Ranked in [%s] by user %s [5]', str(key_name_) ,str(facebookid))
		except:
			logging.error('Error!')
			return
	@staticmethod
	def getter():
		ret = []
		for i in range(1,CACHE_RECOMMENDED_ACCOUNTNUM+1):
			key = 'rank'+str(i)
			rank = Rank.get_by_key_name(str(key))
			if None is not rank:
				ret.append(rank.facebookID)
		return ret

class Account (AccountModel): 
	facebookID = db.StringProperty(required=True)
	money = db.IntegerProperty(default=500)
	candy = db.IntegerProperty(default=70)
	'''purchased story'''
	storyIDs = db.StringListProperty(default=None)
	score = db.IntegerProperty(default=0)
	maxscore = db.IntegerProperty(default=0)
	score_expiration = db.DateTimeProperty(auto_now_add=True)
	day_expiration = db.DateTimeProperty(auto_now_add=True)

	@staticmethod
	def key_name_get(accountid):
		key_name = None
		try:
			int(accountid)
			key_name = "account+"+str(accountid)
		except:
			key_name = "guest+"+str(accountid)
		return key_name

	def to_formdict(self):
		f_data = {}
		f_data['name'] = self.name
		f_data['facebookID'] = self.facebookID
		f_data['thumbnail'] = self.thumbnail
		return f_data

	def setter(self,params):
		self.name = params['name']
		self.facebookID = params['facebookID']
		self.thumbnail = db.Blob(params['thumbnail'])
		logging.info('name:[%s] facebookID:[%s]', self.name, self.facebookID)
		self.put()

	@staticmethod
	def get_by_accountid(accountid):
		ret = Account.get_by_key_name(accountid)
		return ret

	@staticmethod
	def get_by_facebookid(facebookid):
		keyname = Account.key_name_get(facebookid)
		ret = Account.get_by_key_name(keyname)
		return ret

	@staticmethod
	def api_convert(facebookid,access_token,expiration_date_,name,guestid):
		prevaccount = Account.get_by_facebookid(guestid)
		if None == prevaccount:
			logging.error('convert [%s] [fail:no prev account] ', str(facebookid))
			return {"success":False}
		det = Account.api_login(facebookid,
				access_token,
				expiration_date_,
				name)
		if False == det['success']:
			logging.error('convert [%s] [fail:login] ', str(facebookid))
			return {"success":False}
		if True == det['created']:
			newaccount = Account.get_by_facebookid(facebookid)
			if None == newaccount:
				logging.error('convert [%s] [fail:create] ', str(facebookid))
				return {"success":False}
			newaccount.money = prevaccount.money
			newaccount.candy = prevaccount.candy
			newaccount.storyIDs = prevaccount.storyIDs
			newaccount.score = prevaccount.score
			newaccount.maxscore = prevaccount.maxscore
			newaccount.score_expiration = prevaccount.score_expiration
			newaccount.day_expiration = prevaccount.day_expiration
			newaccount.put()
			prevaccount.delete()
			logging.info('convert [%s] [success] ', str(facebookid))
		ret = Account.api_login(facebookid,
				access_token,
				expiration_date_,
				name)
		return ret

	@staticmethod
	def api_login(facebookid,access_token,expiration_date_,name):
		account = Account.get_by_facebookid(facebookid)
		ret = None
		if None == expiration_date_:
			expiration_date_ = "2333-03-13 03:03:33"
		expiration_date = datetime.datetime.strptime(expiration_date_, '%Y-%m-%d %H:%M:%S')
		prices = {}
		prices['candyprices'] = [CANDY_TIER1_PRICE,
		CANDY_TIER2_PRICE,
		CANDY_TIER3_PRICE,
		CANDY_TIER4_PRICE]
		prices['candypricevalues'] = [CANDY_TIER1_VALUE,
		CANDY_TIER2_VALUE,
		CANDY_TIER3_VALUE,
		CANDY_TIER4_VALUE]

		if None == account:
			account = Account(
					key_name = Account.key_name_get(facebookid),
					name=name,
					access_token=access_token,
					facebookID=facebookid,
					expiration_date=expiration_date)
			tobj = datetime.datetime.today().replace(hour=0, minute=0, second=0)+datetime.timedelta(days=1)
			account.day_expiration = tobj
			account.storyIDs = []
			account.put()
			ret = {"success":True,"created":True}
			logging.info('login user [%s] [create]', str(facebookid))
		else:
			todate = datetime.datetime.now()
			if account.expiration_date > todate:
				if account.access_token == access_token:
					ret = {"success":True,"created":False}
				else:
					ret = {"success":False,"created":False}
					ret['error'] = "Access Token mismatched"
			else:
				account.access_token = access_token
				account.expiration_date  = expiration_date
				account.put()
				ret = {"success":True,"created":False}
			if None == account.day_expiration:
				tobj = datetime.datetime.today().replace(hour=0, minute=0, second=0)+datetime.timedelta(days=1)
				account.day_expiration = tobj
				account.put()
			if account.day_expiration < todate:
				if account.candy < 10:
					account.candy = account.candy + 3
					if account.candy > 10:
						account.candy = 10
					ret['freecandy']=True
				tobj = datetime.datetime.today().replace(hour=0, minute=0, second=0)+datetime.timedelta(days=1)
				account.day_expiration = tobj
				account.put()
			else:
				ret['freecandy']=False
			logging.info('login user [%s] [connect]', str(facebookid))
		ret['id']=account.key().name()
		ret['name']=account.name
		ret['prices']=prices
		ret['money']=account.money
		ret['candy']=account.candy
		ret['storyIDs']=account.storyIDs
		ret['recommend']=Account.recommended_users()
		ret['score']=account.score
		ret['maintenance'] = MAINTENANCE
		ret['forceupdate'] = FORCEUPDATE
		ret['score_expiration']=int(time.mktime(account.score_expiration.timetuple()))
		ret['rank_expiration_days']=RANK_EXPIRATION_DAYS
		return ret

	@staticmethod
	def api_submit(req,account_):
		score_ = req.get('score')
		maxscore_ = req.get('maxscore')
		money_ = req.get('money')
		candy_ = req.get('candy')
		dataid_ = req.get('id')

		if 0 < int(score_):
			diffdays = int(RANK_EXPIRATION_DAYS) #1:next 7:Sat
			if diffdays == 7:
				#Monday is 0 and Sunday is 6
				diffdays = 5 - datetime.datetime.today().weekday()
				if diffdays <= 0:
					#Saturday and Sunday handler
					diffdays = 7 + diffdays
			tobj = datetime.datetime.today().replace(hour=0, minute=0, second=0)+datetime.timedelta(days=diffdays)
			account_.score = int(score_)
			account_.maxscore = int(maxscore_)
			account_.score_expiration =tobj
			Rank.setter(account_.facebookID, int(score_))
#			account_.join(account_.facebookID,int(score_))
		account_.money = account_.money - int(money_)
		account_.candy = account_.candy - int(candy_)
		if account_.money < 0:
			account_.money = 0
		if account_.candy < 0:
			account_.candy = 0
		account_.put()
		ret = {}
		ret["success"] = True
		return ret

	@staticmethod
	def api_gift(money_,candy_,account_):
		diffdays = int(RANK_EXPIRATION_DAYS) #1:next 7:Sat
		if diffdays == 7:
			#Monday is 0 and Sunday is 6
			diffdays = diffday- 2 - datetime.datetime.today().weekday
			if diffdays <= 0:
				#Saturday and Sunday handler
				diffdays = 7 - diffdays
		tobj = datetime.datetime.today().replace(hour=0, minute=0, second=0)+datetime.timedelta(days=diffdays)
		if tobj > account_.score_expiration:
			account_.score_expiration =tobj
			account_.money = account_.money + int(money_)
			account_.candy = account_.candy + int(candy_)
			if account_.money < 0:
				account_.money = 0
			if account_.candy < 0:
				account_.candy = 0
			account_.put()
		ret = {}
		ret["success"] = True
		return ret


	@staticmethod
	def api_update(params, account):
		account.name = params['name']
#		if None != params['thumb']:
#			account.thumbnail = db.Blob(str(params['thumb']))
		logging.info('[%s]:name update -> [%s]', account.facebookID, account.name)

		account.put()
		ret = {}
		ret["success"] = True
		return ret;

	@staticmethod
	def api_read(facebookid):
		account = Account.get_by_facebookid(facebookid)
		ret = {}
		if (None != account):
			ret["id"] = account.facebookID
			ret["name"] = account.name
			ret["score"] = account.score
			ret["score_expiration"] = int(time.mktime(account.score_expiration.timetuple()))
			ret["success"] = True
			if None != account.thumbnail:
				ret["thumb"] = "/app/account/thumb?img_id="+str(account.facebookID)
		else:
			ret["id"] = facebookid
			ret["success"] = False
		return ret

	def join(self,facebookid,score):
		try:
			i = (int(hashlib.md5(str(facebookid)).hexdigest(),16) % int(CACHE_RECOMMENDED_ACCOUNTNUM)) + 1
			key = 'recentjoinedaccount'+str(i)
			prev_facebookid = memcache.get(key)
			if None == prev_facebookid:
				logging.info('Ranked in [%s] by user %s [prev none]', str(key) ,str(facebookid))
				memcache.set(key,facebookid,864000)
				return
	
			target = Account.get_by_facebookid(str(prev_facebookid))
			if None == target:
				logging.error('Ranked in [%s] by user %s [target none]', str(key) ,str(facebookid))
				memcache.set(key,facebookid,864000)
				return
	
			todate = datetime.datetime.now()
			if target.score_expiration < todate:
				logging.info('Ranked in [%s] by user %s [new date]', str(key) ,str(facebookid))
				memcache.set(key,facebookid,864000)
				return
	
			if (score > target.score):
				logging.info('Ranked in [%s] by user %s [new score(%d)] > (%d)', 
						str(key),str(facebookid),score,target.score)
				memcache.set(key,facebookid,864000)
				return
		except:
			logging.error('Error! join')
			return

	@staticmethod
	def recommended_users():
		return Rank.getter()


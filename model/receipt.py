from google.appengine.ext import db
from storyengine.model.account import Account
from defines import COIN_TIER1_VALUE
from defines import COIN_TIER2_VALUE
from defines import COIN_TIER3_VALUE
from defines import COIN_TIER4_VALUE
from defines import COIN_TIER5_VALUE
from defines import CANDY_TIER1_PRICE
from defines import CANDY_TIER2_PRICE
from defines import CANDY_TIER3_PRICE
from defines import CANDY_TIER4_PRICE
from defines import CANDY_TIER1_VALUE
from defines import CANDY_TIER2_VALUE
from defines import CANDY_TIER3_VALUE
from defines import CANDY_TIER4_VALUE
from storyengine.model import ReceiptModel
import hashlib

class Receipt (ReceiptModel):
	itemcost = db.IntegerProperty(required=True)
	account = db.ReferenceProperty(Account,
			collection_name='receipts',
			required=True)
	towhom = db.ReferenceProperty(Account,
			collection_name='gifts'),

	@staticmethod
	def new(params,creator_,towhom_=None):
		dataID = params['id']
		if None is dataID:
			dataID = 0
		itemcost_ = params['itemcost']
		if None is itemcost_:
			itemcost_ = 0
		cost = int(params['cost'])
		receipt_type_ = params['receipt_type']
		before_ = None
		after_ = None

		if receipt_type_ == 'money':
			before_ = creator_.money
			if 1 == cost:
				after_ = before_ + int(COIN_TIER1_VALUE)
			elif 2 == cost:
				after_ = before_ + int(COIN_TIER2_VALUE)
			elif 3 == cost:
				after_ = before_ + int(COIN_TIER3_VALUE)
			elif 4 == cost:
				after_ = before_ + int(COIN_TIER4_VALUE)
			elif 5 == cost:
				after_ = before_ + int(COIN_TIER5_VALUE)
			else:
				assert(0)
			creator_.money = after_
			creator_.put()

		elif receipt_type_ == 'candy':
			before_ = creator_.candy
			if 1 == cost:
				after_ = before_ + int(CANDY_TIER1_VALUE)
				creator_.money = creator_.money - int(CANDY_TIER1_PRICE)
			elif 2 == cost:
				after_ = before_ + int(CANDY_TIER2_VALUE)
				creator_.money = creator_.money - int(CANDY_TIER2_PRICE)
			elif 3 == cost:
				after_ = before_ + int(CANDY_TIER3_VALUE)
				creator_.money = creator_.money - int(CANDY_TIER3_PRICE)
			elif 4 == cost:
				after_ = before_ + int(CANDY_TIER4_VALUE)
				creator_.money = creator_.money - int(CANDY_TIER4_PRICE)
			else:
				assert(0)
			creator_.candy = after_
			creator_.put()

		elif receipt_type_ == 'data':
			before_ = creator_.candy
			after_ = before_ - cost
			creator_.candy = after_
			creator_.put()

		elif receipt_type_ == 'gift':
			before_ = creator_.candy
			after_ = before_ - cost
			creator_.candy = after_
			towhom_.candy = cost
			creator_.put()

#		elif receipt_type_ == 'play':
#			before_ = int(params['score'])
#			after_ = int(params['maxscore'])
		else:
			assert(0)

		receipt = Receipt(
				dataID=int(dataID),
				before=before_,
				cost=cost,
				after=after_,
				receipt_type=receipt_type_,
				towhom=towhom_,
				account=creator_,
				itemcost=int(itemcost_)
				)
		if receipt_type_ == 'money':
			receipt_data = params['receipt_data']
			receipt.receipt_hash = str(hashlib.md5(str(receipt_data)).hexdigest())
		receipt.put()
		ret = {}
		ret['money'] = creator_.money
		ret['candy'] = creator_.candy
		ret["success"] = True
		return ret;


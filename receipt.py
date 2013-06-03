import os
import webapp2
from webapp2_extras import sessions
#http://stackoverflow.com/questions/12737008/google-app-engine-session-works-in-localhost-but-fails-when-deployed
import logging, string
from settings import STATIC_PATH
from settings import TEMPLATE_DIR
from defines import USER_AGENT

from google.appengine.ext.webapp import template
from storyengine.model.account import Account
from storyengine.model.receipt import Receipt

#from django import forms
from django import forms
#from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponse
from django.template import Context, loader
import json
import storyengine
import storyengine.model

#from Crypto.Cipher import AES
#import base64
import urllib3
import hashlib

class ReceiptInfoForm(forms.Form):
	CHOICES = (
			('candy', 'candy'),
			('money', 'money'),
			('data', 'data'),
			('gift', 'gift'),
		)
	dataID = forms.CharField(label='dataID',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	category = forms.ChoiceField(label='category',
		choices=CHOICES,
		widget=forms.Select(attrs={'onchange':'get_vehicle_color();'}))
	cost = forms.CharField(label='cost',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))
	towhomID = forms.CharField(label='towhomID',
		widget=forms.TextInput(attrs={'size':'54',
				'maxlength':'100'}))

class ReceiptNewHandler(storyengine.SessionHandler):
	def get(self):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		s_form = ReceiptInfoForm(None)
		context = {'static_path': STATIC_PATH,
			'form':s_form}
		self.render_to_response('form.html',context)
	def post(self): #logout
		accountid = self.session.get('accountid')
		account_ = Account.get_by_accountid(accountid)
		towhom_ = None
		try:
			towhom_ = Account.get_by_accountid(int(towhomID))
		except:
			towhom_ = None
		params = {}
		params['dataID'] = self.request.get('dataID')
		params['cost'] = self.request.get('cost')
		params['receipt_type'] = self.request.get('receipt_type')

		Receipt.new(params,account_,towhom_)
		self.redirect('/'+accountid+'/')

class ReceiptReadHandler(storyengine.SessionHandler):
	def get(self,keyid):
		accountid = self.session.get('accountid')
		account = Account.get_by_accountid(accountid)
		if 1 != account.mod:
			return

		receipt = Receipt.get_by_id(int(keyid))
		context = {'static_path': STATIC_PATH,
			'receipt':receipt,
			'keyid':receipt.key().id()}
		self.render_to_response('receipt_read.html',context)

#unpad = lambda s : s[0:-ord(s[-1])]
#class AESCipher:
#    def __init__( self, key ):
#        self.key = key 
#
#    def decrypt( self, enc ):
#        enc = base64.b64decode(enc)
#        iv = enc[:16]
#        cipher = AES.new(self.key, AES.MODE_CBC, iv )
#        return unpad(cipher.decrypt( enc[16:] ))

class AppReceiptSubmitHandler(webapp2.RequestHandler):
	def post(self): #logout
		if False == (USER_AGENT in self.request.headers["User-Agent"]):
			self.response.out.write(json.dumps({'success':False}))
			return

		facebookid = self.request.get('facebookid')
		account_ = Account.get_by_facebookid(facebookid)
		towhom_ = None
		try:
			towhom_ = Account.get_by_accountid(towhomID)
		except:
			towhom_ = None
		params = {}
		params['id'] = 0
		params['itemcost'] = 0
		params['cost'] = self.request.get('cost')
		params['receipt_type'] = self.request.get('receipt_type')
		if "money" == params['receipt_type']:
			params['receipt_data'] = self.request.get('receipt_data')
			logging.info('receipt_data [%s]', params['receipt_data'])
			receipt_data = params['receipt_data']
			receipt_hash = str(hashlib.md5(str(receipt_data)).hexdigest())

			result = Receipt.all().filter("receipt_hash =", receipt_hash)
			if result != None and result.count() > 0 and result[0].receipt_hash == receipt_hash:
				logging.error('Err! id:[%s] prev existed:[%s]', facebookid, result[0])
			else:
				postdata = {}
				postdata['receipt-data'] = params['receipt_data']
				http = urllib3.PoolManager()
				r = http.request('POST','https://buy.itunes.apple.com/verifyReceipt',
					fields=postdata)
#				r = http.request('POST','https://sandbox.itunes.apple.com/verifyReceipt',
#					fields=postdata)
				t = json.loads(r.data)
				if 0 != int(t['status']) :
					logging.error('ID:[%s] cost:[%s] status:[%s]', str(facebookid), str(params['cost']), str(t['status']))
					return self.response.out.write(json.dumps({'success':False}))

		ret = Receipt.new(params,account_,towhom_)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(ret))


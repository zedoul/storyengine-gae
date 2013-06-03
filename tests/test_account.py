# coding: utf-8
import os

import conftest
import storyengine.category
from storyengine.model.category import Category
from storyengine.model.account import Account

def test_setup():
	conftest.configure()
	return

def test_account_login():
	facebookid = "zedoul@gmail.com"
	access_token = "access_token"
	exp_date = "2113-03-18 07:07:42"
	name = "zedoul"
	ret = Account.api_login(facebookid,access_token,exp_date,name)
	assert True == ret['success']
	assert ret['id']
	assert ret['created']
	assert ret['prices']
	assert ret['money']
	assert ret['candy']
	assert ret['storyIDs']
	assert None != ret['recommend']
	assert None != ret['score']
	assert ret['maintenance']
	assert ret['forceupdate']
	assert ret['score_expiration']
	assert 1 == ret['rank_expiration_days']


# coding: utf-8
import os

import conftest
import storyengine.category
from storyengine.model.category import Category
from storyengine.model.account import Account

def test_setup():
	conftest.configure()
	return

def test_category_index():
	det = Category.api_index('ko')
	assert True == det['success']

def test_category_new():
	facebookid = "zedoul@gmail.com"
	account = Account.get_by_facebookid(facebookid)
	key_name = "TOEIC"
	category = Category.new(key_name,account)
	assert None != category
	return

def test_category_read():
	key_name = "TOEIC"
	category = Category.getter(key_name)
	assert None != category
	return

def test_category_update():
	return

def test_category_del():
	return


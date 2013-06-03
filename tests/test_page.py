# coding: utf-8
import os

import conftest
import storyengine.page
from storyengine.model.story import Page
from storyengine.model.account import Account

def test_setup():
	conftest.configure()
	return

def test_page_index():
	return

def test_page_new():
	facebookid = "zedoul@gmail.com"
	account = Account.get_by_facebookid(facebookid)
	page = Page.new(account)
	assert None != page
	return

def test_page_read():
	return

def test_page_update():
	return

def test_page_del():
	return


# coding: utf-8
import os

import conftest
import storyengine.content
from storyengine.model.content import Content
from storyengine.model.account import Account

def test_setup():
	conftest.configure()
	return

def test_content_index():
	return

def test_content_new():
	facebookid = "zedoul@gmail.com"
	account = Account.get_by_facebookid(facebookid)
	content = Content.new(account)
	assert None != content
	return

def test_content_read():
	return

def test_content_update():
	return

def test_content_del():
	return


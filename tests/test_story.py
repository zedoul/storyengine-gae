# coding: utf-8
import os

import conftest
import storyengine.story
from storyengine.model.story import Story
from storyengine.model.account import Account

def test_setup():
	conftest.configure()
	return

def test_story_index():
	for lang in conftest.langs():
		det = Story.api_index(lang)
		assert True == det['success']

def test_story_new():
	facebookid = "zedoul@gmail.com"
	account = Account.get_by_facebookid(facebookid)
	assert account
	story = Story.new(account)
	story.put()
	assert story
	return story

def test_story_setter():
	story_to_test = test_story_new()
	params = {}
	params['index'] = 1
	story_to_test.setter(params)
	return story_to_test

def test_story_read():
	story_to_test = test_story_setter()
	assert story_to_test
	story = Story.get_by_id(int(story_to_test.key().id()))
	assert story
	assert story.created
	assert story.modified
	assert story.index
	assert story.visible
	assert story.version
	for lang in conftest.langs():
		s = Story.api_read(int(story_to_test.key().id()),lang)
		assert story.name
		assert story.description
	return

def test_story_update():
	return

def test_story_del():
	return


from google.appengine.ext import db
from storyengine.model.story import Story
from storyengine.model.story import Page
from storyengine.model.content import Content

class Locale (db.Model):
	name = db.StringProperty(default=None)
	description = db.TextProperty(default=None)
	language = db.CategoryProperty(choices=set(['en','ko','ja']),required=True)
	story = db.ReferenceProperty(Story,
			default=None,required=True)
	page = db.ReferenceProperty(Page,
			default=None,required=True)
	content = db.ReferenceProperty(Content,
			default=None,required=True)



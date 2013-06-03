from google.appengine.ext import db
import storyengine.model
import datetime
import time

class Achievement (storyengine.model.TransModel):
	def setter(self,req):
		super(Achievement,self).setter(req)


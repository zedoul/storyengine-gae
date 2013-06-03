from google.appengine.ext import db

class Counter (db.Model):
	name = db.StringProperty(required=True)
	count = db.IntegerProperty(required=True,default=0)

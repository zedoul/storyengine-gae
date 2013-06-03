from google.appengine.ext import db

class Trans (db.Model):
	nameen = db.StringProperty(required=True)
	nameko = db.StringProperty(default=None)
	nameja = db.StringProperty(default=None)
	descriptionen = db.TextProperty(default=None)
	descriptionko = db.TextProperty(default=None)
	descriptionja = db.TextProperty(default=None)


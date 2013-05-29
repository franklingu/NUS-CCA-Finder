import urllib
import webapp2
import jinja2
import os
import datetime
import logging


from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

# main page event handler
class MainPage(webapp2.RequestHandler):
  """ Front page for those logged in """
  def get(self):
    user = users.get_current_user()
    if user:  # signed in already
      template_values = {
        'home': self.request.host_url,
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        } 
      template = jinja_environment.get_template('frontuser.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect('/')

# Datastore definitions
class Persons(db.Model):
  """Models a person identified by email"""
  email = db.StringProperty()
  picture = db.BlobProperty()
  name = db.StringProperty()
  gender = db.BooleanProperty()
  year = db.IntegerProperty()
  faculty = db.StringProperty()
  residence = db.StringProperty()
  interest = db.StringListProperty()
  picture = db.BlobProperty()
  
class CCA(db.Model):
  """Models a CCA by name location and description"""
  name = db.StringProperty()
  venue = db.StringProperty()
  category = db.StringProperty()
  description = db.StringProperty(multiline=True)
  videolink = db.LinkProperty()
  joined = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)

#need to be more sure about this one
class ImageDisplay(webapp2.RequestHandler):
  def get(self):
    parent_key = db.Key.from_path('Persons', users.get_current_user().email())
    person = db.get(parent_key)
    if person.picture:
      self.response.headers['Content-Type'] = 'image/png'
      self.response.out.write(person.picture)
    else:
      self.response.out.write('No image')

#event handlers
#login event
class Login(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:  # signed in already
      template_values = {
        'home': self.request.host_url,
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        }
      template = jinja_environment.get_template('frontuser.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(users.create_login_url( federated_identity='https://openid.nus.edu.sg/'))

#personal profile
class Profile(webapp2.RequestHandler):
  """ Form for getting and displaying wishlist items. """
  def get(self):
    user = users.get_current_user()
    if user:  # signed in already
      # Retrieve person
      parent_key = db.Key.from_path('Persons', users.get_current_user().email())
      person = db.get(parent_key)
      if person == None:
        #the user has not complete the profile
        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url),
          'complete': False,
          'name': "",
          'gender': "",
          'year': "",
          'faculty': "",
          'residence': "",
          'interests': "None",
          'CCAs1': "",
          'CCAs2': "",
        }
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))
      else:
        #if the user have completed the profile
        query1 = db.GqlQuery("SELECT * FROM CCA WHERE ANCESTOR IS :1 AND CCA_join=True ORDER BY date DESC", parent_key)
        query2 = db.GqlQuery("SELECT * FROM CCA WHERE ANCESTOR IS :1 AND CCA_join=False ORDER BY date DESC", parent_key)
        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url),
          'complete': True,
          'name': person.name,
          'gender': person.gender,
          'year': person.year,
          'faculty': person.faculty,
          'residence': person.residence,
          'interests': person.interest,
          'CCAs1': query1,
          'CCAs2': query2,
        }
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

#edit personal profile
class EditProfile(webapp2.RequestHandler):
  """display edit profile page and post the inputs to db"""
  def get(self): #get mothed to display the page
    user = users.get_current_user()
    if user: #logged in already
      # Retrieve person
      parent_key = db.Key.from_path('Persons', users.get_current_user().email())
      person = db.get(parent_key)
      if person == None:
        #the user has not complete the profile
        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url),
          'complete': False,
          'name': "",
          'gender': "",
          'year': "",
          'faculty': "",
          'residence': "",
          'interest': "None",
        }
        template = jinja_environment.get_template('editprofile.html')
        self.response.out.write(template.render(template_values))
      else:
        #if the user have completed the profile
        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url),
          'complete': True,
          'name': person.name,
          'gender': person.gender,
          'year': person.year,
          'faculty': person.faculty,
          'residence': person.residence,
          'interest': person.interest,
        }
        template = jinja_environment.get_template('editprofile.html')
        self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

  def post(self):
    """to get the input and store them in db"""
    parent_key = db.Key.from_path('Persons', users.get_current_user().email())
    person = db.get(parent_key)
    if person == None: #store this person in the db if it is not in db yet
      newProfile = Persons(key_name=users.get_current_user().email())
      newProfile.email = users.get_current_user().email()
      newProfile.put()
    
    newProfile = Persons(key_name=users.get_current_user().email())
    newProfile.name = self.request.get('person_name')

    if self.request.get('face_img'):
      picture = images.resize(self.request.get('face_img'), 200, 200)
      newProfile.picture = db.Blob(picture)
    else: 
      self.redirect('/errormsg' + "?error=NoFileChosen&continue_url=profile")

    if self.request.get('person_gender') == "Male":
      newProfile.gender = True
    else:
      newProfile.gender = False 

    newProfile.year = int(self.request.get('person_year'))
    newProfile.faculty = self.request.get('person_faculty') 
    newProfile.residence = self.request.get('person_residence')
    interesttags = self.request.get('person_interest')
    newProfile.interest = interesttags.split()
    err_exist = False
    if len(newProfile.interest) > 6:
      err_exist = True
      msg = "?error=TooManyInterests&continue_url=profile"
    if newProfile.name == "None" or newProfile.name == "default" or newProfile.name == "":
      err_exist = True
      msg = "?error=NameIsIllegal&continue_url=profile"

    if err_exist:
      self.redirect('/errormsg'+msg)
    else:
      newProfile.put()
      self.redirect('/profile')

#display search page to user for searching
class Search(webapp2.RequestHandler):
  """ Display search page """
  def get(self):
    user = users.get_current_user()
    if user:  # signed in already
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        } 
      template = jinja_environment.get_template('search.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

#search db and for display html
class Display(webapp2.RequestHandler):
  """ Displays search result """
  def post(self):

    target = self.request.get('friend_email').rstrip()
    # Retrieve person
    parent_key = db.Key.from_path('Persons', target)

    query1 = db.GqlQuery("SELECT * FROM CCA WHERE ANCESTOR IS :1 AND CCA_join = True ORDER BY date DESC", parent_key)
    query2 = db.GqlQuery("SELECT * FROM CCA WHERE ANCESTOR IS :1 AND CCA_join = False ORDER BY date DESC", parent_key)

    template_values = {
      'user_mail': users.get_current_user().email(),
      'target_mail': target,
      'logout': users.create_logout_url(self.request.host_url),
      'CCAs1': query1,
      'CCAs2': query2,
      } 
    template = jinja_environment.get_template('display.html')
    self.response.out.write(template.render(template_values))

class View(webapp2.RequestHandler):
  """enable user see the view page"""
  def get(self):
    #things to put in
    user = users.get_current_user()
    if user:  # signed in already

      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        } 

      template = jinja_environment.get_template('viewguide.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

class ViewByHall(webapp2.RequestHandler):
  """request handler for view by hall page"""
  def get(self):
    user = users.get_current_user()
    if user:
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        }
      template = jinja_environment.get_template('viewbyhalls.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

class ViewByCategory(webapp2.RequestHandler):
  """request handler for view by category search"""
  def get(self):
    user = users.get_current_user()
    if user:
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        }
      template = jinja_environment.get_template('viewbycategory.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

class ViewBySearch(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url)
        }
      template = jinja_environment.get_template('viewbysearch.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)


class ViewCCA(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user().email()
    if user:
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url)
        }
      template = jinja_environment.get_template('viewCCA.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

class ErrorDealing(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user().email()
    if user:
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        'error': self.request.get('error'),
        'continue_url': self.request.get('continue_url'),
        }
      template = jinja_environment.get_template('errormsg.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

app = webapp2.WSGIApplication([('/index', MainPage),
                               ('/profile', Profile),
                               ('/editprofile', EditProfile),
                               ('/Login',Login),
                               ('/search', Search),
                               ('/display', Display),
                               ('/view', View),
                               ('/viewbyhall',ViewByHall),
                               ('/viewbycategory',ViewByCategory),
                               ('/viewbysearch',ViewBySearch),
                               ('/img', ImageDisplay),
                               ('/errormsg',ErrorDealing)],
                              debug=True)

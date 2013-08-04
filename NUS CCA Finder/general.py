import urllib
import webapp2
import jinja2
import os
import datetime


from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users
from cca import CCA_item
from cca import miniCCA

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

# Datastore definitions
#user profiles
class Persons(db.Model):
  """Models a person identified by email"""
  email = db.StringProperty()
  name = db.StringProperty()
  gender = db.BooleanProperty()
  year = db.IntegerProperty()
  faculty = db.StringProperty()
  residence = db.StringProperty()
  interest = db.StringListProperty()

#define user pic
class Picture(db.Model):
  """picture: child of a person to store profile picture"""
  content = db.BlobProperty()

#event handlers
# host page
class HostPage(webapp2.RequestHandler):
  """ Handler for the front page."""
  def get(self):
    template = jinja_environment.get_template('front.html')
    self.response.out.write(template.render())

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
      template = jinja_environment.get_template('front.html')
      self.response.out.write(template.render())

#main-pic.html--for simple ajax
class MainPic(webapp2.RequestHandler):
  """display main pic"""
  def get(self):
    template = jinja_environment.get_template('main-pic.html')
    self.response.out.write(template.render())

#personal profile--login required
class Profile(webapp2.RequestHandler):
  """ personal profiles """
  def get(self):
    user = users.get_current_user()
    if user:  # signed in already
      # Retrieve person
      person_key = db.Key.from_path('Persons', users.get_current_user().email())
      person = db.get(person_key)
      if person == None:
        #the user has not complete the profile
        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url),
          'complete': False,
          'person': person,
          'CCAs1': "",
          'CCAs2': "",
        }
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))
      else:
        #if the user have completed the profile
        query1 = db.GqlQuery("SELECT * FROM miniCCA WHERE ANCESTOR IS :1 AND status='joined'", person_key)
        query2 = db.GqlQuery("SELECT * FROM miniCCA WHERE ANCESTOR IS :1 AND status='interested'", person_key)
        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url),
          'complete': True,
          'person': person,
          'CCAs1': query1,
          'CCAs2': query2,
        }
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

#edit personal profile--login-required
class EditProfile(webapp2.RequestHandler):
  """display edit profile page and post the inputs to db"""
  def get(self): #get mothed to display the page
    user = users.get_current_user()
    if user: #there is no way to call this directly???
      self.redirect('/profile#editprofile')
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
    newProfile.email = users.get_current_user().email()
    if self.request.get('person_name')!='':
      newProfile.name=self.request.get('person_name')
    #check an img
    if self.request.get('face_img')!='':
      try:
        img = images.resize(self.request.get('face_img'), 200, 200)
        picture = Picture(parent=parent_key)
        picture.content = db.Blob(img)
        #delete prev uploads
        photo = db.GqlQuery("SELECT * FROM Picture WHERE ANCESTOR IS :1", parent_key)
        for item in photo:
          item.delete()
        #save new one
        picture.put()
      except TypeError: #does not redirect now
        self.redirect("/errormsg?error=Not a supported type&continue_url=profile")
      except:
        self.redirect("/errormsg?error=Unexpected error&continue_url=profile")
    else: #cannot detect no-file situation
      err_exist = True
      msg = "?error=No File Chosen&continue_url=profile"
    #determine gender
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
      msg = "?error=Too Many Interests&continue_url=profile"
    if newProfile.name == "None" or newProfile.name == "default" or newProfile.name == "":
      err_exist = True
      msg = "?error=Name Is Illegal&continue_url=profile"

    if err_exist:
      self.redirect('/errormsg'+msg)
    else:
      newProfile.put()
      self.redirect('/profile')

#display search page to user for searching
class Friendster(webapp2.RequestHandler):
  """ Display search page """
  def get(self):
    user = users.get_current_user()
    if user:  # signed in already
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        } 
      template = jinja_environment.get_template('friendster-search.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

  def post(self):
    target = self.request.get('friend_email').rstrip()
    # Retrieve person
    parent_key = db.Key.from_path('Persons', target)
    if parent_key!=None:
      query1 = db.GqlQuery("SELECT * FROM miniCCA WHERE ANCESTOR IS :1 AND status = 'interested'", parent_key)
      query2 = db.GqlQuery("SELECT * FROM miniCCA WHERE ANCESTOR IS :1 AND status = 'joined'", parent_key)
      template_values = {
        'user_mail': users.get_current_user().email(),
        'target_mail': target,
        'found': True,
        'logout': users.create_logout_url(self.request.host_url),
        'CCAs1': query1,
        'CCAs2': query2,
      } 
    else:
      template_values = {
        'user_mail': users.get_current_user().email(),
        'target_mail': target,
        'found': False,
      } 
    template = jinja_environment.get_template('friendster-result.html')
    self.response.out.write(template.render(template_values))

#need to be more sure about this one
class ImageDisplay(webapp2.RequestHandler):
  """diaplay user pic from Blob data"""
  def get(self):
    parent_key = db.Key.from_path('Persons', users.get_current_user().email())
    photos = db.GqlQuery("SELECT * FROM Picture WHERE ANCESTOR IS :1", parent_key)

    if photos.count()!=0:
      photo=photos.get()
      self.response.headers['Content-Type'] = 'image/png'
      self.response.out.write(photo.content)
    else:
      self.redirect('/errormsg'+'?error=No Image&continue_url=editprofile')

#recommended cca html fragment
class Recommend(webapp2.RequestHandler):
  """simple ajax part"""
  def get(self):
    recomd = db.GqlQuery("SELECT * FROM CCA_item ORDER BY joined_number DESC LIMIT 6")
    template_values = {
      'recommends': recomd,
    }
    template = jinja_environment.get_template('recommend.html')
    self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication([('/', HostPage),
                               ('/index', MainPage),
                               ('/main-pic', MainPic),
                               ('/profile', Profile),
                               ('/editprofile', EditProfile),                             
                               ('/friendster', Friendster),
                               ('/img', ImageDisplay),
                               ('/recommend-ccas', Recommend)],
                              debug=True)

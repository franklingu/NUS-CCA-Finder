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
  name = db.StringProperty()
  gender = db.BooleanProperty()
  year = db.IntegerProperty()
  faculty = db.StringProperty()
  residence = db.StringProperty()
  interest = db.StringListProperty()
  
class CCA(db.Model):
  """Models a CCA by name location and description"""
  name = db.StringProperty()
  venue = db.StringProperty()
  category = db.StringProperty()
  description = db.StringProperty(multiline=True)
  videolink = db.LinkProperty()
  joined = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)

class Picture(db.Model):
  content = db.BlobProperty()

#need to be more sure about this one
class ImageDisplay(webapp2.RequestHandler):
  def get(self):
    parent_key = db.Key.from_path('Persons', users.get_current_user().email())
    photos = db.GqlQuery("SELECT * FROM Picture WHERE ANCESTOR IS :1", parent_key)
    if photos:
      for photo in photos:
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(photo.content)
    else:
      self.redirect('/error'+'?error=No Image&continue_url=editprofile')

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
        query1 = db.GqlQuery("SELECT * FROM CCA WHERE ANCESTOR IS :1 AND joined='True' ORDER BY date DESC", parent_key)
        query2 = db.GqlQuery("SELECT * FROM CCA WHERE ANCESTOR IS :1 AND joined='False' ORDER BY date DESC", parent_key)
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
          'interest': "",
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
      except TypeError: #does not redirect
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

    query1 = db.GqlQuery("SELECT * FROM CCA WHERE ANCESTOR IS :1 AND joined = 'True' ORDER BY date DESC", parent_key)
    query2 = db.GqlQuery("SELECT * FROM CCA WHERE ANCESTOR IS :1 AND joined = 'False' ORDER BY date DESC", parent_key)

    template_values = {
      'user_mail': users.get_current_user().email(),
      'target_mail': target,
      'logout': users.create_logout_url(self.request.host_url),
      'CCAs1': query1,
      'CCAs2': query2,
      } 
    template = jinja_environment.get_template('display.html')
    self.response.out.write(template.render(template_values))

class ViewGuide(webapp2.RequestHandler):
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

class ViewHalls(webapp2.RequestHandler):
  """view temasek"""
  def get(self):
    user = users.get_current_user()
    if user:
      hall = self.request.get('name')
      if hall=="" or hall==None:
        self.redirect('/errormsg'+'?Illegal Operation&continue_url=index')
      else:
        sports = db.GqlQuery("SELECT * FROM CCA WHERE joined='root' AND venue=:name AND category='sports' ORDER BY date DESC")
        music = db.GqlQuery("SELECT * FROM CCA WHERE joined='root' AND venue=:name AND category='music' ORDER BY date DESC")
        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url),
          }
        template = jinja_environment.get_template(hall+'.html')
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
      name = self.request.get('name')
      venue = self.request.get('venue')
      if name == None or name == "":
        self.redirect('/errormsg'+'?error=Unexpected Error With Get&continue_url=index')

      ccas = db.GqlQuery("SELECT * FROM CCA WHERE joined='root' AND name=:name")
      if ccas:
        if  True:
          template_values = {
            'user_mail': users.get_current_user().email(),
            'logout': users.create_logout_url(self.request.host_url),
            'ccas': ccas,
          }
          template = jinja_environment.get_template('viewcca.html')
          self.response.out.write(template.render(template_values))
        else:
          self.redirect('/errormsg'+'?error=UnexpectedErrorInDB&continue_url=index')
      else:
        self.redirect('/errormsg'+'?error=ItemDoesNotExist&continue_url=index')
    else:
      self.redirect(self.request.host_url)

class AddCCA(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user().email()
    if user:
      #tesing block go here
      if True:
        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url)
          }
        template = jinja_environment.get_template('newcca.html')
        self.response.out.write(template.render(template_values))
      else:
        self.redirect('/errormsg'+'?error=NotAuthorized&continue_url=index')
    else:
      self.redirect(self.request.host_url)

  def post(self):
    #add a cca; checking is not done yet
    name = self.request.get('cca_name')
    if name:
      cca = CCA(key_name=name)
      cca.name = name
      cca.venue = self.request.get('cca_venue')
      cca.category = self.request.get('cca_category')
      cca.description = self.request.get('cca_desc')
      cca_videolink = self.request.get('youtubelink')
      cca.joined = 'root'
      cca.put()
      self.redirect('/index')
    else:
      self.redirect('/errormsg'+'?error=EmptyInput&continue_url=addcca')

class EditCCA(webapp2.RequestHandler):
  """edit profile:only admins can can see"""
  def get(self):
    user = users.get_current_user().email()
    if user:
      if True: #we set the name as a key_name, so we will always find it
        cca_name = self.request.get('name')
        cca_venue = self.request.get('venue')
        cca = db.GqlQuery("SELECT * FROM CCA WHERE joined='root' AND name=:cca_name AND venue=:cca_venue")
        if cca:
          if cca.count()==1:
            template_values = {
              'user_mail': users.get_current_user().email(),
              'logout': users.create_logout_url(self.request.host_url),
              'cca': cca,
            }
            template = jinja_environment.get_template('editcca.html')
            self.response.out.write(template.render(template_values))
          elif cca.count()>1:
            self.redirect('/errormsg'+'?error=UnexpectedErrorInDB&continue_url=index')
        else:
          self.redirect('/errormsg'+'?error=ItemDoesNotExist&continue_url=index')
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
                               ('/view', ViewGuide),
                               ('/viewbyhall',ViewByHall),
                               ('/viewbycategory',ViewByCategory),
                               ('/viewbysearch',ViewBySearch),
                               ('/viewhalls',ViewHalls),
                               ('/addcca',AddCCA),
                               ('/viewcca',ViewCCA),
                               ('/editcca',EditCCA),
                               ('/img', ImageDisplay),
                               ('/errormsg',ErrorDealing)],
                              debug=True)

import urllib
import webapp2
import jinja2
import os


from google.appengine.ext import db
from google.appengine.api import users
from datetime import datetime

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class CCA_item(db.Model):
  """Models a CCA by name location and description"""
  name = db.StringProperty()
  venue = db.StringProperty()
  category = db.StringProperty()
  description = db.StringProperty(multiline=True)
  videolink = db.StringProperty()
  joined_number = db.IntegerProperty() #show how many people have joined, a standard for sorting


class CCA_comments(db.Model):
  """a comment for CCAitem"""
  author = db.StringProperty() #annonymous if the author chooses to do this
  date = db.StringProperty()
  comment = db.StringProperty(multiline=True) #content of the comment


class miniCCA(db.Model):
  """mini cca: less space to show a person is interested or joining a cca"""
  name_venue = db.StringProperty() #this is the identifier
  join = db.BooleanProperty() #true for join; false for interest

#view cca: login not required
class ViewCCA(webapp2.RequestHandler):
  def get(self):
    cca_name = self.request.get('name')
    cca_venue = self.request.get('venue')
    if cca_name == None or cca_name == "":
      self.redirect('/errormsg'+'?error=Unexpected Error With Get&continue_url=index')
    ccas = db.GqlQuery("SELECT * FROM CCA_item WHERE name=:1 AND venue=:2", cca_name, cca_venue)
    if ccas:
      if True:
        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url),
          'cca': ccas.get(),
          }
        template = jinja_environment.get_template('/viewcca.html')
        self.response.out.write(template.render(template_values))
      else:
        self.redirect('/errormsg'+'?error=UnexpectedErrorInDB&continue_url=index')
    else:
      self.redirect('/errormsg'+'?error=ItemDoesNotExist&continue_url=index')

#add cca: admin required
class AddCCA(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user().email()
    if user:
      if user=='a0105750@nus.edu.sg' or user=='test@example.com':
        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url)
          }
        template = jinja_environment.get_template('newcca.html')
        self.response.out.write(template.render(template_values))
      else:
        self.redirect('/errormsg'+'?error=Not Authorized&continue_url=index')
    else:
      self.redirect('/errormsg'+'?error=Login First Please&continue_url=index')

  def post(self):
    #add a cca; checking is not done yet
    name = self.request.get('cca_name')
    venue = self.request.get('cca_venue')
    if name!='' and venue!='':
      cca = CCA_item(key_name=(name+venue))
      cca.name = name
      cca.venue = venue
      cca.category = self.request.get('cca_category')
      cca.description = self.request.get('cca_desc')
      cca.videolink = self.request.get('youtubelink')
      cca.joined = 'root'
      #check whether a cca with the same name exist or not, to be implemented
      cca.put()
      self.redirect('/CCA/add')
    else:
      self.redirect('/errormsg'+'?error=Empty Input&continue_url=CCA/add')

#add comments: login not required for now
class AddComments(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user().email()
    if user:
      author_email = user
      person_key = db.Key.from_path('Persons', author_email)
      person = db.get(person_key)
      comment = CCA_comments()
      comment.author = person.name
      comment.content = self.request.get('content')
      comment.date = str(datetime.now())
    else:
      author_email = ''

#edit cca: admin required
class EditCCA(webapp2.RequestHandler):
  """edit profile:only admins can can see"""
  def get(self):
    user = users.get_current_user().email()
    if user:
      if user=='a0105750@nus.edu.sg' or user=='test@example.com':
        cca_name = self.request.get('name')
        cca_venue = self.request.get('venue')
        ccas = db.GqlQuery("SELECT * FROM CCA_item WHERE joined='root' AND name=:1 AND venue=:2", cca_name, cca_venue)
        if ccas:
          if ccas.count()==1:
            template_values = {
              'user_mail': users.get_current_user().email(),
              'logout': users.create_logout_url(self.request.host_url),
              'cca': ccas.get(),
            }
            template = jinja_environment.get_template('editcca.html')
            self.response.out.write(template.render(template_values))
          else:
            self.redirect('/errormsg'+'?error=Server Erorr&continue_url=index')
        else:
          self.redirect('/errormsg'+'?error=Item Does Not Exist&continue_url=index')
    else:
      self.redirect(self.request.host_url)

  def post(self):
    name = self.request.get('cca_name')
    venue = self.request.get('cca_venue')
    if name!='' and venue!='':
      cca = CCA_item(key_name=name)
      cca.name = name
      cca.venue = self.request.get('cca_venue')
      cca.category = self.request.get('cca_category')
      cca.description = self.request.get('cca_desc')
      cca_videolink = self.request.get('youtubelink')
      cca.joined = 'root'
      cca.put()
      self.redirect('/index')
    else:
      self.redirect('/errormsg'+'?error=EmptyInput&continue_url=index')

#show interst || join a cca: login required 
class ShowInterest(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user().email()
    if user:
      cca_name = self.request.get('name')
      cca_venue = self.request.get('venue')
      interested = self.request.get('join')
      ccas = db.GqlQuery("SELECT * FROM CCA_item WHERE joined='root' AND name=:1 AND venue=:2", cca_name, cca_venue)
      if ccas:
        cca=ccas.get()
        parent_key = db.Key.from_path('Persons', users.get_current_user().email())
        target = miniCCA(parent=parent_key)
        if interested=='true':
          target.joined='interested'
        elif interested=='false':
          target.joined='joined'
        else:
          self.redirect('/errormsg?error=Request is illegal&continue_url=profile')
        target.name=cca.name
        target.venue=cca.venue #these two should be enough
        target.put()
        self.redirect('/profile')
      else:
        self.redirect('/errormsg?error=CCA Not Found&continue_url=index')
    else:
      self.redirect(self.request.host_url)


app = webapp2.WSGIApplication([('/CCA/view', ViewCCA),
                               ('/CCA/add', AddCCA),
                               ('/CCA/edit', EditCCA),
                               ('/interest', ShowInterest)],
                              debug=True)
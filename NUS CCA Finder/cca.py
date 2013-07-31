import urllib
import webapp2
import jinja2
import os
import logging

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
  joined_number = db.IntegerProperty(default=0) #show how many people have joined, a standard for sorting


class CCA_comments(db.Model):
  """a comment for CCAitem"""
  author = db.StringProperty() #annonymous if the author chooses to do this
  date = db.StringProperty()   
  comment = db.StringProperty(multiline=True) #content of the comment


class miniCCA(db.Model):
  """mini cca: less space to show a person is interested or joining a cca"""
  name =db.StringProperty()   #name
  venue = db.StringProperty() #venue
  status = db.StringProperty() #true for join; false for interest

#view cca: login not required
class ViewCCA(webapp2.RequestHandler):
  def get(self):
    cca_name = self.request.get('name')
    cca_venue = self.request.get('venue')
    if cca_name == "" or cca_venue == "":
      self.redirect('/errormsg'+'?error=Unexpected Error With Get&continue_url=index')
      #logging.info('not enough input')
    else:
      ccas = db.GqlQuery("SELECT * FROM CCA_item WHERE name=:1 AND venue=:2", cca_name, cca_venue)
      person_key = db.Key.from_path('Persons', users.get_current_user().email())
      num = 0
      for cca in ccas:
        num += 1
      if num == 1:
        minis = db.GqlQuery("SELECT * FROM miniCCA WHERE name=:1 AND venue=:2 AND ANCESTOR IS :3", cca_name, cca_venue , person_key)
        no_mini=0
        for mini in minis:
          no_mini+=1
        logging.info("no_mini is "+str(no_mini))
        if no_mini==0:
          interest='no'
          join='no'
        elif no_mini==2:
          interest='yes'
          join='yes'
        elif no_mini==1:
          if minis.get().status=='interested':
            interest='yes'
            join='no'
          else:
            interest='no'
            join='yes'
        else:
          interest='yes'
          join='yes'
          self.redirect('/errormsg'+'?error=Unexpected error: Too many entities found&continue_url=view/guide')

        if users.is_current_user_admin():
          admin='yes'
        else:
          admin='no'

        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url),
          'cca': ccas.get(),
          'interest': interest,
          'join': join,
          'admin': admin,
        }
        template = jinja_environment.get_template('/viewcca.html')
        self.response.out.write(template.render(template_values))
      elif num == 0:
        self.redirect('/view/guide')
      else:
        self.redirect('/errormsg'+'?error=Unexpected error: Database error&continue_url=view/guide')
      #logging.info('end of handler')

  def post(self):
    user = users.get_current_user().email()
    if user:
      cca_name = self.request.get('name')
      cca_venue = self.request.get('venue')
      status = self.request.get('status')
      person_key = db.Key.from_path('Persons', user)
      if person_key:
        miniCCA_query = db.GqlQuery("SELECT * FROM miniCCA WHERE name=:1 AND venue=:2 AND status=:3 AND ANCESTOR IS :4", cca_name, cca_venue, status, person_key)
        num1=0
        for mini in miniCCA_query:
          num1+=1
        #logging.info('num1 is '+str(num1))
        if num1==0: 
          ccas = db.GqlQuery("SELECT * FROM CCA_item WHERE name=:1 AND venue=:2", cca_name, cca_venue)
          num2 = 0
          for cca in ccas:
            num2 += 1
          if num2==1:
            cca=ccas.get()
            parent_key = db.Key.from_path('Persons', users.get_current_user().email())
            target = miniCCA(parent=parent_key)
            if status=='interested':
              target.status='interested'
              err_exist=False
            elif status=='joined':
              target.status='joined'
              err_exist=False
            else:
              self.redirect('/errormsg?error=Request is illegal&continue_url=profile')
              err_exist=True
            if not err_exist:
              target.name=cca_name
              target.venue=cca_venue
              if status=='interested':
                cca.joined_number+=1
              else:
                cca.joined_number+=2
              cca.put()
              target.put()
              self.redirect('/profile')
            else:
              pass
          elif num2==0:
            self.redirect('/errormsg'+'?error=Unexpected error: Data coruption&continue_url=view/guide')
          else:
            self.redirect('/errormsg'+'?error=Unexpected error: Database error&continue_url=view/guide')    
        elif num1==1:
          self.redirect('/profile')
        else:
          self.redirect('/errormsg'+'?error=Unexpected error&continue_url=index')
      else:
        self.redirect('/errormsg'+'error=Login first&continue_url=index')
    else:
      self.redirect('/errormsg'+'?error=Login First Please&continue_url=index')

#add cca: admin required
class AddCCA(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user().email()
    if user:
      if users.is_current_user_admin():
        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url)
          }
        template = jinja_environment.get_template('newcca.html')
        self.response.out.write(template.render(template_values))
      else:
        self.redirect('/errormsg'+'?error=Not Authorized&continue_url=index')
    else:
      self.redirect('/profile')

  def post(self):
    #add a cca; checking is not done yet
    if users.is_current_user_admin():
      name = self.request.get('cca_name')
      venue = self.request.get('cca_venue')
      if name!='' and venue!='':
        cca = CCA_item(key_name=(name+venue))
        cca.name = name
        cca.venue = venue
        cca.category = self.request.get('cca_category')
        cca.description = self.request.get('cca_description')
        cca.videolink = self.request.get('youtubelink')
        cca.joined = 'root'
        #check whether a cca with the same name exist or not, to be implemented
        cca.put()
        self.redirect('/CCA/add')
      else:
        self.redirect('/errormsg'+'?error=Empty Input&continue_url=CCA/add')
    else:
      self.redirect('/errormsg'+'?error=Not authorized&continue_url=index')

#add comments: login not required for now
class AddComments(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user().email()
    if user:
      person_key = db.Key.from_path('Persons', user)
      content = self.request.get('content')
      if len(content)<=6 or len(content)>=200:
        self.redirect('/errormsg'+'?error=Input is short or too long&continue_url=view/guide')
      else:
        this_comment = CCA_comments()
        this_comment.comment = content
        this_comment.date = str(datetime.now())
        if person_key:
          person = db.get(person_key)
          this_comment.author = person.name
        else:
          this_comment.author = 'annonymous'
        this_comment.put()
        self.redirect('/view/guide')
    else:
      self.redirect('/errormsg'+'error=You need to login first&continue_url=view/guide')

#edit cca: admin required
class EditCCA(webapp2.RequestHandler):
  """edit profile:only admins can can see"""
  def get(self):
    user = users.get_current_user().email()
    if user:
      if users.is_current_user_admin():
        cca_name = self.request.get('name')
        cca_venue = self.request.get('venue')
        ccas = db.GqlQuery("SELECT * FROM CCA_item WHERE name=:1 AND venue=:2", cca_name, cca_venue)
        num = 0
        for cca in ccas:
          num += 1
        if num==1:
          template_values = {
            'user_mail': users.get_current_user().email(),
            'logout': users.create_logout_url(self.request.host_url),
            'cca': ccas.get(),
          }
          template = jinja_environment.get_template('editcca.html')
          self.response.out.write(template.render(template_values))
        elif num>1:
          self.redirect('/errormsg'+'?error=Server Erorr&continue_url=index')
        else:
          self.redirect('/errormsg'+'?error=Item Does Not Exist&continue_url=index')
      else:
        self.redirect('/errormsg' + '?error=Not authorized&continue_url=index')
    else:
      self.redirect('/errormsg' + '?error=Not authorized&continue_url=view/guide')

  def post(self):
    name = self.request.get('cca_name')
    venue = self.request.get('cca_venue')
    if name!='' and venue!='':
      cca = CCA_item(key_name=str(name+venue))
      cca.name = name
      cca.venue = self.request.get('cca_venue')
      cca.category = self.request.get('cca_category')
      cca.description = self.request.get('cca_description')
      cca.videolink = self.request.get('youtubelink')
      cca.put()
      self.redirect('/index')
    else:
      self.redirect('/errormsg'+'?error=EmptyInput&continue_url=index')

#search CCA: mode-basic, advanced, (interactive)
class SearchCCA(webapp2.RequestHandler):
  """search for CCAs"""
  def get(self):
    user = users.get_current_user().email()
    if user:
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url)
      }
      template = jinja_environment.get_template('search_cca.html')
      self.response.out.write(template.render(template_values))
    else:
      template_values = {
        'user_mail': '',
        'logout': users.create_logout_url(self.request.host_url)
      }
      template = jinja_environment.get_template('searchCCA.html')
      self.response.out.write(template.render(template_values))

  def post(self):
    try:
      mode = self.request.get('method')
      if mode=='basic':
        logging.info("here is basic")
        query_basic = self.request.get('search_cca_basic')
        ccas = db.GqlQuery("SELECT * from CCA_item WHERE name=:1", query_basic)
        logging.info("pass gql")
        template_values = {
          'user_mail': users.get_current_user().email(),
          'logout': users.create_logout_url(self.request.host_url),
          'search_result': ccas,
        }
        template = jinja_environment.get_template('search_cca_result.html')
        self.response.out.write(template.render(template_values))
      elif mode=='advanced':
        query_name = self.request.get('search_cca_advanced_name')

      else:
        self.redirect('/errormsg'+'?error=Illegal url&continue_url=CCA/search')
    except:
      self.redirect('/errormsg'+'?error=Unexpected error&continue_url=CCA/search')


app = webapp2.WSGIApplication([('/CCA/view', ViewCCA),
                               ('/CCA/add', AddCCA),
                               ('/CCA/edit', EditCCA),
                               ('/CCA/search', SearchCCA),
                               ('/CCA/addcomment', AddComments)],
                              debug=True)
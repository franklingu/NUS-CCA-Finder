import urllib
import webapp2
import jinja2
import os
import datetime
import logging


from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users
from cca import CCA_item

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class ViewGuide(webapp2.RequestHandler):
  """enable user see the view page"""
  def get(self):
    ccas=db.GqlQuery("SELECT * from CCA_item")
    template_values = {
      'user_mail': users.get_current_user().email(),
      'logout': users.create_logout_url(self.request.host_url),
      'ccas': ccas,
      } 
    template = jinja_environment.get_template('/view/viewguide.html')
    self.response.out.write(template.render(template_values))

class ViewHalls(webapp2.RequestHandler):
  """request handler for view by hall page"""
  def get(self):
    template_values = {
      'user_mail': users.get_current_user().email(),
      'logout': users.create_logout_url(self.request.host_url),
      }
    template = jinja_environment.get_template('/view/viewbyhalls.html')
    self.response.out.write(template.render(template_values))

class ViewByHall(webapp2.RequestHandler):
  """view halls: one by one"""
  def get(self):
    hall = self.request.get('hall')
    if not (hall=='Temasek' or hall=='Eusoff' or hall=='Kent Ridge' or hall=='King Edward' or hall=='Raffles' or hall=='Sheares' or hall=='UTown' or hall=='Campus'):
      self.redirect('/errormsg'+'?error=Illegal Link&continue_url=index')
    else:
      sports = db.GqlQuery("SELECT * FROM CCA_item WHERE venue=:1 AND category='sports' ORDER BY joined_number DESC", hall)
      music = db.GqlQuery("SELECT * FROM CCA_item WHERE venue=:1 AND category='music' ORDER BY joined_number DESC", hall)
      dance = db.GqlQuery("SELECT * FROM CCA_item WHERE venue=:1 AND category='dance' ORDER BY joined_number DESC", hall)
      tech = db.GqlQuery("SELECT * FROM CCA_item WHERE venue=:1 AND category='tech' ORDER BY joined_number DESC", hall)
      arts = db.GqlQuery("SELECT * FROM CCA_item WHERE venue=:1 AND category='arts' ORDER BY joined_number DESC", hall)
      drama = db.GqlQuery("SELECT * FROM CCA_item WHERE venue=:1 AND category='drama' ORDER BY joined_number DESC", hall)
      others = db.GqlQuery("SELECT * FROM CCA_item WHERE venue=:1 AND category='others' ORDER BY joined_number DESC", hall)
      #num_tech=0
      #for cca in tech:
      #  num_tech+=1
      #logging.info('tech has '+str(num_tech))
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        'sports': sports,
        'music': music,
        'tech': tech,
        'dance': dance,
        'arts': arts,
        'drama': drama,
        'others': others,
        }
      template = jinja_environment.get_template('/view/halls/'+hall+'.html')
      self.response.out.write(template.render(template_values))

class ViewCategories(webapp2.RequestHandler):
  """request handler for view by category search"""
  def get(self):
    template_values = {
      'user_mail': users.get_current_user().email(),
      'logout': users.create_logout_url(self.request.host_url),
      }
    template = jinja_environment.get_template('/view/viewbycategory.html')
    self.response.out.write(template.render(template_values))

class ViewByCategory(webapp2.RequestHandler):
  """view categoris: one by one"""
  def get(self):
    category = self.request.get('category')
    logging.info('category is '+category)
    if not (category=='sports' or category=='music' or category=='arts' or category=='dance' or category=='tech' or category=='drama' or category=='others'):
      self.redirect('/errormsg'+'?error=Illegal Link&continue_url=index')
    else:
      # the following method is should be replaced by Ajax
      eusoff = db.GqlQuery("SELECT * FROM CCA_item WHERE venue='Eusoff' AND category=:1 ORDER BY joined_number DESC", category)
      ke = db.GqlQuery("SELECT * FROM CCA_item WHERE venue='King Edward' AND category=:1 ORDER BY joined_number DESC", category)
      kr = db.GqlQuery("SELECT * FROM CCA_item WHERE venue='Kent Ridge' AND category=:1 ORDER BY joined_number DESC", category)
      raffles = db.GqlQuery("SELECT * FROM CCA_item WHERE venue='Raffles' AND category=:1 ORDER BY joined_number DESC", category)
      sheares = db.GqlQuery("SELECT * FROM CCA_item WHERE venue='Sheares' AND category=:1 ORDER BY joined_number DESC", category)
      temasek = db.GqlQuery("SELECT * FROM CCA_item WHERE venue='Temasek' AND category=:1 ORDER BY joined_number DESC", category)
      utown = db.GqlQuery("SELECT * FROM CCA_item WHERE venue='Utown' AND category=:1 ORDER BY joined_number DESC", category)
      campus = db.GqlQuery("SELECT * FROM CCA_item WHERE venue='Campus' AND category=:1 ORDER BY joined_number DESC", category)
      num_eusoff=0
      for cca in eusoff:
        num_eusoff+=1
      logging.info('num_eusoff is '+str(num_eusoff))
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        'eusoff': eusoff,
        'ke': ke,
        'kr': kr,
        'raffles': raffles,
        'sheares': sheares,
        'temasek': temasek,
        'utown': utown,
        'campus': campus,
        }
      template = jinja_environment.get_template('/view/categ/'+category+'.html')
      self.response.out.write(template.render(template_values))

class ViewSearch(webapp2.RequestHandler):
  def get(self):
    template_values = {
      'user_mail': users.get_current_user().email(),
      'logout': users.create_logout_url(self.request.host_url)
      }
    template = jinja_environment.get_template('/view/viewbysearch.html')
    self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/view/guide', ViewGuide),
	                             ('/view/all-halls',ViewHalls),
  	                           ('/view/hall',ViewByHall),
  	                           ('/view/all-categories',ViewCategories),
  	                           ('/view/category',ViewByCategory),
                               ('/view/search',ViewSearch)],
                                debug=True)

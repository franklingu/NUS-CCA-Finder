import urllib
import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class GoogleSEOHandler(webapp2.RequestHandler):
  """Display a page if request is not found"""
  def get(self):
    template = jinja_environment.get_template('google6af4498b66c997cc.html')
    self.response.out.write(template.render())

class SiteMapHandler(webapp2.RequestHandler):
  """Display the site map"""
  def get(self):
  	template = jinja_environment.get_template('sitemap.xml')
  	self.response.out.write(template.render())

app = webapp2.WSGIApplication([('/google6af4498b66c997cc.html', GoogleSEOHandler),
	                             ('/sitemap.xml', SiteMapHandler)],
                              debug=True)
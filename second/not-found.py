import urllib
import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class NotFoundHandler(webapp2.RequestHandler):
  """Display a page if request is not found"""
  def get(self):
    template = jinja_environment.get_template('not-found.html')
    self.response.out.write(template.render())
    

app = webapp2.WSGIApplication([('/.*', NotFoundHandler)],
                              debug=True)
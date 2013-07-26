import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class MainPage(webapp2.RequestHandler):
  """ Handler for the front page."""
  def get(self):
    template = jinja_environment.get_template('front.html')
    self.response.out.write(template.render())

class MainPic(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('main-pic.html')
    self.response.out.write(template.render())
 
      
app = webapp2.WSGIApplication([('/', MainPage),
	                             ('/main-pic', MainPic)],
                              debug=True)

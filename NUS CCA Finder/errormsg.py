import urllib
import webapp2
import jinja2
import os

from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class ErrorDealing(webapp2.RequestHandler):
  def get(self):
    template_values = {
      'user_mail': users.get_current_user().email(),
      'logout': users.create_logout_url(self.request.host_url),
      'error': self.request.get('error'),
      'continue_url': self.request.get('continue_url'),
      }
    template = jinja_environment.get_template('errormsg.html')
    self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication([('/errormsg', ErrorDealing)],
                              debug=True)

      
import urllib
import webapp2

from google.appengine.api import users

class LoginHandler(webapp2.RequestHandler):
  """ Redirect users to different OpenId platforms for login."""
  def get(self):
    url = self.request.GET.get('continue_url')
    if url=="" or url==None:
      continue_url = self.request.GET.get("continue")
    else:
      continue_url = url
    openid_url = self.request.GET.get('openid_url')
    if openid_url:
      if openid_url == 'NUS':
        self.redirect(users.create_login_url(continue_url, None, federated_identity='https://openid.nus.edu.sg/'))
      elif openid_url == 'Google':
      	self.redirect(users.create_login_url(continue_url, None ,federated_identity='https://www.google.com/accounts/o8/id'))
      else:
      	self.redirect(users.create_login_url(continue_url, None, federated_identity='https://openid.nus.edu.sg/'))
    else:    
      self.redirect(users.create_login_url(continue_url, None, federated_identity='https://openid.nus.edu.sg/'))

app = webapp2.WSGIApplication([('/_ah/login_required', LoginHandler)],
                              debug=True)
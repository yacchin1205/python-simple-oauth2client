from __future__ import absolute_import

import cherrypy
import os
import sys
import threading
import traceback
import webbrowser

from oauthlib.oauth2.rfc6749.errors import (
    MismatchingStateError,
    MissingTokenError
)
from requests_oauthlib import OAuth2Session


class SimpleOAuthClientAuth:
    def __init__(self, client_id, client_secret,
                 authorize_uri, fetch_token_uri,
                 scope, redirect_uri, verify_ssl=True,
                 state=None, success_html=None,
                 failure_html=None):
        """ Initialize the OAuth2Session """
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_uri = authorize_uri
        self.fetch_token_uri = fetch_token_uri
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.verify_ssl = verify_ssl
        self.success_html = success_html if success_html else """
            <h1>You are now authorized to access the SimpleOAuthClient API!</h1>
            <h3>Access Token: {access_token}</h3>
            <h4>You can close this window</h4>"""
        self.failure_html = failure_html if failure_html else """
            <h1>ERROR: %s</h1><br/><h3>You can close this window</h3>%s"""
        # Ignore when the SimpleOAuthClient API doesn't return the actual scope granted,
        # even though this goes against rfc6749:
        #     https://github.com/idan/oauthlib/blob/master/oauthlib/oauth2/rfc6749/parameters.py#L392
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = 'true'
        self.token = None
        self.state = state
        self.oauth = OAuth2Session(
            self.client_id, scope=self.scope, redirect_uri=self.redirect_uri,
            state=self.state)

    def authorize_url(self):
        """
        Build the authorization url and save the state. Return the
        authorization url
        """
        url, self.state = self.oauth.authorization_url(self.authorize_uri)
        return url

    def fetch_token(self, code, state):
        """
        Fetch the token, using the verification code. Also, make sure the state
        received in the response matches the one in the request. Returns the
        access_token.
        """
        if self.state != state:
            raise MismatchingStateError()
        self.token = self.oauth.fetch_token(self.fetch_token_uri, code=code,
                                            client_secret=self.client_secret,
                                            verify=self.verify_ssl)
        return self.token['access_token']

    def browser_authorize(self):
        """
        Open a browser to the authorization url and spool up a CherryPy
        server to accept the response
        """
        url = self.authorize_url()
        # Open the web browser in a new thread for command-line browser support
        threading.Timer(1, webbrowser.open, args=(url,)).start()
        cherrypy.quickstart(self)

    @cherrypy.expose
    def index(self, state, code=None, error=None):
        """
        Receive a SimpleOAuthClient response containing a verification code. Use the code
        to fetch the access_token.
        """
        error = None
        if code:
            try:
                self.fetch_token(code, state)
            except MissingTokenError:
                error = self._fmt_failure(
                    'Missing access token parameter.</br>Please check that '
                    'you are using the correct client_secret')
            except MismatchingStateError:
                error = self._fmt_failure('CSRF Warning! Mismatching state')
        else:
            error = self._fmt_failure('Unknown error while authenticating')
        # Use a thread to shutdown cherrypy so we can return HTML first
        self._shutdown_cherrypy()
        return error if error else self.success_html.replace('{access_token}', self.token['access_token'])

    def _fmt_failure(self, message):
        tb = traceback.format_tb(sys.exc_info()[2])
        tb_html = '<pre>%s</pre>' % ('\n'.join(tb)) if tb else ''
        return self.failure_html % (message, tb_html)

    def _shutdown_cherrypy(self):
        """ Shutdown cherrypy in one second, if it's running """
        if cherrypy.engine.state == cherrypy.engine.states.STARTED:
            threading.Timer(1, cherrypy.engine.exit).start()

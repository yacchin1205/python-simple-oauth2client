#!/usr/bin/env python
"""SimpleOAuthClient

Usage:
  simple_oauthclient authorize --client_id=<client_id> --client_secret=<client_secret> --authorize_uri=<authorize_uri> \
--fetch_token_uri=<fetch_token_uri> --scope=<scope>... [--redirect_uri=<redirect_uri>] [--config=<config_file>]
  simple_oauthclient --version
  simple_oauthclient --help

Options:
  -h --help                            Show this screen.
  --client_id=<client_id>              App key of your app.
  --client_secret=<client_secret>      App secret of your app.
  --authorize_uri=<authorize_uri>      Authorize URI of your app.
  --fetch_token_uri=<fetch_token_uri>  Fetch token URI of your app.
  --scope=<scope>                      Scopes separated by comma of your app.
  --redirect_uri=<redirect_uri>        Redirect URI of your app [default: http://127.0.0.1:8080/]
  --config=<config_file>               Use the config file specified [default: ./simple_oauthclient.cfg]

"""
from __future__ import absolute_import

from docopt import docopt
from six.moves import configparser

from simple_oauthclient.auth import SimpleOAuthClientAuth


class SimpleOAuthClientCli:
    def __init__(self, arguments):
        """
        Runs the command specified as an argument with the options specified
        """
        self.config_file = arguments['--config']
        self.config = configparser.ConfigParser()
        self.client_id = None
        self.client_secret = None
        self.access_token = None

        if arguments['authorize']:
            self.client_id = arguments['--client_id']
            self.client_secret = arguments['--client_secret']
            self.authorize_uri = arguments['--authorize_uri']
            self.fetch_token_uri = arguments['--fetch_token_uri']
            self.scope = arguments['--scope']
            self.redirect_uri = arguments['--redirect_uri']
            self.authorize()
        elif not arguments['--version'] and not arguments['--help']:
            try:
                # Fail if config file doesn't exist or is missing information
                self.read_config()
            except (IOError, configparser.NoOptionError,
                    configparser.NoSectionError):
                print('Missing config information, please run '
                      '"simple_oauthclient authorize"')

    def read_config(self):
        """ Read credentials from the config file """
        with open(self.config_file) as cfg:
            try:
                self.config.read_file(cfg)
            except AttributeError:  # Not python 3.X fallback
                self.config.readfp(cfg)
        self.client_id = self.config.get('simple_oauthclient', 'client_id')
        self.client_secret = self.config.get('simple_oauthclient', 'client_secret')
        self.access_token = self.config.get('simple_oauthclient', 'access_token')

    def write_config(self, access_token):
        """ Write credentials to the config file """
        self.config.add_section('simple_oauthclient')
        self.config.set('simple_oauthclient', 'client_id', self.client_id)
        self.config.set('simple_oauthclient', 'client_secret', self.client_secret)
        self.config.set('simple_oauthclient', 'access_token', access_token)
        with open(self.config_file, 'w') as cfg:
            self.config.write(cfg)
        print('Credentials written to %s' % self.config_file)
        print('Access token: %s' % access_token)

    def authorize(self):
        """
        Authorize a user using the browser and a CherryPy server, and write
        the resulting credentials to a config file.
        """

        # Thanks to the magic of docopts, I can be guaranteed to have a
        # a client_id and client_secret
        auth = SimpleOAuthClientAuth(
            self.client_id,
            self.client_secret,
            self.authorize_uri,
            self.fetch_token_uri,
            self.scope,
            self.redirect_uri,
        )
        auth.browser_authorize()

        # Write the authentication information to a config file for later use
        if auth.token:
            self.write_config(auth.token['access_token'])
        else:
            print('ERROR: We were unable to authorize to use the SimpleOAuthClient API.')


def main():
    """ Parse the arguments and use them to create a SimpleOAuthClientCli object """
    arguments = docopt(__doc__)
    SimpleOAuthClientCli(arguments)


if __name__ == '__main__':
    """ Makes this file runnable with "python -m simple_oauthclient.cli" """
    main()

#!/usr/bin/env python2

import os
import sys
import argparse
import urllib2
import pickle
import xml.etree.ElementTree as ET
from textwrap import wrap
from redmine import Redmine
from ConfigParser import ConfigParser
from prettyansi.prettyansi import AnsiColors


BASE = '~/.redmine/%s'
_full = lambda p: os.path.expanduser(p)


class ArgParser(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='Command line interface to Redmine using it\'s XML REST API')
        parser.add_argument('-L', '--latest', help='Get the latest issues', action='store_true')
        parser.add_argument('-t', '--type', help='Type of data to lookup - project, issue etc', type=str, choices=['project', 'issue'])
        parser.add_argument('-n', '--num', help='Total number of issues to return')
        parser.add_argument('-D', '--show-descriptions', action='store_true', help='Show descriptions for items as well as subjects')
        parser.add_argument('-s', '--sorting', help='Column for sorting, can be suffixed with :desc to reverse order. Issues only!', type=str)
        parser.add_argument('-o', '--offset', help='Offset for issues starting from most recent descending')
        parser.add_argument('-p', '--project-id', help='Query against this particular project')
        parser.add_argument('-f', '--filter', help='Filter any results against this - saves you grepping')
        parser.add_argument('-R', '--refresh', action='store_true', help='Force reloading, ignoring and updating any previously cached data')
        parser.add_argument('-A', '--alias', help='Add an alias for an id')
        parser.add_argument('-i', '--object', help='Look up a particular item id', type=int)
        parser.add_argument('-m', '--assigned-to-me', help='Filter to show assigned to me only', action='store_true')
        parser.add_argument('--statuses', help='Show a list of issue statuses', action='store_true')
        parser.add_argument('--show-aliases', help='List current aliases in user config', action='store_true')

        self.parser = parser

    def get(self):
        return self.parser.parse_args()


class RedmineData(object):

    def __init__(self, key, url=None, command=None):
        self.url = url
        self.key = key
        self.command = command
        self.data = []

    def link(self, x):
        if self.url:
            return '%s/%s/%s' % (self.url, self.command, x)
        else:
            return '/%ss/%s' % (self.command, x)

    @property
    def path(self):
        return BASE % 'cache/%s.pickle' % self.key

    def cache(self, data):
        # now = datetime.now().strftime('%Y%m%d-%H%M')
        self.data = data
        pickle.dump(data, open(_full(self.path), 'wb'))

    def load(self):
        try:
            self.data = pickle.load(open(_full(self.path)))
            return True
        except IOError:
            self.data = []
            return False

    def show(self, descriptions=False):

        for issue in self.data:

            AnsiColors.activate_color('blue')
            print issue[0].ljust(8),
            AnsiColors.activate_color('red')
            print issue[1][:30].ljust(33),
            AnsiColors.activate_color('yellow')
            print issue[2][:35].encode('utf-8').ljust(38),
            AnsiColors.activate_color('green')
            print self.link(issue[0])

            if descriptions:
                AnsiColors.reset()
                print "\n\n%s\n\n" % issue[3].encode('utf-8')

            if len(issue) == 5:
                # We have journal data
                for cnt, log in enumerate(issue[4]):
                    if cnt % 2 == 0:
                        AnsiColors.activate_color('green')
                    else:
                        AnsiColors.activate_color('red')

                    if log[2] is not None:
                        print "\nComment by %s at %s: \n" % (log[0], log[1])
                        AnsiColors.reset()
                        print '\n'.join(wrap(log[2], 70))
                        AnsiColors.activate_color('yellow')
                        print "_" * 80, "\n"


class RedmineCLI(object):

    def __init__(self, cfg='redmine.cfg'):

        CACHE = _full(BASE % 'cache')

        if not os.path.exists(_full(BASE % '')):
            print "Creating ~/.redmine/"
            os.mkdir(_full(BASE % ''))

        if not os.path.exists(_full(BASE % cfg)):
            print "Setting up redmine.cfg file..."
            self.setup_config(_full(BASE % cfg))

        if not os.path.exists(CACHE):
            print "Creating cache folder..."
            os.mkdir(_full(CACHE))

        self._cfgpath = os.path.expanduser(BASE % cfg)
        cfg = self.get_config()

        self.key, self.url = cfg.get('auth', 'key'), 'http://%s' % cfg.get('auth', 'url')
        self.me = cfg.get('auth', 'uid')

        self.aliases = dict(cfg.items('aliases'))

    def setup_config(self, path):
        cfg = ConfigParser()
        cfg.add_section('auth')
        url = raw_input('Enter URL for your redmine install without http: ')
        cfg.set('auth', 'url', url)
        key = raw_input('Enter your users API key (found in http://%s/my/account/): ' % url)
        cfg.set('auth', 'key', key)
        uid = raw_input('Enter your user id (click on your name and note the number): ')
        cfg.set('auth', 'uid', uid)
        cfg.add_section('aliases')
        with open(path, 'wb') as f:
            cfg.write(f)
        print "Ready to go"

    def get_config(self):
        try:
            f = open(self._cfgpath)
        except IOError:
            sys.exit('FAIL: Please add a config file with API key to %s' % self._cfgpath)

        cfg = ConfigParser()
        cfg.readfp(f)

        return cfg

    def show_aliases(self):
        for alias in self.aliases.items():
            print alias[0].ljust(15), alias[1]

    def add_alias(self, alias, value):
        cfg = self.get_config()
        cfg.set('aliases', alias, value)
        with open(self._cfgpath, 'wb') as _f:
            cfg.write(_f)

    def get_projects(self, **kwargs):
        url = 'projects.xml'
        return self._command(command='projects', command_url=url, element='project', **kwargs)

    def get_issues(self, project=None, **kwargs):
        url = 'issues.xml'
        return self._command(command='issues', project=project, command_url=url, element='issue', **kwargs)

    def get_object(self, object_id, object_type='issue', **kwargs):
        url = '%ss/%d.xml' % (object_type, object_id)
        if object_type == 'issue':
            kwargs.update({'includes': 'journals'})
        return self._command(command='issues', command_url=url, object_id=object_id, element='.', **kwargs)

    def get_statuses(self, **kwargs):
        url = 'issue_statuses.xml'
        return self._command(command='issue_statuses', command_url=url, element='issue_status', **kwargs)

    def _command(self, command='issues', command_url='issues.xml', **kwargs):

        force = kwargs.get('force', False)
        limit = kwargs.get('limit', 100)
        offset = kwargs.get('offset', 0)
        sort = kwargs.get('sort', 'id:desc')
        filter = kwargs.get('filter', None)
        project = kwargs.get('project', None)
        object_id = kwargs.get('object_id', None)
        me_only = kwargs.get('me_only', False)
        element_filter = kwargs.get('element', command)
        includes = kwargs.get('includes', None)

        params = []

        if includes is not None:
            params += (('include', includes),)

        if offset is not None:
            params += (('offset', offset),)

        if sort is not None:
            params += (('sort', sort),)

        if limit is not None:
            params += (('limit', limit),)

        if project:
            params += (('project_id', self.aliases.get(project, project)),)

        if me_only:
            params += (('assigned_to_id', self.me),)

        params_key = '-'.join(['%s%s' % (p[0], p[1]) for p in params])
        params_key += 'filter%s' % filter
        params_key += 'object_id%s' % object_id
        key = 'command%sparams%s' % (command, params_key)

        data = RedmineData(key, url=self.url, command=command)

        if not force:
            if data.load():
                return (True, data)

        rm = Redmine(self.url, key=self.key)

        try:
            # As of Feb 2013 the pyredmine library has finally had a bunch of updates
            # - including cacheing! The response from RedMine.open is now a string rather
            # than a raw ElementTree instance so must convert now.
            issues = ET.fromstring(rm.open(command_url, parms=params)).findall(element_filter)
        except urllib2.HTTPError:
            return (False, 'There was an HTTP error - do you have permission to access?')

        issue_data = list()

        for issue in issues:
            issue_id = issue.find('id').text

            if command == 'projects':
                name = issue.find('identifier').text
            elif command == 'issue_statuses':
                name = issue.find('name').text
            else:
                name = issue.find('project').get('name')

            try:
                description = issue.find('description').text
            except AttributeError:
                description = 'N/A'

            try:
                subject = issue.find('subject').text
            except AttributeError:
                subject = 'N/A'

            history = list()
            if command == 'issues' and object_id:
                journals = issue.find('journals').findall('journal')
                for j in journals:
                    history.append([
                        j.find('user').get('name'),
                        j.find('created_on').text,
                        j.find('notes').text,
                    ])

            if filter is None or (filter in subject.lower() or filter in name.lower()):
                issue_data.append((issue_id, name, subject.replace('\n', ''), description, history))

        data.cache(issue_data)
        return (True, data)

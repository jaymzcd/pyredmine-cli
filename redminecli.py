#!/usr/bin/env python2

import os
import sys
import argparse
import urllib2
import pickle
from redmine import Redmine
from ConfigParser import ConfigParser
from datetime import datetime, timedelta


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
            return '%s/%ss/%s' % (self.url, self.command, x)
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
            if descriptions:
                print "-" * 120
            print issue[0].ljust(8), issue[1][:30].ljust(33), issue[2][:35].encode('utf-8').ljust(38), self.link(issue[0])
            if descriptions:
                print "-" * 120
                print "\n\n%s\n\n" % issue[3].encode('utf-8')


class RedmineCLI(object):

    def __init__(self, cfg='redmine.cfg'):

        CACHE = _full(BASE % 'cache')

        if not os.path.exists(CACHE):
            os.mkdir(_full(CACHE))

        self._cfgpath = os.path.expanduser(BASE % cfg)
        cfg = self.get_config()

        self.key, self.url = cfg.get('auth', 'key'), 'http://%s' % cfg.get('auth', 'url')
        self.me = cfg.get('auth', 'uid')

        self.aliases = dict(cfg.items('aliases'))

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

    def command(self, command='issues', force=False, offset=0, limit=50, sort='id:desc', project=None, filter=None, object_id=None, me_only=False):

        params = []

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

        command_url = '%ss' % command
        if object_id:
            command_url += '/%d.xml' % object_id
            element = '.'
        else:
            command_url += '.xml'
            element = command

        try:
            issues = rm.open(command_url, parms=params).findall(element)
        except urllib2.HTTPError:
            return (False, 'There was an HTTP error - do you have permission to access?')

        issue_data = list()

        for issue in issues:
            issue_id = issue.find('id').text
            if command == 'project':
                project = issue.find('identifier').text
            else:
                project = issue.find('project').get('name')

            try:
                description = issue.find('description').text
            except AttributeError:
                description = 'N/A'

            try:
                subject = issue.find('subject').text
            except AttributeError:
                subject = 'N/A'

            if filter is None or (filter in subject.lower() or filter in project.lower()):
                issue_data.append((issue_id, project, subject.replace('\n', ''), description))

        data.cache(issue_data)
        return (True, data)

if __name__ == '__main__':

    cli = RedmineCLI()
    args = ArgParser().get()

    latest = args.latest

    command = args.type
    refresh = args.refresh
    descriptions = args.show_descriptions
    sorting = args.sorting
    limit = args.num
    offset = args.offset
    me_only = args.assigned_to_me

    if args.alias is not None:
        k, v = args.alias.split('=')
        cli.add_alias(k, v)
        print "Saved alias %s" % args.alias
        sys.exit(0)

    if args.show_aliases:
        cli.show_aliases()
        sys.exit(0)

    if args.object:
        command = 'issue'
        descriptions = True

    if args.project_id:
        command = 'issue'

    if latest:
        command = 'issue'
        refresh = True
        sorting = 'created_on:desc'
        offset = 0
        me_only = True

    response, data = cli.command(command=command, force=refresh, offset=offset, limit=limit, sort=sorting, project=args.project_id, filter=args.filter, object_id=args.object, me_only=me_only)

    if response:
        data.show(descriptions=descriptions)

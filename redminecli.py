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
        parser.add_argument('command', help='Base command to lookup - project, issue etc', type=str, choices=['project', 'issue'])
        parser.add_argument('-n', '--num', help='Total number of issues to return')
        parser.add_argument('-s', '--sorting', help='Column for sorting, can be suffixed with :desc to reverse order. Issues only!', type=str)
        parser.add_argument('-o', '--offset', help='Offset for issues starting from most recent descending')
        parser.add_argument('-p', '--project-id', help='Query against this particular project')
        parser.add_argument('-f', '--filter', help='Filter any results against this - saves you grepping')
        parser.add_argument('-R', '--refresh', action='store_true', help='Force reloading, ignoring and updating any previously cached data')
        parser.add_argument('-A', '--alias', action='store_true', help='Add an alias for an id')

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

    def show(self):
        for issue in self.data:
            print issue[0].ljust(8), issue[1][:30].ljust(33), issue[2][:40].encode('utf-8').ljust(43), self.link(issue[0])


class RedmineCLI(object):

    def __init__(self, cfg='redmine.cfg'):

        CACHE = _full(BASE % 'cache')

        if not os.path.exists(CACHE):
            os.mkdir(_full(CACHE))

        try:
            f = open(os.path.expanduser(BASE % cfg))
        except IOError:
            sys.exit('FAIL: Please add a config file with API key to %s' % cfg)

        cfg = ConfigParser()
        cfg.readfp(f)
        self.key, self.url = cfg.get('auth', 'key'), 'http://%s' % cfg.get('auth', 'url')

        self.aliases = dict(cfg.items('aliases'))

    def command(self, command='issues', force=False, offset=0, limit=50, sort='id:desc', project=None, filter=None):

        params = (('offset', offset), ('limit', limit), ('sort', sort),)
        if project:
            params += (('project_id', self.aliases.get(project, project)),)

        params_key = '-'.join(['%s%s' % (p[0], p[1]) for p in params])
        params_key += 'filter%s' % filter
        key = 'command%sparams%s' % (command, params_key)

        data = RedmineData(key, url=self.url)

        if not force:
            if data.load():
                return (True, data)

        rm = Redmine(self.url, key=self.key)

        try:
            issues = rm.open('%ss.xml' % command, parms=params).findall(command)
        except urllib2.HTTPError:
            return (False, 'There was an HTTP error - do you have permission to access?')

        issue_data = list()

        for issue in issues:
            issue_id = issue.find('id').text
            if command == 'project':
                subject = issue.find('description').text
                project = issue.find('identifier').text
            else:
                subject = issue.find('subject').text
                project = issue.find('project').get('name')

            if subject == None:
                subject = 'N/A'

            if filter is None or (filter in subject.lower() or filter in project.lower()):
                issue_data.append((issue_id, project, subject.replace('\n', '')))

        data.cache(issue_data)
        return (True, data)

if __name__ == '__main__':

    cli = RedmineCLI()
    args = ArgParser().get()
    response, data = cli.command(command=args.command, force=args.refresh, offset=args.offset, limit=args.num, sort=args.sorting, project=args.project_id, filter=args.filter)

    if response:
        data.show()

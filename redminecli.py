#!/usr/bin/env python2

import os
import sys
import argparse
import urllib2
from redmine import Redmine
from ConfigParser import ConfigParser


def init(cfg='~/.redmine.cfg'):
    try:
        f = open(os.path.expanduser(cfg))
    except IOError:
        sys.exit('FAIL: Please add a config file with API key to ~/.redmine.cfg')

    cfg = ConfigParser()
    cfg.readfp(f)
    key, url = cfg.get('auth', 'key'), 'http://%s' % cfg.get('auth', 'url')
    return key, url


def rmcommand(rm, offset=0, limit=50, sort='id:desc', project=None, command='issues'):

    params = (('offset', offset), ('limit', limit), ('sort', sort),)
    if project:
        params += (('project_id', project),)

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

        issue_data.append((issue_id, project, subject.replace('\n', '')))

    return (True, issue_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command line interface to Redmine using it\'s XML REST API')

    parser.add_argument('command', help='Base command to lookup - project, issue etc', type=str, choices=['project', 'issue'])
    parser.add_argument('-n', '--num', help='Total number of issues to return')
    parser.add_argument('-s', '--sorting', help='Column for sorting, can be suffixed with :desc to reverse order. Issues only!', type=str)
    parser.add_argument('-o', '--offset', help='Offset for issues starting from most recent descending')
    parser.add_argument('-p', '--project-id', help='Query against this particular project')

    args = parser.parse_args()
    key, url = init()
    rm = Redmine(url, key=key)

    response, data = rmcommand(rm, command=args.command, offset=args.offset, limit=args.num, sort=args.sorting, project=args.project_id)
    _link = lambda x: '%s/%ss/%s' % (url, args.command, x)

    if response:
        for issue in data:
            print issue[0].ljust(8), issue[1][:30].ljust(33), issue[2][:40].encode('utf-8').ljust(43), _link(issue[0])
    else:
        print data

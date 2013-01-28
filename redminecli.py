#!/usr/bin/env python2

import os
import sys
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


def issue_list(rm):
    issues = rm.open('issues.xml').findall('issue')
    issue_data = list()

    for issue in issues:
        issue_id = issue.find('id').text
        subject = issue.find('subject').text
        project = issue.find('project').get('name')
        issue_data.append((issue_id, project, subject))

    return issue_data

if __name__ == '__main__':
    key, url = init()
    rm = Redmine(url, key=key)
    issues = issue_list(rm)

    _link = lambda x: '%s/issues/%s' % (url, x)

    for issue in issues:
        print issue[0].ljust(8), issue[1][:30].ljust(33), issue[2][:40].ljust(43), _link(issue[0])

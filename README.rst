==================
Redmine Python CLI
==================

.. image:: http://i.imgur.com/8KO0oHF.png

Actually there's a much more `featureful ruby version <https://github.com/diasjorge/redmine-cli>`_,
but I just wanted something quick and easy in Python using an existing library, in this
case pyredminews - to get back an issue list - I often forget what the most recent
issue ID was that I wanted to log tickets against.

Setup
=====

On first launch the script will create a

Add a file to ``~/.redmine.cfg`` with your API key and URL thus::

    [auth]
        url=redmine.yoursite.com
        key=C400D10350540028BF74EAFD62280560
        uid=<USER ID>

Note the key above is just a random MD5 hash - it is *not* my private redmine
key! :) Then run the script. You should get back the first 100 issues listed
on your redmine ``/issues/`` page along with the project name, subject &
a URL to click if you're using a fancy terminal.

Not exactly groundbreaking but saves me swapping over to chrome to go hunting
for id's.

Usage
=====

Command line interface to Redmine using it's XML REST API::

    usage: redmine [-h] [-L] [-t {project,issue}] [-n NUM] [-D] [-s SORTING]
                   [-o OFFSET] [-p PROJECT_ID] [-f FILTER] [-R] [-A ALIAS]
                   [-i OBJECT] [-m] [--show-aliases]

    Command line interface to Redmine using it's XML REST API

    optional arguments:
      -h, --help            show this help message and exit
      -L, --latest          Get the latest issues
      -t {project,issue}, --type {project,issue}
                            Type of data to lookup - project, issue etc
      -n NUM, --num NUM     Total number of issues to return
      -D, --show-descriptions
                            Show descriptions for items as well as subjects
      -s SORTING, --sorting SORTING
                            Column for sorting, can be suffixed with :desc to
                            reverse order. Issues only!
      -o OFFSET, --offset OFFSET
                            Offset for issues starting from most recent descending
      -p PROJECT_ID, --project-id PROJECT_ID
                            Query against this particular project
      -f FILTER, --filter FILTER
                            Filter any results against this - saves you grepping
      -R, --refresh         Force reloading, ignoring and updating any previously
                            cached data
      -A ALIAS, --alias ALIAS
                            Add an alias for an id
      -i OBJECT, --object OBJECT
                            Look up a particular item id
      -m, --assigned-to-me  Filter to show assigned to me only
      --show-aliases        List current aliases in user config

.. image:: http://i.imgur.com/tQnzagt.png

To get a list of the first n projects - note in a somewhat hacky manner use a high
enough number to return all results - this will probably do unless you have some
serious overusage of Redmine::

    redmine -n1000 -tproject

This returns the project id, identifier, description and a URL. Using either the
id *or* identifier for PROJECT_ID you can query open issues for that project. You
can also use predefined aliases added with ``-A``::

    redmine -p <PID> issue

To get the 50 most recent issues for the project aliased *mymvp*::

    redmine -n50 -s updated_on:desc -p mymvp

Get issues with 'ssl' in the subject for project id 122::

    redmine -n100 -p122 -fssl

When specifiying a project with ``-p`` the command automatically defaults to
loading issues. You can get only issues assigned directly to you (i.e. excluding
any group assignments) with ``-m``.

For more detail on a particular item use ``-D`` along with the id::

    redmine -i 20019 -D

Cacheing
--------

For any request a key is created out of the parameters. This is then saved to the
``~/.redmine/cache/`` directory to reuse when called again. For the most part the
actual subjects, titles etc won't change but you can force a refresh with the ``-R``
flag. This will cause the pickled data to be renewed.

Note that changing the sort or number of results will cause a fresh hit to the
redmine instance.

Used libraries
--------------

This makes use of the following key libraries, some standard some external:

* `pyredminews <http://github.com/ianepperson/pyredminews>`_ - using a fork here on GH
* `argparse <http://docs.python.org/2.7/library/argparse.html>`_ standard lib in 2.7
* `ConfigParser <http://docs.python.org/2/library/configparser.html>`_ standard lib in 2
* `prettyansi <https://github.com/jaymzcd/pyprettyansi>`_ for terminal coloring

Moar code
---------

You can find some more on me at `jaymz.eu <http://jaymz.eu>`_. Follow
`@jaymzcampbell <http://twitter.com/jaymzcampbell>`_ for acerbic tweets. I
work at `u-dox <http://u-dox.com>`_ and we're `on github <http://github.com/udox>`_ too!


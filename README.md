# Redmine Python CLI

![logo](http://i.imgur.com/8KO0oHF.png)

Actually there's a much more [featureful ruby version](https://github.com/diasjorge/redmine-cli),
but I just wanted something quick and easy in Python using an existing library, in this
case pyredminews - to get back an issue list - I often forget what the most recent
issue ID was that I wanted to log tickets against.

## Setup

Add a file to `~/.redmine.cfg` with your API key and URL thus:

    [auth]
        url=redmine.yoursite.com
        key=C400D10350540028BF74EAFD62280560

Note the key above is just a random MD5 hash - it is _not_ my private redmine
key! :) Then run the script. You should get back the 25 issues listed
on your redmine `/issues/` page along with the project name, subject &
a URL to click if you're using a fancy terminal.

Not exactly groundbreaking but saves me swapping over to chrome to go hunting
for id's.

## Usage
Command line interface to Redmine using it's XML REST API

    usage: redmine [-h] [-n NUM] [-s SORTING] [-o OFFSET] [-p PROJECT_ID]
                   [-f FILTER]
                   {project,issue}

    Command line interface to Redmine using it's XML REST API

    positional arguments:
      {project,issue}       Base command to lookup - project, issue etc

    optional arguments:
      -h, --help            show this help message and exit
      -n NUM, --num NUM     Total number of issues to return
      -s SORTING, --sorting SORTING
                            Column for sorting, can be suffixed with :desc to
                            reverse order. Issues only!
      -o OFFSET, --offset OFFSET
                            Offset for issues starting from most recent descending
      -p PROJECT_ID, --project-id PROJECT_ID
                            Query against this particular project
      -f FILTER, --filter FILTER
                            Filter any results against this - saves you grepping

![usage](http://i.imgur.com/NGb3Uh9.png)

To get a list of the first n projects - note in a somewhat hacky manner use a high
enough number to return all results - this will probably do unless you have some
serious overusage of Redmine:

    redmine -n1000 project

This returns the project id, identifier, description and a URL. Using either the
id _or_ identifier for PROJECT_ID you can query open issues for that project:

    redmine -p <PID> issue

To get the 50 most recent issues for the project _mymvp_:

    redmine -n50 -s updated:desc -p mymvp issue

Get issues with 'ssl' in the subject for project id 122:

    redmine -n100 -p122 -fssl issue

## Used libraries

This makes use of the following key libraries, some standard some external:

* [pyredminews](github.com/ianepperson/pyredminews) - using a fork here on GH
* [argparse](http://docs.python.org/2.7/library/argparse.html) standard lib in 2.7
* [ConfigParser](http://docs.python.org/2/library/configparser.html) standard lib in 2

## Moar code

You can find some more on me at [jaymz.eu](http://jaymz.eu). Follow [@jaymzcampbell](http://twitter.com/jaymzcampbell)
for acerbic tweets. I work at [u-dox](http://u-dox.com) and we're [on github](http://github.com/udox) too!

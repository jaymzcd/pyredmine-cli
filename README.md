# Redmine Python CLI

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

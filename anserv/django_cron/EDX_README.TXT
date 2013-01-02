There are multiple projects with this name in both Google Code and on
github. pip installs a different one from what I would like to use,
and it is small, so I am including it in this code repository.

Honestly, they're mostly pretty bad, but it beats writing our own
version.

  http://code.google.com/p/django-cron/

Used in the code, mostly because it is the first one I ran across, but
it also seems to be the best for what we're doing. The cron runs as a
thread in Django, which is a bad long-term way to go, but in the short
term, it makes development/deployment very easy.

The version in pip is probably this version: 
  https://github.com/Tivix/django-cron
The code is better, but it has serious architectural issues for our
uses. All cron jobs to be explicitly listed in settings.py, which
makes closures, decorators, and modules hard. 

In addition, it requires an explicit Unix crontab to call management
commands. This is architecturally better, but complicates
development/deployment, and it didn't make sense at this stage. 

This code is sane, clean, and simple, although a little
lightweight/underfeatured: 
https://github.com/jsocol/django-cronjobs

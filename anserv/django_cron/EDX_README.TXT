Summary: This code should be burned and rewritten from scratch. It was
helpful for defining the API, but it is poorly written and unrobust. 





Details: 

There are multiple projects with this name in both Google Code and on
github. pip installs a different one from what I would like to use,
and it is small, so I am including it in this code repository.

Honestly, they're mostly pretty bad, but I thought it would beat
writing our own version. I started with:

  http://code.google.com/p/django-cron/

I used in the code, mostly because it is the first one I ran across,
but it also seems to be the best for what we're doing. The cron runs
as a thread in Django, which is a bad long-term way to go, but in the
short term, it makes development/deployment very easy.

Sadly, the code was broken in a number of ways, and to debug it, I
ended up rewriting it mostly from scratch. It now works, but the code
is junk. Mutating bad code until it works doesn't lead to good
code. Key problem right now is that if the application dies with a
Cron or Job in an executing state, on restart, it won't run again. To
make it reliable, you need to run:
  Cron.objects.all().delete()
  Job.objects.all().delete()
In addition, the debuggability of cron tasks, as well as error
handling is zero. I'm going to leave this be for a bit, so I can 
continue to make progress in other places. 

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

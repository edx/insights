analytics-experiments
=====================

This is a development version of an analytics framework for the edX
infrastructure. The goal of this framework is to define an
architecture for simple, pluggable analytics modules. The architecture
must have the following properties:

1. Easy to use. Professors, graduate students, etc. should be able to
write plug-ins quickly and easily. These should be able to run in the
system without impacting the overall stability. Results should be
automatically shown to customers. 
2. The API must support robust, scalable implementations. The current
back-end is not designed for mass scaling, but the modules should be. 
3. Reusable. The individual analytics modules should be able to use
the results from other modules, and people should be able to build on
each others' work.

Architecture
------------

The analytics framework has access to the event stream from the
tracking architecture, a read-replica of the main database, as well
as, in the future, course definition database, and read-replicas of
auxilliary databases, such as discussion forums. 

Each module in the analytics framework has its own Mongo database. In
addition, in the near future, it should have read-only access to the
DBs associated with other modules.

The module consists of a set of functions which can be decorated as: 
* Event handlers. These receive tracking events. 
* Views. These render HTML to be shown to the user
* Future: AJAX calls associated with events. 
* Queries: These render machine-readable results through an SOA. 
* Future: CRON tasks

To understand the system, the best place to start is by reading a
sample module. Next place is to look at the code for the
decorators. Final place is for the main views and dashboard. 

Installing
----------

    apt-get install python-pip python-matplotlib python-scipy emacs mongodb apache2-utils python-mysqldb subversion ipython nginx git 
    pip install django pymongo pymysql flup fs mysql-client mako
    
    git clone git@github.com:MITx/analytics-experiments.git
    cd analytics-experiments
    git checkout pmitros/api-devel
    cd anserv
    python manage.py syncdb
    python manage.py syncdb --database=local
    [If you want real data, create an override_settings.py, pointing to your 
    SQL database, and disable DUMMY_MODE]
    python manage.py runserver localhost:9902

For a half-broken dashboard, go to: 

    http://127.0.0.1:9022/static/dashboard.html

To see a listing of modules, go to: 

    http://127.0.0.1:9022/probe

Then 

    http://127.0.0.1:9022/probe/view

Etc. 

Writing a New Module
--------------------
Modules should be placed in the modules/[module_name]

Each module can have decorators: 

    @cron(time_in_seconds)

Runs periodically. 

To declare a new view (human-readable HTML), decorate with: 

    @view(name="User_Activity", 
        category="global", 
        args=['db','fs'], 
        description="Plot of per-day user activity")

If any parameters to the decorator are omitted, the system will make a
best guess. Parameters to the function are passed a keyword args, as
specified by the args parameter.

@query will have the same syntax as @view, although at the moment, the
code is lagging.

@memoize(t) tells the system not to rerun a query for 't'
seconds. Right now, it breaks some of the logic for guessing category,
etc. It needs to be modified to use decorator.decorator so it doesn't
drop function metainformation.

See examples for syntax. 

Shortcuts/invariants
--------------------

* At present, events come into the system through an SOA. The tracking
framework is modified to use a Python HTTP logger, which are received
by the framework. For most events, this should be replaced with
something asynchronous, as well as queued.
* The analytics have no isolation from each other. The architecture
supports running each module in its own sandbox. This should not be
broken (e.g. by having direct calls across modules).
* Right now, all functions must be re-entrant. Some folks would like to
write an analytic that runs in a single process without worrying about
thread safety (e.g. while(true) { get_event(); handle_event(); }). The
API is designed to support this, but this is not implemented.
* The analytics framework has no way to generate new events. This would be 
useful for chaining analytics.
* There are no filters. E.g. an event handler cannot ask for all video events. 
* We are copying code from the main mitx repo (models.py, mitmako). We
  should figure out a better way to handle this.

Target markets
--------------

The analytics has several target markets: 

1. Internal system use. As we build out infrastructure for intelligent
tutoring, partnering students into small groups, etc., we need to do
analysis on student interactions with the system.
2. Marketing. Numbers to figure out student lifecycle. 
3. Instructors. Numbers to figure out who students are, and how to
improve the courses. 
4. Product. 
5. Students. 
6. Board of directors, reporters, etc. 

Modes of operation
------------------

1. Hard realtime. When an event comes in, it is synchronously
processed. The caller knows that by the time the event returns, it can
extract results from the analytic.
2. Soft realtime. There is a queue, but processing is fast enough that
the queue is assumed to be nearly empty.
3. Queued. There is a queue with potentially a significant backlog. 
4. Batched. Processing runs at e.g. 5 minute or 1 day intervals. 

Analytics can be per-student, per-resource, or global. They may also
be per-course or per-university, but this is architecturally brittle,
and not recommended (although likely unavoidable).

For developing the system, hard realtime is the most critical, and
we'd like to keep the invariant that it works. Next most useful is
either queued or batched. 

Sharding
--------

Some types of analytics support sharding per-resource (e.g. number of
views) or per-student (e.g. time spent in course). Some require global
optimization and cannot be sharede (e.g. IRT). This is something we'll
need to eventually think about, but this is a 2.0 feature. Note that
the current decorator design pattern does not help -- it merely helps
define a storage API. A statistic like class rank may be per-user, but
require data from all users. 

Useful pointers
---------------

Pivotal Tracker has a set of possible metrics of mixed quality. The
wiki has another set of possible metrics. The most useful metrics
we've found were in competing systems and in publications from the
research community.

Next steps for API evolution
----------

1. Add support for asynchronous views. When the client issues a
request for a view which takes a while to calculate, there should be
visual feedback.
2. Rewrite the cron code from scratch .
3. Add gridfs/pythonfs support for e.g. generating plots with
matplotlib, animations, etc.
4. Move views into an iframe. 
5. Be more clever about inspection. Recognize names of arguments (fs,
database, etc.), and pass in whatever is required.
6. Create appropriate userspace. We need higher-level functions to
extract information from events.

Other useful next steps
-----------------------

1. Test infrastructure. We should have a dummy dataset and database,
and be able to confirm output of all queries.
2. Development data. We need sample outputs for all queries for when
the DB is not available for UI development (some of this exists). 

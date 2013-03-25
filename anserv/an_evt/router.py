import logging
log=logging.getLogger(__name__)

class DatabaseRouter(object):
    ''' Route reads from MITx models to main DB. Route all other
    accesses to local DB. 
    '''
    def db_for_read(self, model, **hints):
        if model._meta.app_label in ['student','courseware','sites', 'contenttypes', 'courseware_old', 'student_old']:
            return 'default'
        elif model._meta.app_label in ['an_evt','modules', 'cronjobs', 'celery', 'sessions', 'auth', 'django_cache']:
            return 'local'
        else: 
            log.error("ERROR. We need to explicitly route: {0}".format(model._meta.app_label))
            return 'error'
    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)
    #     print "-"
    #     if model._meta.app_label in ['contenttypes']: ## HACK. 
    #         return 'default'
    #     return 'local'
    # def allow_relation(self, obj1, obj2, **hints):
    #     print "?"
    #     return None
    # def allow_syncdb(self, db, model):
    #     print ">"
    #     print db, model._meta.app_label
    #     if db == 'default' or self.db_for_read(model, None) == 'default':
    #         return False
    #     if db == 'local':
    #         return True
    #     raise ValueError("Unknown database")


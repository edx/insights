import django
from django.db import models
import datetime

## Create your models here.
#class StudentBookAccesses(models.Model):
#    username = models.CharField(max_length=500, unique=True) # TODO: Should not have max_length
#    count = models.IntegerField()

class FSExpirations(models.Model):
    ''' The modules have access to a pyfilesystem object where they
    can store big data, images, etc. In most cases, we would like
    those objects to expire (e.g. if a view generates a .PNG analytic
    to show to a user). This model keeps track of files stored, as
    well as the expirations of those models. 
    '''

    def __init__(self, module, filename, expires, seconds, days=0):
        models.Model.__init__(self)
        self.module = module
        self.filename = filename
        self.expires = expires
        self.expiration = datetime.datetime.now() + datetime.timedelta(days, seconds)

    module = models.CharField(max_length=500) # Defines the namespace
    filename = models.CharField(max_length=500) # Filename within the namespace
    expires = models.BooleanField() # Does it expire? 
    expiration = models.DateTimeField(db_index = True) 

    def expired(self):
        ''' Returns a list of expired objects '''
        return self.objects.filter(expires=True, expiration__lte = datetime.datetime.now())

    class Meta:
        unique_together = (("module","filename"))
        ## FIXME: We'd like to create an index first on expiration than on expires (so we can 
        ## search for objects where expires=True and expiration is before now). Django 1.5 
        ## supports this, but 1.4 does not. 
        ## 
        ## I'm putting this in in preparation for 1.5. This is
        ## slightly redundant, since documentation is unclear about
        ## order of the joint index.
        ##
        ## When 1.5 comes out, we can drop the index on expiration. 
        if django.get_version()>='1.5':
            index_together = [
                ["expires","expiration"], 
                ["expiration","expires"]
                ]

    def __str__(self):
        if self.expires: 
            return self.module+'/'+self.filename+" Expires "+str(self.expiration)
        else:
            return self.module+'/'+self.filename+" Permanent ("+str(self.expiration)+")"

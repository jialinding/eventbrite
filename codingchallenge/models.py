from django.db import models


# Create your models here.
class Category(models.Model):
    resource_uri = models.URLField()
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    name_localized = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200)
    short_name_localized = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name
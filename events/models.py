from django.db import models
from django.conf import settings

class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    location = models.CharField(max_length=300)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date', '-start_time']

    @property
    def date(self):
        return self.start_date

    @property
    def time(self):
        return self.start_time

    def __str__(self):
        return self.title
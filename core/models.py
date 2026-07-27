from django.db import models
class HeroImage(models.Model):
    image = models.ImageField(upload_to='hero/')
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
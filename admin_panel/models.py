from django.db import models

from django.utils import timezone



# Create your models here.

class Banner(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='banners/')
    description1 = models.TextField(blank=True, null=True)
    description2 = models.TextField(blank=True, null=True)
    description3 = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active =models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    def update_status(self):
        today = timezone.now().date()
        return self.start_date <= today <=self.end_date
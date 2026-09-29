from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
import os


# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



class Listing(models.Model):
    CATEGORY_CHOICES = [
        ('mobiles', 'Mobiles'),
        ('computers', 'computers'),
        ('electronics', 'Electronics'),
        ('vehicles', 'Vehicles'),
        ('property', 'Property'),
        ('fashion', 'Fashion'),
        ('furniture', 'Furniture'),
        ('musical_instruments', 'musical instruments'),
        ('sports', 'sports'),
        ('books', 'Books'),
        ('toys', 'toys'),
        ('pets', 'pets'),
        ('jobs', 'Jobs'),
        ('services', 'Services'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models. PositiveIntegerField()
    image = models.ImageField(upload_to='listings/', blank=False, null=False)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def delete(self, *args, **kwargs):
        # Delete the image file from media/listings when a listing is deleted
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)

        # Delete the database record
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + relativedelta(months=1)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta

class Payment(models.Model):
    PAYMENT_CHOICES = (
        ('boost', 'Boost'),
        ('feature', 'Feature'),
    )

    agent = models.ForeignKey('Agent', on_delete=models.CASCADE)
    apartment = models.ForeignKey('Apartment', on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    reference = models.CharField(max_length=100, unique=True) 
    is_successful = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def mark_as_paid(self):
        self.is_successful = True
        self.paid_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.agent.user.username} - {self.payment_type}"

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='Profiles')
    phone_number = models.CharField(max_length=15) 
    whatsapp_number = models.CharField(max_length=15) 
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class University(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name

class Period(models.Model):
    period = models.CharField(max_length=50)

    def __str__(self):
        return self.period
    
class ApartmentType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Amenity(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Distance(models.Model):
    distance = models.CharField(max_length=50)

    def __str__(self):
        return self.distance
    
class State(models.Model):
    state = models.CharField(max_length=50)

    def __str__(self):
        return self.state
    
class Apartment(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='apartments')
    title = models.CharField(max_length=400)
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='apartments')
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    distance = models.ForeignKey(Distance, on_delete=models.CASCADE)
    address = models.CharField(max_length=2000)
    apartment_type = models.ManyToManyField(ApartmentType)
    amenities = models.ManyToManyField(Amenity, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)

    slug = models.SlugField(unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    boost_until = models.DateTimeField(null=True, blank=True) 

    def is_boosted(self):
        """Return True if apartment is currently boosted"""
        if self.boost_until:
            return timezone.now() <= self.boost_until
        return False

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Apartment.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
        
class ApartmentImage(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='Apartments', default='Apartments/home.jpg')
    

    def __str__(self):
        return self.image.name 

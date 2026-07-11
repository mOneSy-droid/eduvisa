from django.db import models
from django.utils.text import slugify

class Partner(models.Model):
    CATEGORY_CHOICES = [
        ('accreditation', 'Akkreditatsiya'),
        ('university', 'Hamkor universitet'),
    ]
    name = models.CharField(max_length=255)
    logo_url = models.URLField(max_length=500)
    website_url = models.URLField(max_length=500, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='accreditation')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

class NewsItem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    excerpt = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-published_at']

class Banner(models.Model):
    text = models.TextField()
    highlight = models.CharField(max_length=255, null=True, blank=True)
    link_url = models.CharField(max_length=255, null=True, blank=True, default='#universities')
    link_label = models.CharField(max_length=255, null=True, blank=True, default="So'rov yuborish")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
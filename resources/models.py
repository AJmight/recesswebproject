from django.db import models
from django.conf import settings

class Resource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='resources/files/', blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True, help_text="Alternatively, provide a link to an external resource (e.g., YouTube video, article).")
    resource_type = models.CharField(
        max_length=50,
        choices=[
            ('ARTICLE', 'Article'),
            ('VIDEO', 'Video'),
            ('PDF', 'PDF Document'),
            ('AUDIO', 'Audio File'),
            ('OTHER', 'Other')
        ],
        default='ARTICLE'
    )
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name_plural = "Resources"

    def __str__(self):
        return self.title

    def get_file_url(self):
        if self.file:
            return self.file.url
        return None
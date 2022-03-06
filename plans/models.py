from django.db import models


class Plan(models.Model):
    """Model for site-wide settings."""
    name = models.CharField(max_length=200, help_text="Name of site-wide variable", default="Basic")
    value = models.JSONField(
        null=True, blank=True, help_text="Value of site-wide variable that scripts can reference - must be valid JSON",
        default=dict(thumbnail_200=True, thumbnail_400=False, original_image=False, temporary_link=False)
    )

    def __unicode__(self):
        return self.name

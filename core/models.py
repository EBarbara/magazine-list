from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Woman(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Woman")
        verbose_name_plural = _("Women")

    def __str__(self):
        return self.name

class Section(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")

    def __str__(self):
        return self.name

class Issue(models.Model):
    publishing_date = models.DateField(verbose_name=_("Publishing Date"))
    edition = models.IntegerField(null=True, blank=True, verbose_name=_("Edition"))

    class Meta:
        verbose_name = _("Issue")
        verbose_name_plural = _("Issues")
        unique_together = ('publishing_date', 'edition')

    def __str__(self):
        edition_str = f" Ed. {self.edition}" if self.edition else ""
        return f"{self.publishing_date.strftime('%b/%y')}{edition_str}"

class IssueCover(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='covers', verbose_name=_("Issue"))
    image = models.ImageField(upload_to='covers/', verbose_name=_("Image"))

    class Meta:
        verbose_name = _("Issue Cover")
        verbose_name_plural = _("Issue Covers")

    def __str__(self):
        return f"Cover for {self.issue}"

class Appearance(models.Model):
    woman = models.ForeignKey(Woman, on_delete=models.CASCADE, verbose_name=_("Woman"))
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name=_("Section"))
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, verbose_name=_("Issue"))

    class Meta:
        verbose_name = _("Appearance")
        verbose_name_plural = _("Appearances")
        ordering = ['issue__publishing_date']

    def __str__(self):
        return f"{self.woman} in {self.issue} ({self.section})"

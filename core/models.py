from django.db import models

# Create your models here.

class Woman(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Women"

    def __str__(self):
        return self.name

class Section(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Issue(models.Model):
    publishing_date = models.DateField()
    edition = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('publishing_date', 'edition')

    def __str__(self):
        edition_str = f" Ed. {self.edition}" if self.edition else ""
        return f"{self.publishing_date.strftime('%b/%y')}{edition_str}"

class Appearance(models.Model):
    woman = models.ForeignKey(Woman, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    class Meta:
        ordering = ['issue__publishing_date']

    def __str__(self):
        return f"{self.woman} in {self.issue} ({self.section})"

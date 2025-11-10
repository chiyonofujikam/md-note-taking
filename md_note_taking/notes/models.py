from django.db import models

class NoteModel(models.Model):
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=200, blank=True)
    document = models.FileField(upload_to='documents/', blank=True, null=True)
    markdown_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    report_issues = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Note: {self.filename or 'untitled'}, created at: {self.created_at}, reported issues: {self.report_issues}"
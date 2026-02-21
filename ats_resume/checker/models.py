from django.db import models

class ScannedResume(models.Model):
    filename = models.CharField(max_length=255)
    # Change 'upload_upload' to 'upload_to'
    resume_file = models.FileField(upload_to='resumes/') 
    score = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} - {self.score}%"
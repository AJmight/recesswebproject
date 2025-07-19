# assessments/models.py

from django.db import models
from django.conf import settings # Import settings to reference AUTH_USER_MODEL

class Assessment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    score = models.IntegerField()  # e.g., 0 to 4

    def __str__(self):
        return f"{self.text} ({self.score})"

class UserAssessment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True) # Stores AI feedback as JSON string

    def __str__(self):
        return f"{self.user.username} - {self.assessment.name} ({self.score})"

class Answer(models.Model):
    user_assessment = models.ForeignKey(UserAssessment, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"UA: {self.user_assessment.id}, Q: {self.question.id}, C: {self.choice.id}"

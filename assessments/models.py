# assessments/models.py

from django.db import models
from django.conf import settings # Import settings to get AUTH_USER_MODEL

# Get the custom User model dynamically
User = settings.AUTH_USER_MODEL # Use settings.AUTH_USER_MODEL to reference your custom User model

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
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Use the correct User model
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True) # AI-generated feedback will go here

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "User Assessment"
        verbose_name_plural = "User Assessments"

    def __str__(self):
        return f"{self.user.username} - {self.assessment.name} ({self.score})"

class Answer(models.Model):
    user_assessment = models.ForeignKey(UserAssessment, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user_assessment', 'question') # A user can only answer a question once per assessment
        verbose_name = "Answer"
        verbose_name_plural = "Answers"

    def __str__(self):
        return f"{self.user_assessment.user.username}'s answer to {self.question.text[:30]}..."

# assessments/admin.py

from django.contrib import admin
from .models import Assessment, Question, Choice, UserAssessment, Answer

# Register your models here.
admin.site.register(Assessment)

# For Question, you might want to manage Choices inline
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1 # Number of empty forms to display

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'assessment')
    list_filter = ('assessment',)
    search_fields = ('text',)
    inlines = [ChoiceInline] # Allows managing choices directly from the Question admin page

# For UserAssessment, make score and answers read-only
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0 # Don't show empty forms
    readonly_fields = ('question', 'choice',) # Make question and choice read-only
    can_delete = False # Prevent deleting individual answers
    show_change_link = True # Allow clicking to view full answer details if needed

@admin.register(UserAssessment)
class UserAssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'assessment', 'score', 'submitted_at', 'has_feedback')
    list_filter = ('assessment', 'submitted_at')
    search_fields = ('user__username', 'assessment__name')
    readonly_fields = ('user', 'assessment', 'score', 'submitted_at') # Make these read-only
    fields = ('user', 'assessment', 'score', 'submitted_at', 'feedback') # Define order and include feedback
    inlines = [AnswerInline] # Show answers inline

    def has_feedback(self, obj):
        return bool(obj.feedback)
    has_feedback.boolean = True
    has_feedback.short_description = "Has AI Feedback"


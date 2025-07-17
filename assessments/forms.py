# assessments/forms.py

from django import forms
from .models import Assessment, Question, Choice

class AssessmentForm(forms.Form):
    """
    Form for users to take an assessment. Dynamically generated based on Assessment questions.
    """
    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('assessment')
        super().__init__(*args, **kwargs)
        for question in assessment.question_set.all():
            # Ensure choices are ordered by score or ID for consistency
            choices = [(choice.id, choice.text) for choice in question.choice_set.all().order_by('score')]
            self.fields[f"question_{question.id}"] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True
            )
            # Add Bootstrap class to the radio buttons for better styling
            self.fields[f"question_{question.id}"].widget.attrs.update({'class': 'form-check-input'})
            # You might want to add a custom CSS class to the label or div for more styling control
            # e.g., self.fields[f"question_{question.id}"].widget.attrs.update({'class': 'form-check-input assessment-question-radio'})

class AssessmentAdminForm(forms.ModelForm):
    """
    Form for admins to create/edit Assessment objects.
    """
    class Meta:
        model = Assessment
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class QuestionForm(forms.ModelForm):
    """
    Form for admins to create/edit Question objects.
    """
    class Meta:
        model = Question
        fields = ['text'] # Assessment is set in the view
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class ChoiceForm(forms.ModelForm):
    """
    Form for admins to create/edit Choice objects.
    """
    class Meta:
        model = Choice
        fields = ['text', 'score'] # Question is set in the view
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control'}),
        }

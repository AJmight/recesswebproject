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
            choices = [(choice.id, choice.text) for choice in question.choice_set.all().order_by('score')]
            self.fields[f"question_{question.id}"] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True
            )
            self.fields[f"question_{question.id}"].choices = choices
            self.fields[f"question_{question.id}"].widget.attrs.update({'class': 'form-check-input'})

class AssessmentAdminForm(forms.ModelForm):
    """
    Form for admins to create/edit Assessment objects.
    """
    class Meta:
        model = Assessment
        # REMOVED 'is_mandatory_first_assessment' from fields
        fields = ['name', 'description'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Depression Screening (PHQ-9)'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'A brief description of this assessment.'}),
            # If 'instructions' is in your model, uncomment/add this:
            # 'instructions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Instructions for the user before taking the assessment.'}),
        }

class QuestionForm(forms.ModelForm):
    """
    Form for admins to create/edit Question objects.
    """
    class Meta:
        model = Question
        fields = ['text'] 
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'e.g., Little interest or pleasure in doing things?'}),
        }

class ChoiceForm(forms.ModelForm):
    """
    Form for admins to create/edit Choice objects.
    """
    class Meta:
        model = Choice
        fields = ['text', 'score'] 
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Not at all'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 0'}),
        }

class AssessmentUploadForm(forms.Form):
    """
    Form to upload a JSON file containing assessment data.
    """
    json_file = forms.FileField(
        label="Upload Assessment JSON File",
        help_text="Upload a JSON file structured with assessment name, description, and questions/choices.",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

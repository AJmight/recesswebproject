# assessments/views.py

import json
# Correct import for messages
from django.contrib import messages 
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test # user_passes_test for admin/therapist views
from django.contrib.auth import get_user_model

from assessments.forms import AssessmentAdminForm, AssessmentForm, QuestionForm # Correct way to get the custom User model

from .models import Assessment, Choice, Question, UserAssessment, Answer # Removed 'User' from here

# Get the custom User model dynamically
User = get_user_model()

# Helper for admin checks (re-using from users app logic)
def is_admin(user):
    return user.is_authenticated and user.is_admin

# Helper for therapist or admin checks
def is_therapist_or_admin(user):
    return user.is_authenticated and (user.is_therapist or user.is_admin)

# --- Client Views ---

@login_required(login_url=reverse_lazy('users:login'))
def assessment_list(request):
    """
    Lists all available assessments for users to take.
    """
    assessments = Assessment.objects.all().order_by('name')
    return render(request, 'assessments/assessment_list.html', {'assessments': assessments})

@login_required(login_url=reverse_lazy('users:login'))
def take_assessment(request, assessment_id):
    """
    Displays an assessment form and processes its submission.
    Expects AI feedback from client-side upon completion.
    """
    assessment = get_object_or_404(Assessment, id=assessment_id)

    if request.method == 'POST':
        form = AssessmentForm(request.POST, assessment=assessment)
        # Assuming AI feedback comes in a hidden field named 'ai_feedback_json'
        ai_feedback_json = request.POST.get('ai_feedback_json')

        if form.is_valid() and ai_feedback_json:
            total_score = 0
            # Create UserAssessment first to link answers to it
            user_assessment = UserAssessment.objects.create(
                user=request.user,
                assessment=assessment,
                score=0, # Temporary score, will update after calculating
                feedback=ai_feedback_json # Store the raw JSON from AI
            )
            
            # Store each answer and calculate total score
            for key, choice_id in form.cleaned_data.items():
                if key.startswith('question_'):
                    question_id = int(key.split('_')[1])
                    question = Question.objects.get(id=question_id)
                    choice = Choice.objects.get(id=choice_id)
                    
                    Answer.objects.create(
                        user_assessment=user_assessment,
                        question=question,
                        choice=choice
                    )
                    total_score += choice.score
            
            user_assessment.score = total_score
            user_assessment.save() # Save again with final score

            messages.success(request, 'Assessment submitted successfully! Review your feedback.')
            return redirect('assessments:assessment_result', user_assessment_id=user_assessment.id)
        else:
            messages.error(request, 'Please correct the errors below or AI feedback was not received.')
    else:
        form = AssessmentForm(assessment=assessment)
        
        # Fetch approved therapists for AI prompt if needed
        # Serialize the queryset correctly for JSON.
        # Use values() to get dicts, and handle potential None values for JSON serialization.
        approved_therapists_raw = User.objects.filter(
            role=User.Role.THERAPIST, is_approved=True
        ).values('username', 'specialization', 'location', 'bio')
        
        # Convert to a list of dicts that are JSON serializable
        approved_therapists_list = []
        for therapist in approved_therapists_raw:
            approved_therapists_list.append({
                'username': therapist['username'],
                'specialization': therapist['specialization'] if therapist['specialization'] else 'N/A',
                'location': therapist['location'] if therapist['location'] else 'N/A',
                'bio': therapist['bio'] if therapist['bio'] else 'N/A',
            })

        # Also serialize questions and choices for client-side JS to collect answers
        questions_data = []
        for question in assessment.question_set.all().prefetch_related('choice_set'):
            choices_data = []
            for choice in question.choice_set.all():
                choices_data.append({
                    'pk': choice.pk,
                    'fields': {
                        'text': choice.text,
                        'score': choice.score
                    }
                })
            questions_data.append({
                'pk': question.pk,
                'fields': {
                    'text': question.text,
                    'choices': choices_data # Nested choices here
                }
            })


        context = {
            'form': form,
            'assessment': assessment,
            'approved_therapists_json': json.dumps(approved_therapists_list),
            'assessment_questions_data': json.dumps(questions_data) # Pass structured questions data
        }
        return render(request, 'assessments/take_assessment.html', context)

@login_required(login_url=reverse_lazy('users:login'))
def assessment_result(request, user_assessment_id):
    """
    Displays the results and AI-generated feedback for a completed assessment.
    """
    ua = get_object_or_404(UserAssessment, id=user_assessment_id, user=request.user)
    
    # Parse the JSON feedback stored in the model
    feedback_data = {}
    try:
        if ua.feedback: # Ensure feedback is not None or empty
            feedback_data = json.loads(ua.feedback)
        else:
            feedback_data = {"summary": "No AI feedback available.", "insights": "", "recommendations": "Please contact support if you believe this is an error."}
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing feedback JSON for UserAssessment ID {ua.id}: {e}")
        feedback_data = {"summary": "Could not load detailed feedback due to a data error.", "insights": "", "recommendations": "Please contact support."}

    return render(request, 'assessments/assessment_result.html', {
        'user_assessment': ua,
        'feedback_data': feedback_data # Pass parsed feedback
    })

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_therapist_or_admin, login_url=reverse_lazy('core:dashboard')) # Restrict to therapists and admins
def my_assessment_results(request):
    """
    Displays a list of all assessments previously taken by the current user.
    This view is now restricted to therapists and admins.
    """
    user_assessments = UserAssessment.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'assessments/my_results.html', {'user_assessments': user_assessments})


# --- Admin Views for Assessment Management ---

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def manage_assessments(request):
    """
    Admin view to list and manage assessments (add, edit, delete).
    """
    assessments = Assessment.objects.all().order_by('name')
    return render(request, 'assessments/manage_assessments.html', {'assessments': assessments})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def add_assessment(request):
    """
    Admin view to add a new assessment.
    """
    if request.method == 'POST':
        form = AssessmentAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assessment added successfully!')
            return redirect('assessments:manage_assessments')
        else:
            messages.error(request, 'Error adding assessment. Please correct the errors.')
    else:
        form = AssessmentAdminForm()
    return render(request, 'assessments/add_edit_assessment.html', {'form': form, 'title': 'Add New Assessment'})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def edit_assessment(request, pk):
    """
    Admin view to edit an existing assessment.
    """
    assessment = get_object_or_404(Assessment, pk=pk)
    if request.method == 'POST':
        form = AssessmentAdminForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assessment updated successfully!')
            return redirect('assessments:manage_assessments')
        else:
            messages.error(request, 'Error updating assessment. Please correct the errors.')
    else:
        form = AssessmentAdminForm(instance=assessment)
    return render(request, 'assessments/add_edit_assessment.html', {'form': form, 'title': 'Edit Assessment'})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def delete_assessment(request, pk):
    """
    Admin view to delete an assessment.
    """
    assessment = get_object_or_404(Assessment, pk=pk)
    if request.method == 'POST':
        assessment.delete()
        messages.info(request, 'Assessment deleted successfully.')
        return redirect('assessments:manage_assessments')
    return render(request, 'assessments/confirm_delete.html', {'item': assessment.name})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def manage_questions(request, assessment_id):
    """
    Admin view to manage questions for a specific assessment.
    """
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    questions = assessment.question_set.all().order_by('id')
    return render(request, 'assessments/manage_questions.html', {'assessment': assessment, 'questions': questions})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def add_question(request, assessment_id):
    """
    Admin view to add a new question to an assessment.
    """
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assessment = assessment
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('assessments:manage_questions', assessment_id=assessment.id)
        else:
            messages.error(request, 'Error adding question. Please correct the errors.')
    else:
        form = QuestionForm()
    return render(request, 'assessments/add_edit_question.html', {'form': form, 'assessment': assessment, 'title': 'Add New Question'})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def edit_question(request, pk):
    """
    Admin view to edit an existing question.
    """
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('assessments:manage_questions', assessment_id=question.assessment.id)
        else:
            messages.error(request, 'Error updating question. Please correct the errors.')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'assessments/add_edit_question.html', {'form': form, 'assessment': question.assessment, 'title': 'Edit Question'})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def delete_question(request, pk):
    """
    Admin view to delete a question.
    """
    question = get_object_or_404(Question, pk=pk)
    assessment_id = question.assessment.id
    if request.method == 'POST':
        question.delete()
        messages.info(request, 'Question deleted successfully.')
        return redirect('assessments:manage_questions', assessment_id=assessment_id)
    return render(request, 'assessments/confirm_delete.html', {'item': question.text})

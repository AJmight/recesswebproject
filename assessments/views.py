# assessments/views.py

import json
from django.contrib import messages 
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model

from django.db import transaction

from .models import Assessment, Choice, Question, UserAssessment, Answer
from .forms import AssessmentForm, AssessmentAdminForm, QuestionForm, ChoiceForm, AssessmentUploadForm

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_admin

def is_therapist_or_admin(user):
    return user.is_authenticated and (user.is_therapist or user.is_admin)

# --- Client Views ---

@login_required(login_url=reverse_lazy('users:login'))
def assessment_list(request):
    assessments = Assessment.objects.all().order_by('name')
    return render(request, 'assessments/assessment_list.html', {'assessments': assessments})

@login_required(login_url=reverse_lazy('users:login'))
def take_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)

    if request.method == 'POST':
        print("Received POST request for take_assessment.") # DEBUG
        form = AssessmentForm(request.POST, assessment=assessment)
        ai_feedback_json = request.POST.get('ai_feedback_json')

        print(f"Form is valid: {form.is_valid()}") # DEBUG
        print(f"AI Feedback JSON received (first 100 chars): {ai_feedback_json[:100] if ai_feedback_json else 'None/Empty'}") # DEBUG
        print(f"Length of AI Feedback JSON: {len(ai_feedback_json) if ai_feedback_json else 0}") # DEBUG

        if form.is_valid() and ai_feedback_json:
            total_score = 0
            try:
                user_assessment = UserAssessment.objects.create(
                    user=request.user,
                    assessment=assessment,
                    score=0, # Temporary score
                    feedback=ai_feedback_json # Store the raw JSON from AI
                )
                print(f"UserAssessment created with ID: {user_assessment.id}") # DEBUG
                
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
                user_assessment.save()
                print(f"UserAssessment updated with final score: {user_assessment.score}") # DEBUG

                messages.success(request, 'Assessment submitted successfully! Review your feedback.')
                return redirect('assessments:assessment_result', user_assessment_id=user_assessment.id)
            except Exception as e:
                print(f"Error during UserAssessment creation/saving: {e}") # DEBUG
                messages.error(request, f"An error occurred while saving your assessment: {e}")
                # Render the form again with errors if saving fails
                return render(request, 'assessments/take_assessment.html', {'form': form, 'assessment': assessment})
        else:
            messages.error(request, 'Please correct the errors below or AI feedback was not received.')
            # If AI feedback is missing, log it specifically
            if not ai_feedback_json:
                print("AI feedback JSON was missing or empty.") # DEBUG
            print(f"Form errors: {form.errors}") # DEBUG
    else: # GET request
        form = AssessmentForm(assessment=assessment)
        
        approved_therapists_raw = User.objects.filter(
            role=User.Role.THERAPIST, is_approved=True
        ).values('username', 'specialization', 'location', 'bio')
        
        approved_therapists_list = []
        for therapist in approved_therapists_raw:
            approved_therapists_list.append({
                'username': therapist['username'],
                'specialization': therapist['specialization'] if therapist['specialization'] else 'N/A',
                'location': therapist['location'] if therapist['location'] else 'N/A',
                'bio': therapist['bio'] if therapist['bio'] else 'N/A',
            })

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
                    'choices': choices_data
                }
            })

        context = {
            'form': form,
            'assessment': assessment,
            'approved_therapists_json': json.dumps(approved_therapists_list),
            'assessment_questions_data': json.dumps(questions_data)
        }
        return render(request, 'assessments/take_assessment.html', context)

@login_required(login_url=reverse_lazy('users:login'))
def assessment_result(request, user_assessment_id):
    ua = get_object_or_404(UserAssessment, id=user_assessment_id, user=request.user)
    
    feedback_data = {}
    try:
        if ua.feedback:
            feedback_data = json.loads(ua.feedback)
        else:
            feedback_data = {"summary": "No AI feedback available.", "insights": "", "recommendations": "Please contact support if you believe this is an error."}
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing feedback JSON for UserAssessment ID {ua.id}: {e}")
        feedback_data = {"summary": "Could not load detailed feedback due to a data error.", "insights": "", "recommendations": "Please contact support."}

    return render(request, 'assessments/assessment_result.html', {
        'user_assessment': ua,
        'feedback_data': feedback_data
    })

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_therapist_or_admin, login_url=reverse_lazy('core:dashboard'))
def my_assessment_results(request):
    user_assessments = UserAssessment.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'assessments/my_results.html', {'user_assessments': user_assessments})


# --- Admin Views for Assessment Management ---

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def manage_assessments(request):
    assessments = Assessment.objects.all().order_by('name')
    return render(request, 'assessments/manage_assessments.html', {'assessments': assessments})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def add_assessment(request):
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
    assessment = get_object_or_404(Assessment, pk=pk)
    if request.method == 'POST':
        assessment.delete()
        messages.info(request, 'Assessment deleted successfully.')
        return redirect('assessments:manage_assessments')
    return render(request, 'assessments/confirm_delete.html', {'item': assessment.name})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def manage_questions(request, assessment_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    questions = assessment.question_set.all().order_by('id')
    return render(request, 'assessments/manage_questions.html', {'assessment': assessment, 'questions': questions})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def add_question(request, assessment_id):
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
    question = get_object_or_404(Question, pk=pk)
    assessment_id = question.assessment.id
    if request.method == 'POST':
        question.delete()
        messages.info(request, 'Question deleted successfully.')
        return redirect('assessments:manage_questions', assessment_id=assessment_id)
    return render(request, 'assessments/confirm_delete.html', {'item': question.text})


@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def upload_assessment(request):
    if request.method == 'POST':
        form = AssessmentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            json_file = request.FILES['json_file']
            try:
                file_content = json_file.read().decode('utf-8')
                assessment_data = json.loads(file_content)

                with transaction.atomic():
                    assessment_name = assessment_data.get('name')
                    assessment_description = assessment_data.get('description')
                    assessment_instructions = assessment_data.get('instructions', '')

                    if not assessment_name or not assessment_description:
                        messages.error(request, "JSON file must contain 'name' and 'description' for the assessment.")
                        return render(request, 'assessments/upload_assessment.html', {'form': form, 'title': 'Upload Assessment'})

                    if Assessment.objects.filter(name=assessment_name).exists():
                        messages.error(request, f"An assessment with the name '{assessment_name}' already exists. Please use a unique name or edit the existing one.")
                        return render(request, 'assessments/upload_assessment.html', {'form': form, 'title': 'Upload Assessment'})

                    assessment = Assessment.objects.create(
                        name=assessment_name,
                        description=assessment_description,
                        instructions=assessment_instructions
                    )

                    questions_data = assessment_data.get('questions', [])
                    if not questions_data:
                        messages.warning(request, f"Assessment '{assessment_name}' created, but no questions were found in the JSON. You can add them manually.")
                        return redirect('assessments:manage_questions', assessment_id=assessment.id)

                    for q_data in questions_data:
                        question_text = q_data.get('text')
                        if not question_text:
                            raise ValueError("Question text is missing in one of the questions.")

                        question = Question.objects.create(
                            assessment=assessment,
                            text=question_text
                        )

                        choices_data = q_data.get('choices', [])
                        if not choices_data:
                            messages.warning(request, f"Question '{question_text}' added, but no choices were found. Add them manually.")
                            continue

                        for c_data in choices_data:
                            choice_text = c_data.get('text')
                            choice_score = c_data.get('score')
                            
                            if choice_text is None or choice_score is None:
                                raise ValueError(f"Choice text or score is missing for question '{choice_text}' in question '{question_text}'.")
                            
                            try:
                                choice_score = int(choice_score)
                            except ValueError:
                                raise ValueError(f"Choice score for '{choice_text}' in question '{question_text}' is not a valid integer.")

                            Choice.objects.create(
                                question=question,
                                text=choice_text,
                                score=choice_score
                            )
            
                messages.success(request, f"Assessment '{assessment_name}' uploaded and created successfully!")
                return redirect('assessments:manage_questions', assessment_id=assessment.id)

            except json.JSONDecodeError:
                messages.error(request, "Invalid JSON file. Please ensure the file is correctly formatted JSON.")
            except ValueError as e:
                messages.error(request, f"Error processing assessment data: {e}")
            except Exception as e:
                messages.error(request, f"An unexpected error occurred during upload: {e}")
        else:
            messages.error(request, "Error with file upload. Please ensure you selected a file.")
    else:
        form = AssessmentUploadForm()
    return render(request, 'assessments/upload_assessment.html', {'form': form, 'title': 'Upload Assessment'})
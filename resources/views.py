from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Resource
from .forms import ResourceForm

# Helper test for admin users
def is_admin(user):
    return user.is_authenticated and user.is_staff # Django's built-in is_staff for admin access

@login_required
def resource_list(request):
    resources = Resource.objects.all()
    return render(request, 'resources/resource_list.html', {'resources': resources})

@login_required
@user_passes_test(is_admin, login_url='users:login')
def manage_resources(request):
    """
    Allows admins to add, edit, and delete resources.
    """
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Resource added successfully!")
            return redirect('resources:manage_resources')
    else:
        form = ResourceForm()
    resources = Resource.objects.all()

    context = {
        'form': form,
        'resources': resources
    }
    return render(request, 'resources/manage_resources.html', context)
@login_required
@user_passes_test(is_admin)
def add_resource(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = request.user
            resource.save()
            messages.success(request, 'Resource added successfully!')
            return redirect('resources:manage_resources')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResourceForm()
    return render(request, 'resources/add_edit_resource.html', {'form': form, 'title': 'Add New Resource'})

@login_required
@user_passes_test(is_admin)
def edit_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully!')
            return redirect('resources:manage_resources')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResourceForm(instance=resource)
    return render(request, 'resources/add_edit_resource.html', {'form': form, 'title': 'Edit Resource'})

@login_required
@user_passes_test(is_admin)
def delete_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        resource.delete()
        messages.info(request, 'Resource deleted.')
        return redirect('resources:manage_resources')
    return render(request, 'resources/confirm_delete.html', {'item': resource.title})
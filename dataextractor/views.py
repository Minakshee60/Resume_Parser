from django.shortcuts import render, redirect
from pyresparser import ResumeParser
from .models import Resume, UploadResumeModelForm
from django.contrib import messages
from django.conf import settings
import os

def homepage(request):
    if request.method == 'POST':
        file_form = UploadResumeModelForm(request.POST, request.FILES)
        files = request.FILES.getlist('resume')
        resumes_data = []
        
        if file_form.is_valid():
            for file in files:
                try:
                    # Saving the uploaded resume file
                    resume = Resume(resume=file)
                    resume.save()
                    
                    # Extracting resume data using ResumeParser
                    parser = ResumeParser(os.path.join(settings.MEDIA_ROOT, resume.resume.name))
                    data = parser.get_extracted_data()

                    # Check for extracted data validity and handle missing fields
                    if not data:
                        messages.error(request, f"Failed to extract data from {file.name}. Please check the format.")
                        continue
                    
                    resume.name = data.get('name', None)
                    resume.email = data.get('email', None)
                    resume.mobile_number = data.get('mobile_number', None)
                    resume.education = ', '.join(data.get('degree', [])) if data.get('degree') else None
                    resume.company_name = ', '.join(data.get('company_names', [])) if data.get('company_names') else None
                    resume.college_name = data.get('college_name', None)
                    resume.designation = data.get('designation', None)
                    resume.total_experience = data.get('total_experience', None)
                    resume.skills = ', '.join(data.get('skills', [])) if data.get('skills') else None
                    resume.experience = ', '.join(data.get('experience', [])) if data.get('experience') else None

                    # Save the populated resume object
                    resume.save()
                    resumes_data.append(data)
                except Exception as e:
                    messages.error(request, f"An error occurred while processing {file.name}: {str(e)}")
                    continue

            messages.success(request, 'Resumes uploaded and parsed successfully!')
            resumes = Resume.objects.all()
            return render(request, 'base.html', {'form': file_form, 'resumes': resumes})

    else:
        form = UploadResumeModelForm()
    
    return render(request, 'base.html', {'form': form})

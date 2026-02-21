from django.shortcuts import render
from .utils import (
    process_resume, 
    generate_insights, 
    get_improvement_strategies,
    extract_top_keywords,
    generate_resume_template
)
from .models import ScannedResume

def checker_view(request):
    context = {}
    if request.method == "POST":
        job_desc = request.POST.get('job_description')
        resume_files = request.FILES.getlist('resume_file')
        
        if job_desc and resume_files:
            results = []
            for f in resume_files:
                score, missing = process_resume(f, job_desc)
                
                # --- SAVE TO DATABASE ---
                ScannedResume.objects.create(
                    filename=f.name,
                    resume_file=f,
                    score=score
                )
                # ------------------------

                results.append({
                    'filename': f.name,
                    'score': score,
                    'missing': missing,
                    'strategies': get_improvement_strategies(score, missing)
                })
            
            context['bulk_results'] = sorted(results, key=lambda x: x['score'], reverse=True)
            
    return render(request, 'checker.html', context)


def generator_view(request):
    """
    Logic for the 'AI Template Builder' page.
    Extracts keywords from a JD and builds a blueprint.
    """
    context = {}
    
    if request.method == "POST":
        job_desc = request.POST.get('job_description')
        
        # Persist the Job Description
        context['job_description'] = job_desc

        if job_desc:
            # 1. Identify the most important technical terms in the JD
            keywords = extract_top_keywords(job_desc)
            
            # 2. Construct a formatted text template using those keywords
            template = generate_resume_template(keywords)
            
            # 3. Pass the template to generator.html
            context.update({
                'template': template # Used in {{ template }}
            })
            
    return render(request, 'generator.html', context)


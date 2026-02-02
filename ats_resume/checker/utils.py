import re
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean_text(text):
    """Removes special characters and converts to lowercase."""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return ' '.join(text.split())

def process_resume(resume_file, job_desc):
    """Extracts text, calculates similarity, and finds missing keywords."""
    # 1. Extract Text from PDF
    resume_text = ""
    try:
        reader = PdfReader(resume_file)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                resume_text += content
    except Exception as e:
        print(f"Extraction Error: {e}")
        return 0, []

    # 2. Extract Missing Keywords (Set Difference)
    # Get words 4+ letters long, excluding common generic words
    stop_words = {'work', 'experience', 'team', 'required', 'years', 'ability', 'skills', 'responsibilities'}
    jd_words = set(re.findall(r'\b\w{4,}\b', job_desc.lower()))
    resume_words = set(re.findall(r'\b\w{4,}\b', resume_text.lower()))
    
    missing_list = sorted(list(jd_words - resume_words - stop_words))[:12]

    # 3. Calculate Similarity Score
    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(job_desc)
    
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    vectors = vectorizer.fit_transform([cleaned_resume, cleaned_jd])
    
    similarity = cosine_similarity(vectors)[0][1]
    
    # 4. Score Boosting Logic
    # raw cosine is usually low (0.1 - 0.3). 
    # Square root boost + linear scaling makes it feel professional (0.2 -> 65%)
    display_score = round((similarity ** 0.5) * 100, 1)
    
    # Cap at 99.9% unless it's an exact text match
    if display_score > 99 and cleaned_resume != cleaned_jd:
        display_score = 98.5

    return display_score, missing_list

def generate_insights(missing_keywords):
    """Categorizes missing words into professional feedback sentences."""
    insights = []
    categories = {
        'technical': ['python', 'java', 'sql', 'react', 'aws', 'api', 'django', 'fastapi', 'docker', 'git'],
        'soft_skills': ['leadership', 'communication', 'management', 'agile', 'analytical', 'problem'],
        'education': ['degree', 'bachelor', 'master', 'certification', 'university', 'phd']
    }

    if not missing_keywords:
        return ["Your resume is perfectly aligned with the job's core requirements!"]

    for word in missing_keywords:
        if any(tech in word for tech in categories['technical']):
            insights.append(f"Technical Gap: The JD emphasizes '{word}'. Add this to your Skills section.")
        elif any(soft in word for soft in categories['soft_skills']):
            insights.append(f"Soft Skill: '{word}' is a key requirement. Mention an example in your experience.")
        elif any(edu in word for edu in categories['education']):
            insights.append(f"Qualification: The system noted a missing mention of '{word}' or related education.")
        
        if len(insights) >= 5: break # Keep it concise

    # Add a general tip if specific categories aren't hit
    if len(insights) < 3:
        insights.append("Keyword Optimization: Use industry-standard terminology found in the JD to pass ATS filters.")

    return insights

def get_improvement_strategies(score, missing_keywords=None):
    # Get a specific example of a gap if available
    gap_example = missing_keywords[0] if missing_keywords else "key industry terms"
    
    if score < 40:
        return [
            f"Critical Gap: Your resume completely lacks mention of '{gap_example}'.",
            "Formatting: Ensure your resume is a single-column layout.",
            "Action: Standardize headings like 'Work Experience' and 'Education'."
        ]
    elif score < 75:
        return [
            f"Optimization: Increase keyword density for terms like '{gap_example}'.",
            "Quantification: Use numbers (e.g., 'Improved speed by 20%') to stand out.",
            "Context: Ensure missing keywords are placed within professional experience."
        ]
    else:
        return [
            "Refinement: You are a strong match. Focus on active verbs like 'Spearheaded' or 'Architected'.",
            "Strategy: Double-check that your contact links (LinkedIn/GitHub) are clickable in the PDF.",
            "Final Polish: Tailor your Summary to mention the company name to show high intent."
        ]

def generate_resume_template(keywords):
    keyword_str = ", ".join(keywords)
    template = f"""
[NAME] | [PHONE] | [EMAIL] | [LINKEDIN/PORTFOLIO]

SUMMARY
-----------------------------------------------------------
[Write 2-3 sentences. Mention you have experience with {keywords[0] if keywords else 'key industry skills'}. 
Tip: Use 'Action Verbs' like Led, Developed, or Optimized.]

TECHNICAL SKILLS (ATS Primary Scan Area)
-----------------------------------------------------------
Core Competencies: {keyword_str}
[User Note: Do not remove these keywords; they are why the AI flagged this JD!]

PROFESSIONAL EXPERIENCE
-----------------------------------------------------------
[Most Recent Job Title] | [Company Name] | [Dates]
• Led a project involving {keywords[1] if len(keywords)>1 else 'industry standards'} resulting in a [X]% increase in efficiency.
• Managed [Specific Task] using {keywords[2] if len(keywords)>2 else 'relevant tools'}.
• [Tip: Always use numbers (%, $, #) to prove your impact to the recruiter.]

EDUCATION
-----------------------------------------------------------
[Degree Name] | [University Name] | [Year]
    """
    return template

def extract_top_keywords(job_desc):
    """Extracts high-importance words for the template generator."""
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([job_desc])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]
    keyword_index = scores.argsort()[-10:][::-1]
    return [feature_names[i] for i in keyword_index]
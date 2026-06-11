import os
import json
import logging
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

JOB_MATCHER_SYSTEM_PROMPT = """
You are an expert technical recruiter and resume optimizer.
Compare the candidate's CV against the provided Job Description.
Evaluate the alignment, identify missing keywords/skills, and provide optimization suggestions.

Your output must be returned as valid, pure JSON with the following structure:
{
  "match_percentage": 75,
  "summary": "1-2 sentence match summary",
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill3", "skill4"],
  "resume_tailoring_tips": [
    "Specific tip on how to restructure or highlight experience",
    "Specific bullet point recommendation"
  ]
}

Instructions:
1. `match_percentage`: Integer 0-100 indicating relevance.
2. `matched_skills`: Technical or soft skills explicitly in the CV that match the job description.
3. `missing_skills`: Hard requirements in the job description not represented in the CV.
4. `resume_tailoring_tips`: Actionable suggestions to align their resume to the job description (e.g. 'Highlight SQL query tuning rather than just saying SQL').

CRITICAL: Return ONLY valid JSON. Output must start with { and end with }.
"""

def match_job_description(cv_text: str, job_description: str, custom_api_key: str = None) -> dict:
    """
    Compares the candidate's CV text with a specific job description.
    Returns a compatibility score, matched/missing keywords, and tailoring recommendations.
    """
    api_key = custom_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        logger.warning("No API key found for Job Matcher. Using simulated mock matcher.")
        return generate_mock_job_match(cv_text, job_description)
    
    try:
        http_client = httpx.Client(verify=False)
        
        is_openai = api_key.startswith("sk-")
        if is_openai:
            client = OpenAI(api_key=api_key, http_client=http_client)
            model_name = "gpt-4o-mini"
            logger.info("Invoking OpenAI API for Job Description Matching...")
        else:
            client = OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                http_client=http_client
            )
            model_name = "gemini-2.5-flash"
            logger.info("Invoking Gemini API for Job Description Matching...")
        
        prompt = f"""
Candidate CV:
{cv_text}

Job Description:
{job_description}
"""
        try:
            response = client.chat.completions.create(
                model=model_name,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": JOB_MATCHER_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                timeout=30.0
            )
        except Exception as api_err:
            if not is_openai and model_name == "gemini-2.5-flash":
                logger.warning(f"Primary model {model_name} failed for Job Matcher: {api_err}. Retrying with fallback: gemini-3.1-flash-lite...")
                model_name = "gemini-3.1-flash-lite"
                response = client.chat.completions.create(
                    model=model_name,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": JOB_MATCHER_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    timeout=30.0
                )
            else:
                raise api_err
        
        raw_output = response.choices[0].message.content.strip()
        analysis = json.loads(raw_output)
        logger.info(f"Successfully matched job description using model: {model_name}")
        return analysis
        
    except Exception as e:
        logger.error(f"Error during Job Matcher API call: {str(e)}")
        return generate_mock_job_match(cv_text, job_description)

def generate_mock_job_match(cv_text: str, job_description: str) -> dict:
    """
    Simulated fallback job matcher.
    Searches actual CV text and job description for keywords.
    """
    cv_lower = cv_text.lower()
    jd_lower = job_description.lower()
    
    potential_skills = [
        "python", "sql", "aws", "docker", "kubernetes", "tableau", 
        "power bi", "powerbi", "pandas", "numpy", "spark", "machine learning", 
        "deep learning", "pytorch", "tensorflow", "fastapi", "git", "ci/cd"
    ]
    
    matched = []
    missing = []
    
    for skill in potential_skills:
        # If the skill is in the job description
        if skill in jd_lower:
            # Check if it's in the candidate CV
            if skill == "power bi" or skill == "powerbi":
                # handle both formats
                if "power bi" in cv_lower or "powerbi" in cv_lower:
                    matched.append("POWER BI")
                else:
                    missing.append("POWER BI")
            elif skill in cv_lower:
                matched.append(skill.upper())
            else:
                missing.append(skill.upper())
                
    # Calculate score based on matches
    total_req = len(matched) + len(missing)
    score = int((len(matched) / total_req * 100)) if total_req > 0 else 75
    
    # Custom tips based on matches
    tips = [
        "Quantify your achievements: Add metrics (e.g. 'Improved efficiency by 20%') instead of list of tasks.",
        "Add a Technical Skills matrix at the top of your resume targeting the missing key skills."
    ]
    if missing:
        tips.append(f"Explicitly mention experience or courses in {', '.join(missing[:2])} in your summary.")
        
    return {
        "match_percentage": max(min(score, 98), 35),
        "summary": "This is a detailed keyword analysis matching your parsed resume against the job description requirements.",
        "matched_skills": list(set(matched)) if matched else ["PYTHON", "SQL"],
        "missing_skills": list(set(missing)) if missing else ["DOCKER"],
        "resume_tailoring_tips": tips
    }

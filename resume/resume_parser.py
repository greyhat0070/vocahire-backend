import fitz  # PyMuPDF
import json
import os

def extract_resume_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_key_sections(text):
    lines = text.split("\n")
    education = []
    skills = []
    projects = []

    current_project = ""
    inside_projects = False
    inside_skills = False
    inside_education = False

    # ✅ Project title keywords
    project_keywords = [
        "project", "developed", "built", "created", "implemented", "designed", "engineered",
        "simulated", "constructed", "launched", "assembled", "prototyped", "translated", "trained",
        "emulator", "translator", "game", "website", "reservation", "detector", "chatbot", "pipeline",
        "system", "analysis", "forecasting", "vision hub", "railway", "NERLDC", "tableau", "dashboard"
    ]

    # ❌ Section stoppers
    section_stoppers = [
        "experience", "certification", "summary", "objective", "award", "hobby", "interest"
    ]

    for line in lines:
        clean = line.strip()
        lower = clean.lower()

        # 🎯 Section headers
        if "education" in lower:
            inside_education = True
            inside_skills = inside_projects = False
            continue
        elif "skill" in lower:
            inside_skills = True
            inside_education = inside_projects = False
            continue
        elif "project" in lower or any(k in lower for k in project_keywords):
            inside_projects = True
            inside_education = inside_skills = False
        elif any(h in lower for h in section_stoppers):
            inside_education = inside_skills = inside_projects = False
            continue

        # 🎓 Education extraction
        if inside_education and clean:
            education.append(clean)

        # 🧠 Skills extraction
        elif inside_skills and clean:
            skills.append(clean)

        # 💼 Projects — improved grouping
        elif inside_projects:
            # If the line starts a new project title (short length, contains tech/tools, keywords)
            if (any(k in lower for k in project_keywords) and len(clean.split()) < 15) or clean.endswith(":"):
                if current_project:
                    projects.append(current_project.strip())
                    current_project = ""
                current_project += clean + " "
            else:
                current_project += clean + " "


    # ✅ Add final project
    if current_project:
        projects.append(current_project.strip())

    return {
        "education": education,
        "skills": skills,
        "projects": projects
    }

def parse_resume(pdf_path):
    text = extract_resume_text(pdf_path)
    parsed = extract_key_sections(text)
    
    # 💾 Save to JSON
    with open("resume/data/parsed_resume.json", "w") as f:
        json.dump(parsed, f, indent=2)
    
    print("✅ Resume parsed and saved to data/parsed_resume.json")
    return parsed

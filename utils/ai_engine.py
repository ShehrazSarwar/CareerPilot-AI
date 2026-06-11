import os
import json
import logging
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from utils.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

load_dotenv()

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_custom_technologies(role_name: str) -> list:
    r_lower = role_name.lower()
    if any(k in r_lower for k in ["video", "editor", "film", "animator", "motion", "creative", "media"]):
        return ["Adobe Premiere Pro", "After Effects", "DaVinci Resolve", "Final Cut Pro", "Adobe Photoshop"]
    if any(k in r_lower for k in ["design", "ux", "ui", "product design", "graphic", "creative"]):
        return ["Figma", "Adobe XD", "Sketch", "User Research", "Wireframing"]
    if any(k in r_lower for k in ["marketing", "seo", "sem", "ads", "growth", "copywriter", "content"]):
        return ["Google Analytics", "SEMrush", "Google Ads", "WordPress", "Copywriting"]
    if any(k in r_lower for k in ["sales", "business development", "account"]):
        return ["Salesforce CRM", "HubSpot", "LinkedIn Sales Navigator", "Cold Outreach"]
    if any(k in r_lower for k in ["hr", "human resources", "recruiter", "talent", "people"]):
        return ["Workday HRIS", "LinkedIn Recruiter", "ATS Software", "Excel"]
    if any(k in r_lower for k in ["finance", "financial", "accounting", "valuation"]):
        return ["Excel", "Bloomberg Terminal", "SQL", "Financial Modeling"]
    if any(k in r_lower for k in ["qa", "testing", "tester", "quality assurance"]):
        return ["Selenium", "Playwright", "Postman", "Jira", "Git"]
    if any(k in r_lower for k in ["cloud", "devops", "sre", "infrastructure", "platform"]):
        return ["AWS / Azure", "Terraform", "Docker", "Kubernetes", "CI/CD"]
    if any(k in r_lower for k in ["project", "program", "product", "manager", "owner", "scrum", "agile"]):
        return ["Jira", "Confluence", "Asana", "Agile / Scrum", "Product Analytics"]
    if any(k in r_lower for k in ["data analyst", "business analyst", "bi", "reporting"]):
        return ["SQL", "PowerBI / Tableau", "Excel", "Python", "Pandas"]
    if any(k in r_lower for k in ["data scientist", "data science", "machine learning", "ml", "nlp"]):
        return ["Python", "Scikit-Learn", "Pandas", "SQL", "Jupyter Notebooks"]
    if any(k in r_lower for k in ["ai", "generative", "llm", "prompt", "agent"]):
        return ["Python", "LangChain", "OpenAI API", "Vector Databases", "Git"]
    if any(k in r_lower for k in ["security", "cyber", "pentest", "soc"]):
        return ["SIEM / Splunk", "Wireshark", "Nmap", "Linux", "Firewalls"]
    return ["Domain Tools", "Excel / Sheets", "Project Tools"]

def get_custom_certifications(role_name: str) -> list:
    r_lower = role_name.lower()
    if any(k in r_lower for k in ["video", "editor", "film", "animator", "motion", "creative", "media"]):
        return [
            {"name": "Adobe Certified Professional in Video Design", "provider": "Adobe", "reason": "Validates professional competence in Premiere Pro and After Effects."},
            {"name": "DaVinci Resolve Certified End User", "provider": "Blackmagic Design", "reason": "Proves deep knowledge in professional color grading, editing, and audio mixing."},
            {"name": "Final Cut Pro Certified User", "provider": "Apple", "reason": "Establishes mastery over macOS-native video editing workflows."}
        ]
    if any(k in r_lower for k in ["design", "ux", "ui", "product design", "graphic", "creative"]):
        return [
            {"name": "Google UX Design Professional Certificate", "provider": "Coursera / Google", "reason": "Provides a comprehensive foundation in UX research and Figma prototyping."},
            {"name": "Certified Usability Analyst (CUA)", "provider": "Human Factors International", "reason": "Industry standard credential for user-centered design and testing."},
            {"name": "Figma Creator Certificate", "provider": "Figma", "reason": "Validates expert capabilities in advanced component systems, variables, and design workflows."}
        ]
    if any(k in r_lower for k in ["marketing", "seo", "sem", "ads", "growth", "copywriter", "content"]):
        return [
            {"name": "Google Ads Search Certification", "provider": "Google", "reason": "Validates expertise in planning and optimizing Google Search ad campaigns."},
            {"name": "Google Analytics 4 (GA4) Certification", "provider": "Google", "reason": "Ensures capability in tracking customer journeys and conversion events."},
            {"name": "HubSpot Inbound Marketing Certification", "provider": "HubSpot", "reason": "Validates competence in content creation, SEO, and lead nurturing."}
        ]
    if any(k in r_lower for k in ["sales", "business development", "account"]):
        return [
            {"name": "Salesforce Certified Administrator", "provider": "Salesforce", "reason": "Validates core pipeline management and CRM customization capabilities."},
            {"name": "HubSpot Sales Software Certification", "provider": "HubSpot", "reason": "Proves mastery of automated email templates, outreach pipelines, and sequences."},
            {"name": "Certified Professional Salesperson (CPSP)", "provider": "NASP", "reason": "Establishes credibility in consultative sales strategies and relationship building."}
        ]
    if any(k in r_lower for k in ["hr", "human resources", "recruiter", "talent", "people"]):
        return [
            {"name": "Associate Professional in Human Resources (aPHR)", "provider": "HRCI", "reason": "Validates baseline HR policies, operational tasks, and legal requirements."},
            {"name": "SHRM Certified Professional (SHRM-CP)", "provider": "SHRM", "reason": "Gold standard credential validating leadership and talent management strategy."},
            {"name": "LinkedIn Recruiter Certification", "provider": "LinkedIn", "reason": "Proves elite candidate sourcing and talent mapping capabilities."}
        ]
    if any(k in r_lower for k in ["finance", "financial", "accounting", "valuation"]):
        return [
            {"name": "Financial Modeling & Valuation Analyst (FMVA)", "provider": "CFI", "reason": "Comprehensive industry-recognized standard for hands-on corporate finance and modeling."},
            {"name": "Chartered Financial Analyst (CFA) Level 1", "provider": "CFA Institute", "reason": "Gold standard credential for asset management and deep investment analysis."},
            {"name": "Certified Public Accountant (CPA)", "provider": "AICPA / State Boards", "reason": "Validates ultimate expertise in auditing, financial accounting, and tax compliance."}
        ]
    if any(k in r_lower for k in ["qa", "testing", "tester", "quality assurance"]):
        return [
            {"name": "ISTQB Certified Tester Foundation Level", "provider": "ISTQB", "reason": "Global standard certification for software testing principles and processes."},
            {"name": "Certified Software Test Engineer (CSTE)", "provider": "ISQI", "reason": "Proves technical expertise in automation testing scripts and quality models."},
            {"name": "Selenium Certified Professional", "provider": "Selenium Academy", "reason": "Validates capabilities in building web automation frameworks using Selenium WebDriver."}
        ]
    if any(k in r_lower for k in ["cloud", "devops", "sre", "infrastructure", "platform"]):
        return [
            {"name": "AWS Certified Solutions Architect - Associate", "provider": "Amazon Web Services", "reason": "Establishes core architectural knowledge of cloud deployments."},
            {"name": "HashiCorp Certified: Terraform Associate", "provider": "HashiCorp", "reason": "Validates enterprise-level Infrastructure as Code skills."},
            {"name": "Certified Kubernetes Administrator (CKA)", "provider": "CNCF", "reason": "Highly regarded credential proving hands-on Kubernetes administration."}
        ]
    if any(k in r_lower for k in ["project", "program", "product", "manager", "owner", "scrum", "agile"]):
        return [
            {"name": "Project Management Professional (PMP)", "provider": "PMI", "reason": "Premier global project management credential for traditional and hybrid workflows."},
            {"name": "Certified ScrumMaster (CSM)", "provider": "Scrum Alliance", "reason": "Validates agile sprint management, backlog grooming, and scrum theory."},
            {"name": "Professional Scrum Product Owner I (PSPO I)", "provider": "Scrum.org", "reason": "Tests value optimization and backlog delivery."}
        ]
    return [
        {"name": f"Professional {role_name} Certification", "provider": "Industry Institute", "reason": f"Establishes a solid foundational background for a career as a {role_name}."},
        {"name": f"Certified {role_name} Specialist", "provider": "Standard Credentialing Body", "reason": f"Validates the core tools and workflows expected of a {role_name}."}
    ]

def get_custom_project_ideas(role_name: str) -> list:
    r_lower = role_name.lower()
    if any(k in r_lower for k in ["video", "editor", "film", "animator", "motion", "creative", "media"]):
        return [
            {
                "title": "Cinematic Short Film Edit & Color Grading Reel",
                "description": "Ingest raw multi-cam footage, sync audio, perform A/B roll cuts, and apply advanced color correction/grading utilizing DaVinci Resolve or Premiere Pro.",
                "difficulty": "Intermediate",
                "technologies": ["Adobe Premiere Pro", "DaVinci Resolve", "Adobe After Effects"]
            },
            {
                "title": "30-Second Commercial Motion Graphics Promo",
                "description": "Design a fast-paced promo video with animated typography, custom transitions, masking, and audio sound design to showcase a product launch.",
                "difficulty": "Advanced",
                "technologies": ["Adobe After Effects", "Adobe Premiere Pro", "Audition"]
            }
        ]
    if any(k in r_lower for k in ["design", "ux", "ui", "product design", "graphic", "creative"]):
        return [
            {
                "title": "Mobile App Design Case Study: Food Delivery UX",
                "description": "Run user research, build user personas, draw wireframes, and design a high-fidelity interactive prototype in Figma utilizing auto-layout and components.",
                "difficulty": "Intermediate",
                "technologies": ["Figma", "User Research", "Wireframing"]
            },
            {
                "title": "SaaS Platform Design System",
                "description": "Create a comprehensive, accessible (WCAG compliant) design system in Figma with buttons, typography scale, color palette, and input states.",
                "difficulty": "Advanced",
                "technologies": ["Figma", "Design Systems", "WCAG Accessibility"]
            }
        ]
    if any(k in r_lower for k in ["marketing", "seo", "sem", "ads", "growth", "copywriter", "content"]):
        return [
            {
                "title": "Comprehensive E-Commerce Growth Strategy & SEO Audit",
                "description": "Perform keyword research and SEO site audit for a mock retail site. Create a content calendar and mock landing page optimization blueprint.",
                "difficulty": "Intermediate",
                "technologies": ["SEMrush/Ahrefs", "Google Analytics", "On-Page SEO"]
            },
            {
                "title": "Mock paid advertising campaign & conversion funnel dashboard",
                "description": "Design a complete paid ads strategy. Model conversion rates and calculate customer acquisition cost (CAC) and return on ad spend (ROAS).",
                "difficulty": "Intermediate",
                "technologies": ["Excel / Google Sheets", "Meta Ads Manager (Mock)", "GA4"]
            }
        ]
    if any(k in r_lower for k in ["finance", "financial", "accounting", "valuation"]):
        return [
            {
                "title": "Three-Statement Valuation Model (DCF & Comps)",
                "description": "Construct a fully integrated 3-statement forecasting model (Income, Balance, Cash Flow) for a public company and run a DCF valuation.",
                "difficulty": "Intermediate",
                "technologies": ["Excel", "Financial Modeling", "DCF Analysis"]
            },
            {
                "title": "Portfolio Risk & Performance Dashboard",
                "description": "Use Python and Pandas to fetch historical stock prices, calculate portfolio returns, volatility, Sharpe ratio, and visualize metrics.",
                "difficulty": "Advanced",
                "technologies": ["Python", "Pandas", "Matplotlib / Streamlit", "YFinance"]
            }
        ]
    techs = get_custom_technologies(role_name)
    return [
        {
            "title": f"Comprehensive {role_name} Project",
            "description": f"Develop an end-to-end portfolio project applying core workflows, tools, and standards expected of a professional {role_name}.",
            "difficulty": "Intermediate",
            "technologies": techs[:3]
        }
    ]

def get_custom_interview_prep(role_name: str) -> list:
    r_lower = role_name.lower()
    if any(k in r_lower for k in ["video", "editor", "film", "animator", "motion", "creative", "media"]):
        return [
            {
                "question": "How do you manage your project directory structure and backup strategy for video assets?",
                "answer": "Maintain a strict folder template: Raw Footage, Audio, Graphics, SFX, Projects, and Exports. Employ the 3-2-1 backup rule (3 copies, 2 different media formats, 1 offsite/cloud copy) to safeguard large media volumes."
            },
            {
                "question": "Explain your workflow for color grading raw log footage.",
                "answer": "Start by applying a normalization LUT or adjusting primary exposure and contrast. Follow up with primary color balancing (correcting casts, setting highlights/shadows). Finally, perform secondary grading (targeting skin tones) and apply creative styling/looks."
            }
        ]
    if any(k in r_lower for k in ["design", "ux", "ui", "product design", "graphic", "creative"]):
        return [
            {
                "question": "What is your user research methodology when starting a new product design?",
                "answer": "I conduct semi-structured user interviews, competitive analysis, and review analytics. I then synthesize findings into empathy maps and user personas to guide the wireframing phase."
            },
            {
                "question": "How do you handle negative feedback on your design prototypes during usability testing?",
                "answer": "I view negative feedback as an opportunity to iterate. I separate myself from the design, seek to understand the root cause of usability friction, and validate design alternatives through further tests."
            }
        ]
    return [
        {
            "question": f"What are the most important qualities of a successful {role_name}?",
            "answer": f"A successful {role_name} needs strong communication skills, attention to detail, adaptability, and deep expertise in core tools and industry workflows."
        },
        {
            "question": f"How do you prioritize tasks under tight deadlines in a {role_name} position?",
            "answer": "Assess business impact, organize tasks using Agile/Scrum templates, clarify scope with stakeholders early, and focus on delivering high-quality core outcomes first."
        }
    ]

def get_custom_roadmap(role_name: str) -> dict:
    r_lower = role_name.lower()
    if any(k in r_lower for k in ["video", "editor", "film", "animator", "motion", "creative", "media"]):
        return {
            "30_day": [
                "Master core keyboard shortcuts, timeline organization, and ingest workflows in Premiere Pro / DaVinci.",
                "Learn color correction theory: color wheels, scopes, curves, and LOG footage transformation."
            ],
            "60_day": [
                "Complete the Cinematic Short Film Color Grading project and upload the reel to YouTube/Vimeo.",
                "Practice motion tracking, masking, and dynamic text animations in After Effects."
            ],
            "90_day": [
                "Assemble your professional editing showreel (max 60 seconds) showcasing your best cuts and grading.",
                "Apply to local production houses, creative agencies, or remote freelance platforms."
            ]
        }
    if any(k in r_lower for k in ["design", "ux", "ui", "product design", "graphic", "creative"]):
        return {
            "30_day": [
                "Master Figma auto-layout, component states, variables, and design library patterns.",
                "Study layout hierarchy, typography scaling, Gestalt principles, and WCAG accessibility standards."
            ],
            "60_day": [
                "Build the Food Delivery UX mobile app case study project and run usability test loops.",
                "Create a responsive SaaS design system framework with interactive Figma prototypes."
            ],
            "90_day": [
                "Polish your portfolio case studies on Behance/Medium or your personal website.",
                "Prepare case study walkthrough decks for product design interviews."
            ]
        }
    if any(k in r_lower for k in ["marketing", "seo", "sem", "ads", "growth", "copywriter", "content"]):
        return {
            "30_day": [
                "Complete Google Ads Search and Google Analytics 4 (GA4) certification tracks.",
                "Master search engine optimization basics, keyword metrics (volume, KD), and search intent."
            ],
            "60_day": [
                "Build your e-commerce search strategy and SEO audit portfolio piece.",
                "Configure a mock growth conversion funnel and calculate customer metrics (CAC, LTV, ROAS)."
            ],
            "90_day": [
                "Compile your growth reports, create a clean slide deck, and optimize your LinkedIn profile.",
                "Apply to growth marketing, SEO specialist, or customer acquisition positions."
            ]
        }
    if any(k in r_lower for k in ["finance", "financial", "accounting", "valuation"]):
        return {
            "30_day": [
                "Master three-statement modeling theory and standard Excel forecasting workflows.",
                "Study corporate valuation methodologies: Discounted Cash Flow (DCF) and trading comparables."
            ],
            "60_day": [
                "Construct the fully integrated Three-Statement forecast and DCF model in Excel for a target public company.",
                "Develop the Portfolio Risk analysis dashboard script in Python using Pandas."
            ],
            "90_day": [
                "Polish your valuation spreadsheets, write a brief investment thesis memo, and publish code.",
                "Prepare for finance technical interviews (accounting linkages, valuation assumptions)."
            ]
        }
    return None

def generate_mock_data(target_role: str, cv_text: str = "") -> dict:
    """
    Generates realistic fallback data for testing/demo purposes if OpenAI calls fail.
    Dynamically scans the candidate's actual CV text for keywords (like PowerBI, SQL, Docker)
    to customize the strengths, gaps, and readiness score.
    """
    logger.info(f"Generating mock evaluation data for role: {target_role}...")
    
    cv_lower = cv_text.lower() if cv_text else ""
    
    # 1. Base blueprints for each role
    role_blueprints = {
        "Data Analyst": {
            "career_score": 65,
            "strengths": [
                "Good communication and presentation skills from previous roles",
                "Strong analytical mindset and logical thinking"
            ],
            "weaknesses": [
                "Lack of hands-on experience with enterprise BI tools like Tableau or PowerBI",
                "Limited experience in advanced statistical modeling or regression analysis",
                "Missing exposure to automated data pipeline schedulers (Airflow)"
            ],
            "skill_gaps": [
                "Tableau or PowerBI dashboard development",
                "Advanced SQL window functions, CTEs, and query optimization",
                "ETL/ELT pipeline design and warehousing concepts"
            ],
            "summary": "The candidate has solid analytical fundamentals. To transition to a mid-level Data Analyst role, they must master modern BI tools (like PowerBI or Tableau), advanced database querying concepts, and basic data extraction pipelines.",
            "certifications": [
                {"name": "Google Data Analytics Professional Certificate", "provider": "Coursera / Google", "reason": "Establishes structured understanding of data collection, cleaning, and SQL basics."},
                {"name": "Microsoft Certified: Power BI Data Analyst Associate (PL-300)", "provider": "Microsoft", "reason": "Validates enterprise-level dashboard design, data modeling, and reporting skills."},
                {"name": "Tableau Desktop Certified Associate", "provider": "Tableau", "reason": "Highly sought-after visualization credential that increases credibility for reporting-heavy positions."}
            ],
            "project_ideas": [
                {
                    "title": "E-Commerce Customer Cohort & Retention Analysis",
                    "description": "Analyze transactional data to calculate cohort retention rates, Customer Lifetime Value (CLV), and order trends. Build a clean dashboard.",
                    "difficulty": "Intermediate",
                    "technologies": ["Python", "Pandas", "SQL", "PowerBI"]
                },
                {
                    "title": "Automated Web Scraper & ETL Pipeline",
                    "description": "Create a python script to scrape market listings daily, clean the data using pandas, load it into database tables, and run automated analysis.",
                    "difficulty": "Intermediate",
                    "technologies": ["Python", "SQL", "BeautifulSoup", "Airflow"]
                }
            ],
            "roadmap_30_60_90": {
                "30_day": [
                    "Master advanced SQL concepts: CTEs, Window Functions, and Query Execution Plans.",
                    "Complete training on PowerBI/Tableau parameters, DAX, and calculated fields."
                ],
                "60_day": [
                    "Build the E-Commerce Cohort Analysis project and push clean code to GitHub.",
                    "Learn core data warehousing architectures (Star schema, dimensional modeling)."
                ],
                "90_day": [
                    "Prepare and take the PL-300 PowerBI certification.",
                    "Tailor resume bullet points to highlight metrics and business impact."
                ]
            },
            "interview_prep": [
                {
                    "question": "What is the difference between a CTE and a Subquery?",
                    "answer": "CTEs (Common Table Expressions) are defined using the WITH statement and improve query legibility and modularity, while subqueries are nested inside queries. CTEs can also be recursive and are often optimized better by database planners."
                },
                {
                    "question": "Explain what a Cohort Analysis is and why it's useful.",
                    "answer": "Cohort analysis tracks groups of users sharing a characteristic (like signup month) over time. It is vital for understanding user retention, customer lifetime value, and churn rates."
                }
            ]
        },
        "Data Scientist": {
            "career_score": 68,
            "strengths": [
                "Strong academic or practical baseline in quantitative reasoning",
                "Understanding of core machine learning concepts (Supervised/Unsupervised learning)"
            ],
            "weaknesses": [
                "No experience deploying models into scalable production settings",
                "Lacks experience with Big Data engines (Apache Spark) for processing large datasets",
                "Lacks model tracking and registry discipline (MLflow, Weights & Biases)"
            ],
            "skill_gaps": [
                "Production Model Deployment (FastAPI, Docker)",
                "Big Data frameworks (PySpark, Databricks)",
                "MLOps lifecycle tools (MLflow)",
                "Advanced model optimization and hyperparameter tuning"
            ],
            "summary": "The candidate shows high potential in quantitative analysis and core ML algorithms. To be industry-ready for a mid/senior Data Scientist role, they need to bridge the gap between static Jupyter Notebook models and production-grade MLOps and Big Data systems.",
            "certifications": [
                {"name": "Google Professional Data Engineer", "provider": "Google Cloud", "reason": "Validates data processing, BigQuery, Spark, and ML systems in GCP."},
                {"name": "Databricks Certified Associate Developer for Apache Spark", "provider": "Databricks", "reason": "Proves deep competency in handling large-scale data modeling and processing tasks."},
                {"name": "AWS Certified Machine Learning - Specialty", "provider": "Amazon Web Services", "reason": "Validates model training, tuning, and hosting infrastructure using Amazon SageMaker."}
            ],
            "project_ideas": [
                {
                    "title": "Predictive Customer Churn API with Model Registry",
                    "description": "Train a classification model using XGBoost. Log parameters, metrics, and models using MLflow. Wrap the final model in a FastAPI container.",
                    "difficulty": "Intermediate",
                    "technologies": ["Python", "Scikit-Learn", "FastAPI", "MLflow", "Docker"]
                },
                {
                    "title": "Large Scale PySpark Market Trend Analytics",
                    "description": "Ingest and analyze a multi-gigabyte dataset using PySpark. Perform distributed feature engineering and run simple ML clustering on Databricks.",
                    "difficulty": "Advanced",
                    "technologies": ["Python", "PySpark", "Databricks", "Parquet", "Tableau"]
                }
            ],
            "roadmap_30_60_90": {
                "30_day": [
                    "Study modern ML validation techniques and model tracking using MLflow.",
                    "Learn PySpark fundamentals and run simple operations on local cluster."
                ],
                "60_day": [
                    "Build the FastAPI model deployment container and deploy it to a free container host (Render or local Docker).",
                    "Execute a distributed analytics project on Databricks Community Edition."
                ],
                "90_day": [
                    "Add ML model testing (Pytest for inputs/ranges) to your projects.",
                    "Update resume to emphasize deployed models and pipeline savings."
                ]
            },
            "interview_prep": [
                {
                    "question": "What is the difference between bagging and boosting?",
                    "answer": "Bagging (e.g., Random Forest) builds decision trees in parallel, reducing variance by averaging outputs. Boosting (e.g., XGBoost) builds trees sequentially, where each new tree corrects the residual errors of the previous ones, reducing bias."
                },
                {
                    "question": "How do you address data leakage in a ML pipeline?",
                    "answer": "Data leakage occurs when target information from the future or test set leaks into training. To prevent it: 1) Split data into train/test before any preprocessing (scaling, imputation), 2) Use pipeline objects (like Scikit-Learn Pipeline) to encapsulate preprocessing and fit steps together."
                }
            ]
        },
        "AI Engineer": {
            "career_score": 62,
            "strengths": [
                "Strong programming background in Python",
                "Basic understanding of deep learning neural networks"
            ],
            "weaknesses": [
                "Lacks experience with Generative AI architectures, vector databases, and RAG",
                "No experience building agentic loops or multi-agent workflows",
                "Missing Docker containerization and software engineering engineering rigor"
            ],
            "skill_gaps": [
                "Retrieval-Augmented Generation (RAG) pipelines",
                "Vector Databases (ChromaDB, Pinecone, pgvector)",
                "LLM frameworks (LangChain, LlamaIndex, LangGraph)",
                "API wrapper creation and containerized deployments"
            ],
            "summary": "The candidate has a solid foundational software profile. Transitioning to AI Engineering requires mastery of Generative AI patterns, prompt engineering frameworks, vector search indexing, and deployment methodologies.",
            "certifications": [
                {"name": "Generative AI with Large Language Models", "provider": "DeepLearning.AI", "reason": "Covers prompt engineering, fine-tuning, RLHF, and agent setups."},
                {"name": "LangChain Certified AI Developer (Community)", "provider": "LangChain", "reason": "Validates active building of LLM chains, agents, and custom tools."},
                {"name": "AWS Certified Machine Learning - Specialty", "provider": "AWS", "reason": "Ensures knowledge of cloud-scale AI/ML hosting and operations."}
            ],
            "project_ideas": [
                {
                    "title": "Production-Ready PDF RAG Assistant",
                    "description": "Ingest multi-page PDFs, partition text, embed using OpenAI, store in ChromaDB, and handle contextual question-answering. Containerize the workspace.",
                    "difficulty": "Intermediate",
                    "technologies": ["Python", "LangChain", "ChromaDB", "FastAPI", "Docker"]
                },
                {
                    "title": "Multi-Agent Git Review Planner",
                    "description": "Build a LangGraph agent workflow that monitors a repo, reviews PR changes, refactors styling, and creates feedback markdown reports.",
                    "difficulty": "Advanced",
                    "technologies": ["Python", "LangGraph", "GitHub API", "OpenAI"]
                }
            ],
            "roadmap_30_60_90": {
                "30_day": [
                    "Complete a comprehensive course on Vector Databases, Chunking Strategies, and embeddings.",
                    "Build a simple CLI-based Chatbot using OpenAI API and LangChain."
                ],
                "60_day": [
                    "Develop the Production-Ready RAG Assistant with FastAPI endpoints and Docker file.",
                    "Learn agent mechanics: routing, tools execution, and state machines in LangGraph."
                ],
                "90_day": [
                    "Host the Multi-Agent review planner and add performance metrics.",
                    "Optimize resume to highlight AI agent system design and cost optimization techniques."
                ]
            },
            "interview_prep": [
                {
                    "question": "What is hybrid search in vector retrieval?",
                    "answer": "Hybrid search combines semantic vector search (retrieving by meaning) with keyword search (using BM25 for exact matches). The results are merged using algorithms like Reciprocal Rank Fusion (RRF), improving search accuracy for domain-specific queries."
                },
                {
                    "question": "How do you evaluate an LLM app's retrieval pipeline?",
                    "answer": "You can evaluate retrieval using metrics like Context Precision (was the context relevant?) and Context Recall (did we retrieve all relevant info?), using frameworks like Ragas or TruLens with ground-truth test datasets."
                }
            ]
        },
        "Software Engineer": {
            "career_score": 70,
            "strengths": [
                "Proficiency in basic syntax, data structures, and algorithms",
                "Understanding of database fundamentals and SQL writing"
            ],
            "weaknesses": [
                "Lacks experience with microservices architecture and scalability design",
                "Missing solid CI/CD automation pipeline experience",
                "No experience with system design components (load balancers, caching, message queues)"
            ],
            "skill_gaps": [
                "System Design at Scale (caching, database partitioning)",
                "Containerization & Orchestration (Docker, Kubernetes)",
                "CI/CD workflow tools (GitHub Actions, Jenkins)",
                "API design, authentication protocols (OAuth, JWT)"
            ],
            "summary": "The candidate has strong code writing basics. To reach mid-to-senior levels, they should focus on microservices architectures, cloud platforms, robust CI/CD, and system design patterns for high traffic.",
            "certifications": [
                {"name": "AWS Certified Developer - Associate", "provider": "Amazon Web Services", "reason": "Validates core cloud architecture, API Gateway, DynamoDB, and Serverless setups."},
                {"name": "Certified Kubernetes Administrator (CKA)", "provider": "CNCF / Linux Foundation", "reason": "Proves hands-on competence in managing, scaling, and deploying microservices."},
                {"name": "Oracle Certified Professional: Java / Python Equivalent", "provider": "Oracle", "reason": "Validates language-specific deep mechanics, design patterns, and concurrency."}
            ],
            "project_ideas": [
                {
                    "title": "Scalable URL Shortener API with Redis Caching",
                    "description": "Create a high-performance URL shortener. Implement Redis caching to prevent database reads, rate-limiting, and deploy inside a Docker network.",
                    "difficulty": "Intermediate",
                    "technologies": ["Python", "FastAPI", "Redis", "PostgreSQL", "Docker"]
                },
                {
                    "title": "Real-time Event Streaming Chat Service",
                    "description": "Develop a real-time messaging application utilizing WebSockets and Kafka/RabbitMQ to handle pub/sub message distribution across multiple service replicas.",
                    "difficulty": "Advanced",
                    "technologies": ["Go or Python", "WebSockets", "Kafka", "PostgreSQL", "Docker"]
                }
            ],
            "roadmap_30_60_90": {
                "30_day": [
                    "Study System Design fundamentals: CAP theorem, caching strategies, load balancers.",
                    "Master Docker, learning to write custom multi-stage Dockerfiles."
                ],
                "60_day": [
                    "Complete the Scalable URL Shortener project, adding comprehensive unit tests and CI/CD pipelines.",
                    "Implement OAuth2/JWT secure authentication layers in your endpoints."
                ],
                "90_day": [
                    "Prepare for System Design interviews by practicing design diagrams.",
                    "Host portfolio projects and link detailed design choices in your README files."
                ]
            },
            "interview_prep": [
                {
                    "question": "What is the CAP Theorem?",
                    "answer": "CAP theorem states that a distributed system can guarantee at most two out of three: Consistency (every read receives the most recent write), Availability (every request receives a non-error response), and Partition Tolerance (the system continues to operate despite network partition errors)."
                },
                {
                    "question": "What is the difference between SQL and NoSQL databases, and when do you choose?",
                    "answer": "SQL databases are relational, schema-based, and ACID-compliant. They are ideal for complex queries and transaction stability. NoSQL databases are non-relational, flexible-schema, and scale horizontally, making them perfect for unstructured data or high write volumes."
                }
            ]
        },
        "Cybersecurity Analyst": {
            "career_score": 60,
            "strengths": [
                "Understanding of networking protocols and operating system concepts",
                "Familiarity with scripting languages for simple automation"
            ],
            "weaknesses": [
                "Lacks practical experience with SIEM platforms (Splunk, Sentinel)",
                "No experience with cloud infrastructure security configuration (AWS, Azure)",
                "Missing hands-on malware analysis or threat hunting experience"
            ],
            "skill_gaps": [
                "SIEM administration and custom alert writing (Splunk)",
                "Incident Response and threat hunting workflows",
                "Cloud security posture management (CSPM)",
                "Penetration testing and vulnerability scanning (Nessus, Metasploit)"
            ],
            "summary": "The candidate has solid networking knowledge. To transition to a security operations center (SOC) or security engineering role, they must gain experience on SIEM threat monitoring, incident response frameworks, and cloud security controls.",
            "certifications": [
                {"name": "CompTIA Security+", "provider": "CompTIA", "reason": "Core baseline validating fundamental network security, threat management, and cryptography."},
                {"name": "Certified Ethical Hacker (CEH)", "provider": "EC-Council", "reason": "Proves understanding of offensive vectors, scanning, and hacking tools."},
                {"name": "CompTIA Cybersecurity Analyst (CySA+)", "provider": "CompTIA", "reason": "Intermediate cert validating threat detection, data analysis, and incident remediation."}
            ],
            "project_ideas": [
                {
                    "title": "SOC Log Monitoring Sandbox with ELK / Splunk",
                    "description": "Deploy a local Linux machine. Forward syslog data to an ELK stack. Write custom rules to detect failed SSH login attempts and brute force logs.",
                    "difficulty": "Intermediate",
                    "technologies": ["Linux", "Docker", "ELK Stack", "Bash Scripting"]
                },
                {
                    "title": "Automated Cloud Vulnerability Scanner",
                    "description": "Develop a script that scans AWS IAM policies for wildcard permissions and publicly readable S3 buckets, generating alerts on a Discord webhook.",
                    "difficulty": "Intermediate",
                    "technologies": ["Python", "Boto3 (AWS)", "GitHub Actions", "Webhooks"]
                }
            ],
            "roadmap_30_60_90": {
                "30_day": [
                    "Complete CompTIA Security+ study material covering standard risk vectors.",
                    "Set up a local virtualized sandbox network using VirtualBox/VMware."
                ],
                "60_day": [
                    "Implement the SOC Log Monitoring project, writing alerts for intrusion detection.",
                    "Learn cloud security fundamentals (IAM roles, Security Groups, audit logs)."
                ],
                "90_day": [
                    "Practice Wireshark packet capture analysis and malware remediation patterns.",
                    "Tailor resume to emphasize security controls and incident containment logs."
                ]
            },
            "interview_prep": [
                {
                    "question": "What is the difference between Symmetric and Asymmetric encryption?",
                    "answer": "Symmetric encryption uses the same key for both encryption and decryption (fast, good for data-at-rest). Asymmetric encryption uses a public key to encrypt and a private key to decrypt (slower, used for key exchange like TLS)."
                },
                {
                    "question": "Can you explain the stages of the Cyber Kill Chain?",
                    "answer": "Developed by Lockheed Martin, it defines the phases of a cyberattack: 1) Reconnaissance, 2) Weaponization, 3) Delivery, 4) Exploitation, 5) Installation, 6) Command and Control, and 7) Actions on Objectives. Security analysts use it to find interception points."
                }
            ]
        },
        "Product Manager": {
            "career_score": 66,
            "strengths": [
                "Excellent stakeholder management and cross-functional communication",
                "Ability to define feature roadmaps and customer requirements"
            ],
            "weaknesses": [
                "Lacks technical product management understanding (API patterns, databases)",
                "Limited experience in metric-driven validation and A/B test methodologies",
                "Missing hands-on experience with agile product tooling (Jira Advanced Roadmaps)"
            ],
            "skill_gaps": [
                "Technical system overview (APIs, system flows)",
                "Product Analytics platforms (Amplitude, Mixpanel)",
                "A/B testing design, statistical significance calculations",
                "Jira Epic structure and sprint capacity planning"
            ],
            "summary": "The candidate is a strong communicator. To succeed as a Technical Product Manager, they should focus on API architecture basics, data-driven product analytics, product testing (A/B), and scrum management templates.",
            "certifications": [
                {"name": "Certified Scrum Product Owner (CSPO)", "provider": "Scrum Alliance", "reason": "Focuses on scrum rules, product backlog management, and user stories."},
                {"name": "Professional Scrum Product Owner I (PSPO I)", "provider": "Scrum.org", "reason": "Rigorous industry assessment testing value optimization and backlog delivery."},
                {"name": "Product Management Certificate", "provider": "Product School", "reason": "Validates user research, prioritization frameworks, and UI/UX flows."}
            ],
            "project_ideas": [
                {
                    "title": "PRD & Interactive Figma Prototype for SaaS Feature",
                    "description": "Write a complete Product Requirement Document (PRD) detailing user personas, metrics, and API payloads. Build a clickable Figma mockup.",
                    "difficulty": "Intermediate",
                    "technologies": ["PRD Writing", "Figma", "Jira", "Amplitude (Mock data)"]
                },
                {
                    "title": "A/B Testing Impact Dashboard",
                    "description": "Analyze a mock user interaction dataset using Python to calculate click-through rates, p-values, and statistical significance of feature variants.",
                    "difficulty": "Intermediate",
                    "technologies": ["Python", "Pandas", "Scipy (Stats)", "Streamlit"]
                }
            ],
            "roadmap_30_60_90": {
                "30_day": [
                    "Study product analytics metrics (Retention, Conversion, Cohorts) and A/B testing stats.",
                    "Complete a course on REST APIs, system integrations, and JSON payload flows."
                ],
                "60_day": [
                    "Complete a comprehensive PRD and Figma prototype, linking them in your portfolio.",
                    "Practice writing structured User Stories, Epics, and Acceptance Criteria in Jira."
                ],
                "90_day": [
                    "Run mock feature prioritizing exercises using frameworks like RICE or WSJF.",
                    "Position resume around product metrics (e.g. increase activation rates by X%)."
                ]
            },
            "interview_prep": [
                {
                    "question": "How do you prioritize a product backlog?",
                    "answer": "Backlog prioritization uses frameworks like RICE (Reach, Impact, Confidence, Effort) or MoSCoW. These frameworks quantify business value relative to engineering effort to ensure the highest ROI features are delivered first."
                },
                {
                    "question": "What is the difference between an API Gateway and an API?",
                    "answer": "An API is a single endpoint/service contract enabling software communication. An API Gateway is a routing layer sitting in front of microservices that aggregates requests, handles auth, and manages rate-limiting."
                }
            ]
        }
    }
    
    # Let's add the custom blueprints to role_blueprints dictionary
    role_blueprints.update({
        "Cloud/Devops": {
            "career_score": 50,
            "strengths": [
                "Understanding of automation scripting and scripting languages",
                "Familiarity with container concepts or cloud platform basics"
            ],
            "weaknesses": [
                "Lack of hands-on experience with Terraform or Infrastructure as Code",
                "Missing advanced CI/CD setup with GitHub Actions or Jenkins",
                "Limited experience in configuring Kubernetes or container orchestration at scale"
            ],
            "skill_gaps": [
                "Terraform (Infrastructure as Code)",
                "CI/CD workflow tools (GitHub Actions / Jenkins)",
                "Kubernetes and container orchestration"
            ],
            "summary": "The candidate has base scripting/automation skills. To transition to a Cloud/DevOps role, they need to master Infrastructure as Code (Terraform), CI/CD pipelines, and container orchestration (Kubernetes).",
            "certifications": [
                {"name": "AWS Certified Solutions Architect - Associate", "provider": "Amazon Web Services", "reason": "Establishes core architectural knowledge of cloud deployments for this career path."},
                {"name": "HashiCorp Certified: Terraform Associate", "provider": "HashiCorp", "reason": "Validates enterprise-level Infrastructure as Code skills for this career path."},
                {"name": "Certified Kubernetes Administrator (CKA)", "provider": "CNCF", "reason": "Highly regarded credential proving hands-on Kubernetes administration."}
            ],
            "project_ideas": [
                {
                    "title": "Automated AWS Infrastructure deployment via Terraform",
                    "description": "Deploy a multi-tier web application stack on AWS (VPC, EC2, RDS) securely using modular Terraform scripts. Set up state locking.",
                    "difficulty": "Intermediate",
                    "technologies": ["Terraform", "AWS", "GitHub Actions"]
                },
                {
                    "title": "GitOps CI/CD Pipeline with Kubernetes",
                    "description": "Build an automated pipeline that builds a Docker image on PR merge, pushes to registry, and updates deployment in a local K8s cluster.",
                    "difficulty": "Advanced",
                    "technologies": ["Docker", "Kubernetes", "GitHub Actions", "ArgoCD"]
                }
            ],
            "roadmap_30_60_90": {
                "30_day": [
                    "Master Docker container building and multi-stage container optimization.",
                    "Learn core AWS services and network configurations (VPC, IAM, Security Groups)."
                ],
                "60_day": [
                    "Write modular Terraform templates and build the automated AWS deployment project.",
                    "Set up GitHub Actions to run tests, build images, and lint codebase."
                ],
                "90_day": [
                    "Deploy a local Kubernetes cluster (Minikube/Kind) and practice scheduling services and ingress.",
                    "Prepare for the AWS Solutions Architect or Terraform Associate exam."
                ]
            },
            "interview_prep": [
                {
                    "question": "What is Infrastructure as Code (IaC) and why is it important?",
                    "answer": "IaC manages infrastructure using configuration files rather than manual processes. This ensures consistency, enables version control, reduces human error, and permits rapid replicability."
                },
                {
                    "question": "Explain the difference between Docker and Kubernetes.",
                    "answer": "Docker is a containerization technology that packages applications into isolated containers. Kubernetes is an orchestration engine that manages, scales, and networks those containers across a cluster of servers."
                }
            ]
        },
        "UI/UX Design": {
            "career_score": 50,
            "strengths": [
                "Basic understanding of interface layouts and prototyping",
                "Creative visual perspective and user empathy"
            ],
            "weaknesses": [
                "Lacks detailed user research and usability testing experience",
                "Missing high-fidelity design projects using Figma component systems",
                "No experience working with design systems or style guide implementation"
            ],
            "skill_gaps": [
                "Figma component systems, auto-layout, and prototyping",
                "User research, persona creation, and empathy mapping",
                "Usability testing methodologies and design heuristics"
            ],
            "summary": "The candidate shows creative design potential. To become a professional UI/UX Designer, they need to master advanced Figma capabilities, learn user research methodologies, and build a portfolio of end-to-end design case studies.",
            "certifications": [
                {"name": "Google UX Design Professional Certificate", "provider": "Coursera / Google", "reason": "Provides a comprehensive foundation in UX research and Figma prototyping for this career path."},
                {"name": "Interaction Design Foundation (IxDF) Membership", "provider": "IxDF", "reason": "Access to top industry courses on user interface design, typography, and UX research."},
                {"name": "Nielsen Norman Group UX Certification", "provider": "NN/g", "reason": "Prestigious UX credential that signifies deep theoretical and practical expertise."}
            ],
            "project_ideas": [
                {
                    "title": "Mobile App Design Case Study: Food Delivery UX",
                    "description": "Run user research, build user personas, draw wireframes, and design a high-fidelity interactive prototype in Figma utilizing auto-layout and components.",
                    "difficulty": "Intermediate",
                    "technologies": ["Figma", "User Research", "Wireframing"]
                },
                {
                    "title": "SaaS Platform Design System",
                    "description": "Create a comprehensive, accessible (WCAG compliant) design system in Figma with buttons, typography scale, color palette, and input states.",
                    "difficulty": "Advanced",
                    "technologies": ["Figma", "Design Systems", "WCAG Accessibility"]
                }
            ],
            "roadmap_30_60_90": {
                "30_day": [
                    "Master Figma auto-layout, interactive components, and prototyping features.",
                    "Learn core UX design principles: Gestalt principles, heuristic evaluation, and WCAG accessibility standards."
                ],
                "60_day": [
                    "Complete user research and build the Mobile App Design Case Study project.",
                    "Learn to conduct usability tests and document feedback patterns."
                ],
                "90_day": [
                    "Construct the SaaS design system, write a detailed case study on Behance/Medium, and prepare your design portfolio.",
                    "Practice presenting design decisions and articulating UI choices."
                ]
            },
            "interview_prep": [
                {
                    "question": "What is the difference between UI and UX design?",
                    "answer": "UX (User Experience) is about the overall feel and usability of the product, focusing on user journeys, research, and functionality. UI (User Interface) is about the visual look and feel—focusing on colors, typography, buttons, spacing, and layout aesthetics."
                },
                {
                    "question": "What is Auto-Layout in Figma and why do designers use it?",
                    "answer": "Auto-Layout allows buttons, lists, and pages to automatically grow or shrink when text changes or items are added. It mimics CSS Flexbox, ensuring responsive layouts that easily translate to code."
                }
            ]
        },
        "Marketing/Sales": {
            "career_score": 50,
            "strengths": [
                "Strong communication, negotiation, and storytelling skills",
                "Driven and performance-focused mindset"
            ],
            "weaknesses": [
                "Lack of hands-on experience with paid advertising platforms (Google/Meta Ads)",
                "Limited experience in search engine optimization (SEO) tool suites",
                "Missing data-driven campaign tracking and attribution modeling"
            ],
            "skill_gaps": [
                "Meta & Google Ads Campaign Management",
                "SEO tools (Ahrefs, SEMrush, Google Search Console)",
                "Google Analytics 4 (GA4) and growth funnel analytics"
            ],
            "summary": "The candidate possesses excellent verbal and presentation fundamentals. Transitioning to professional marketing or sales roles requires learning digital channel advertising, SEO analytics, and tracking user acquisition funnel metrics.",
            "certifications": [
                {"name": "Google Ads Search Certification", "provider": "Google", "reason": "Validates expertise in planning, executing, and optimizing Google Search ad campaigns."},
                {"name": "Google Analytics 4 Certification", "provider": "Google", "reason": "Ensures capability in tracking customer journeys, events, and conversion funnels."},
                {"name": "HubSpot Inbound Marketing Certification", "provider": "HubSpot", "reason": "Establishes a solid understanding of content strategy, lead nurturing, and email marketing."}
            ],
            "project_ideas": [
                {
                    "title": "Comprehensive E-Commerce Growth Strategy & SEO Audit",
                    "description": "Perform keyword research and SEO site audit for a mock retail site. Create a content calendar and mock landing page optimization blueprint.",
                    "difficulty": "Intermediate",
                    "technologies": ["SEMrush/Ahrefs", "Google Analytics", "On-Page SEO"]
                },
                {
                    "title": "Mock paid advertising campaign & conversion funnel dashboard",
                    "description": "Design a complete paid ads strategy. Model conversion rates and calculate customer acquisition cost (CAC) and return on ad spend (ROAS).",
                    "difficulty": "Intermediate",
                    "technologies": ["Excel / Google Sheets", "Meta Ads Manager (Mock)", "GA4"]
                }
            ],
            "roadmap_30_60_90": {
                "30_day": [
                    "Complete Google Ads and Google Analytics 4 training courses.",
                    "Learn key growth metrics: CAC, LTV, ROAS, CTR, and conversion rates."
                ],
                "60_day": [
                    "Run an SEO audit project on a live website or mock business, detailing recommendations.",
                    "Set up mock Google Ads campaign configurations, writing high-performing ad copy."
                ],
                "90_day": [
                    "Build a growth dashboard summarizing metrics, present acquisition funnel ideas.",
                    "Optimize resume to highlight past outcomes, target key metrics, and apply for roles."
                ]
            },
            "interview_prep": [
                {
                    "question": "What is the difference between CAC and LTV, and why does it matter?",
                    "answer": "CAC is Customer Acquisition Cost. LTV is Customer Lifetime Value. A healthy business model requires LTV to be significantly higher than CAC (typically an LTV:CAC ratio of 3:1 or higher is targeted) to ensure profitability."
                },
                {
                    "question": "Explain the difference between SEO and SEM.",
                    "answer": "SEO (Search Engine Optimization) focuses on getting organic, unpaid traffic by ranking high on search engine results. SEM (Search Engine Marketing) focuses on buying ads on search engines to get paid traffic."
                }
            ]
        },
        "Finance": {
            "career_score": 50,
            "strengths": [
                "Excellent mathematical competency and quantitative mindset",
                "Strong structure and attention to detail in documentation"
            ],
            "weaknesses": [
                "Limited experience in advanced three-statement financial modeling",
                "Lack of hands-on database querying or financial reporting tools",
                "Missing industry standard financial credentials (CFA, etc.)"
            ],
            "skill_gaps": [
                "Three-Statement Financial Modeling in Excel",
                "Corporate Valuation methods (DCF, Comps)",
                "SQL for financial data extraction and reporting"
            ],
            "summary": "The candidate has high analytical potential. To succeed in corporate finance or financial analysis, they must learn multi-statement financial modeling, DCF valuations, and data querying techniques.",
            "certifications": [
                {"name": "Financial Modeling & Valuation Analyst (FMVA)", "provider": "CFI", "reason": "Comprehensive industry-recognized standard for hands-on corporate finance and modeling."},
                {"name": "Chartered Financial Analyst (CFA) Level 1", "provider": "CFA Institute", "reason": "Gold standard credential for asset management and deep investment analysis."},
                {"name": "Microsoft Office Specialist: Excel Expert", "provider": "Microsoft", "reason": "Validates elite competency in formulas, macros, and financial worksheets."}
            ],
            "project_ideas": [
                {
                    "title": "Three-Statement Valuation Model (DCF & Comps)",
                    "description": "Construct a fully integrated 3-statement forecasting model (Income, Balance, Cash Flow) for a public company and run a DCF valuation.",
                    "difficulty": "Intermediate",
                    "technologies": ["Excel", "Financial Modeling", "DCF Analysis"]
                },
                {
                    "title": "Portfolio Risk & Performance Dashboard",
                    "description": "Use Python and Pandas to fetch historical stock prices, calculate portfolio returns, volatility, Sharpe ratio, and visualize metrics.",
                    "difficulty": "Advanced",
                    "technologies": ["Python", "Pandas", "Matplotlib / Streamlit", "YFinance"]
                }
            ],
            "roadmap_30_60_90": {
                "30_day": [
                    "Master advanced Excel formulas: XLOOKUP, INDEX-MATCH, nested IFs, and dynamic arrays.",
                    "Learn accounting foundations and the links between the three financial statements."
                ],
                "60_day": [
                    "Build the integrated Three-Statement financial model in Excel for a target company.",
                    "Study valuation methodologies: DCF, trading comparables, and precedent transactions."
                ],
                "90_day": [
                    "Complete the Portfolio Risk Analyzer project in Python or compile financial analysis sheets.",
                    "Update resume to emphasize modeling projects and begin preparing for finance interviews."
                ]
            },
            "interview_prep": [
                {
                    "question": "How are the three financial statements linked?",
                    "answer": "Net Income from the Income Statement flows to Cash Flow from Operations (CF) and Retained Earnings on the Balance Sheet. Depreciation/amortization reduces net income but is added back on CF. Finally, the ending Cash balance on the Cash Flow Statement matches the Cash asset account on the Balance Sheet."
                },
                {
                    "question": "What is a Discounted Cash Flow (DCF) analysis?",
                    "answer": "A DCF estimates a company's current value by forecasting its future free cash flows, discounting them back to the present using the Weighted Average Cost of Capital (WACC), and adding a discounted terminal value."
                }
            ]
        },
        "Generic": {
            "career_score": 50,
            "strengths": [
                "Good baseline capabilities and versatile professional background",
                "Strong willingness to learn and adapt to new challenges"
            ],
            "weaknesses": [
                "Lacks role-specific deep domain expertise shown in candidate profile",
                "Missing hands-on experience with specialized tools for this position",
                "No visible certification or training in the target field"
            ],
            "skill_gaps": [
                "Targeted domain-specific tools and methodologies",
                "Industry standards and best practices for this role",
                "Hands-on project work in this domain"
            ],
            "summary": "The candidate shows strong foundational skills. To transition to this target role successfully, they must acquire specialized domain knowledge, learn target tools, and build representative portfolio projects.",
            "certifications": [
                {"name": "General Professional Certificate", "provider": "Industry Recognized Provider", "reason": "Establishes a solid foundational background for this career path."},
                {"name": "Domain Specialized Associate", "provider": "Standard Body", "reason": "Validates core tools and workflows expected of professionals in this area."}
            ],
            "project_ideas": [
                {
                    "title": "Comprehensive Domain Project",
                    "description": "Develop an end-to-end project applying core workflows and standards of the target role, detailing all design decisions in a repository.",
                    "difficulty": "Intermediate",
                    "technologies": ["Python", "SQL", "Git"]
                }
            ],
            "roadmap_30_60_90": {
                "30_day": [
                    "Research and master core theoretical concepts and standards of the target role.",
                    "Identify and learn the primary tools and software used in this field."
                ],
                "60_day": [
                    "Complete a capstone project illustrating hands-on execution of target workflows.",
                    "Document your learning path and showcase project code or documentation."
                ],
                "90_day": [
                    "Join professional groups, seek informational interviews, and tailor your portfolio.",
                    "Apply to entry-level or transitional positions in this area."
                ]
            },
            "interview_prep": [
                {
                    "question": "What motivated you to transition to this role?",
                    "answer": "Focus on how your transferable skills (problem solving, communication, quantitative analysis) apply to the target role, combined with your self-directed learning and projects."
                },
                {
                    "question": "How do you stay updated with industry developments in this field?",
                    "answer": "Mention specific blogs, podcasts, newsletters, or online communities you follow, and discuss your continuous learning habits through courses and hands-on projects."
                }
            ]
        }
    })

    # 2. Classify custom roles dynamically
    if target_role in role_blueprints:
        matched_role = target_role
    else:
        r_lower = target_role.lower()
        if any(k in r_lower for k in ["cloud", "devops", "sre", "site reliability", "infrastructure", "sysadmin", "network engineer", "platform engineer"]):
            matched_role = "Cloud/Devops"
        elif any(k in r_lower for k in ["design", "ux", "ui", "product design", "graphic", "creative"]):
            matched_role = "UI/UX Design"
        elif any(k in r_lower for k in ["marketing", "sales", "seo", "growth", "business development", "product marketing"]):
            matched_role = "Marketing/Sales"
        elif any(k in r_lower for k in ["finance", "financial", "accounting", "auditor", "investment"]):
            matched_role = "Finance"
        elif any(k in r_lower for k in ["data scientist", "data science", "machine learning", "ml engineer", "nlp"]):
            matched_role = "Data Scientist"
        elif any(k in r_lower for k in ["ai engineer", "generative ai", "prompt engineer", "llm"]):
            matched_role = "AI Engineer"
        elif any(k in r_lower for k in ["data analyst", "business analyst", "bi analyst", "reporting"]):
            matched_role = "Data Analyst"
        elif any(k in r_lower for k in ["software", "developer", "programmer", "backend", "frontend", "fullstack", "web developer"]):
            matched_role = "Software Engineer"
        elif any(k in r_lower for k in ["security", "cyber", "pentest", "soc analyst", "information security"]):
            matched_role = "Cybersecurity Analyst"
        elif any(k in r_lower for k in ["product manager", "product owner", "project manager", "scrum master"]):
            matched_role = "Product Manager"
        else:
            matched_role = "Generic"

    # Deep-copy standard/classified blueprint
    import copy
    data = copy.deepcopy(role_blueprints[matched_role])
    
    # If custom target role, customize blueprint texts dynamically
    if target_role not in ["Software Engineer", "AI Engineer", "Data Analyst", "Data Scientist", "Cybersecurity Analyst", "Product Manager"]:
        data["summary"] = data["summary"].replace("this target role", f"the {target_role} role").replace("this role", f"the {target_role} role")
        data["weaknesses"] = [w.replace("this position", f"the {target_role} position") for w in data["weaknesses"]]
        data["skill_gaps"] = [g.replace("this role", f"the {target_role} role") for g in data["skill_gaps"]]
        
        # Override project ideas dynamically
        data["project_ideas"] = get_custom_project_ideas(target_role)
        
        # Override certifications dynamically
        data["certifications"] = get_custom_certifications(target_role)
        
        # Override interview prep dynamically
        data["interview_prep"] = get_custom_interview_prep(target_role)
        
        # Override roadmap dynamically if customized one exists
        custom_rm = get_custom_roadmap(target_role)
        if custom_rm:
            data["roadmap_30_60_90"] = custom_rm
        else:
            for phase in ["30_day", "60_day", "90_day"]:
                data["roadmap_30_60_90"][phase] = [item.replace("target role", target_role) for item in data["roadmap_30_60_90"][phase]]

    # 3. DYNAMIC SCORING LOGIC
    # Let's count primary matching keywords for the target role
    primary_keywords_map = {
        "Data Analyst": ["data analyst", "powerbi", "power bi", "tableau", "excel", "dashboard", "reporting", "looker", "sql", "pandas", "kpi"],
        "Data Scientist": ["data scientist", "machine learning", "regression", "scikit-learn", "statistics", "pyspark", "spark", "xgboost", "random forest", "python", "sql", "modeling"],
        "AI Engineer": ["ai engineer", "generative ai", "llm", "large language model", "rag", "langchain", "llamaindex", "openai", "prompt engineering", "vector database", "chromadb", "pinecone", "huggingface", "pytorch", "tensorflow", "python"],
        "Software Engineer": ["software engineer", "fullstack", "backend", "frontend", "java", "c++", "c#", "go language", "javascript", "typescript", "react", "node.js", "django", "fastapi", "spring boot", "rest api", "microservices", "system design"],
        "Cybersecurity Analyst": ["cybersecurity", "cyber security", "security analyst", "soc", "siem", "splunk", "firewall", "penetration testing", "pentest", "vulnerability", "incident response", "wireshark", "cryptography", "encryption", "network security", "threat hunting"],
        "Product Manager": ["product manager", "product owner", "prd", "roadmap", "user stories", "agile", "scrum", "jira", "sprint", "stakeholder", "product backlog", "competitor analysis"],
        "Cloud/Devops": ["cloud", "devops", "aws", "azure", "gcp", "terraform", "ansible", "kubernetes", "docker", "ci/cd", "infrastructure", "jenkins", "sysadmin", "sre", "site reliability"],
        "UI/UX Design": ["ui", "ux", "figma", "wireframe", "prototype", "design", "user research", "adobe", "sketch", "user flow", "usability", "interaction design"],
        "Marketing/Sales": ["marketing", "seo", "sem", "adwords", "analytics", "campaign", "social media", "content", "crm", "sales", "growth", "funnel", "conversions"],
        "Finance": ["finance", "financial", "excel", "modeling", "valuation", "accounting", "portfolio", "risk", "cfa", "cpa", "forecast", "revenue"]
    }
    
    # Identify target primary keywords
    target_kws = []
    if matched_role in primary_keywords_map:
        target_kws = primary_keywords_map[matched_role]
    else:
        # Tokenize the custom target role
        target_kws = [w.strip() for w in target_role.lower().split() if len(w.strip()) > 2]
        
    num_primary_matches = sum(1 for kw in target_kws if kw in cv_lower)
    
    # Calculate base score
    if num_primary_matches == 0:
        base_score = 20
    elif num_primary_matches == 1:
        base_score = 35
    elif num_primary_matches == 2:
        base_score = 50
    else:
        base_score = 65
        
    # Calculate role-specific bumps
    score_bump = 0
    skills_discovered = []
    
    # Define and check standard skills
    has_bi = "powerbi" in cv_lower or "power bi" in cv_lower or "tableau" in cv_lower
    has_python = "python" in cv_lower
    has_sql = "sql" in cv_lower
    has_docker = "docker" in cv_lower or "kubernetes" in cv_lower or "container" in cv_lower
    has_spark = "spark" in cv_lower or "pyspark" in cv_lower or "hadoop" in cv_lower
    has_ml = "machine learning" in cv_lower or "pytorch" in cv_lower or "tensorflow" in cv_lower or "scikit" in cv_lower
    has_cloud = "aws" in cv_lower or "amazon web" in cv_lower or "azure" in cv_lower or "gcp" in cv_lower or "google cloud" in cv_lower
    
    # Only award bumps that are relevant to the matched role
    if matched_role == "Data Analyst":
        if has_bi:
            skills_discovered.append("PowerBI/Tableau")
            score_bump += 12
            data["skill_gaps"] = [g for g in data["skill_gaps"] if "powerbi" not in g.lower() and "tableau" not in g.lower() and "bi tool" not in g.lower()]
            data["weaknesses"] = [w for w in data["weaknesses"] if "powerbi" not in w.lower() and "tableau" not in w.lower() and "bi tool" not in w.lower()]
            data["strengths"].append("Demonstrated hands-on experience in enterprise BI dashboards (PowerBI/Tableau).")
        if has_sql:
            skills_discovered.append("SQL")
            score_bump += 10
            data["skill_gaps"] = [g for g in data["skill_gaps"] if "sql" not in g.lower() or "advanced" in g.lower()]
            data["strengths"].append("Practical familiarity with SQL relational database queries.")
        if has_python:
            skills_discovered.append("Python")
            score_bump += 5
            data["strengths"].append("Solid programming proficiency in Python.")
            
    elif matched_role == "Data Scientist":
        if has_ml:
            skills_discovered.append("Machine Learning")
            score_bump += 12
            data["strengths"].append("Core proficiency in Machine Learning models and framework libraries.")
        if has_python:
            skills_discovered.append("Python")
            score_bump += 8
            data["strengths"].append("Solid programming proficiency in Python.")
        if has_sql:
            skills_discovered.append("SQL")
            score_bump += 5
            data["strengths"].append("Practical familiarity with SQL relational database queries.")
        if has_spark:
            skills_discovered.append("Big Data (Spark)")
            score_bump += 6
            data["skill_gaps"] = [g for g in data["skill_gaps"] if "spark" not in g.lower() and "pyspark" not in g.lower()]
            data["weaknesses"] = [w for w in data["weaknesses"] if "spark" not in w.lower() and "big data" not in w.lower()]
            data["strengths"].append("Experience processing large-scale datasets using Apache Spark.")
        if has_cloud:
            skills_discovered.append("Cloud Platforms")
            score_bump += 4
            data["strengths"].append("Familiarity with cloud-based deployment architectures (AWS/Azure/GCP).")
            
    elif matched_role == "AI Engineer":
        if has_ml:
            skills_discovered.append("Machine Learning")
            score_bump += 12
            data["strengths"].append("Core proficiency in Machine Learning models and framework libraries.")
        if has_python:
            skills_discovered.append("Python")
            score_bump += 8
            data["strengths"].append("Solid programming proficiency in Python.")
        if has_cloud:
            skills_discovered.append("Cloud Platforms")
            score_bump += 5
            data["strengths"].append("Familiarity with cloud-based deployment architectures (AWS/Azure/GCP).")
        if has_docker:
            skills_discovered.append("Docker/Containerization")
            score_bump += 5
            data["skill_gaps"] = [g for g in data["skill_gaps"] if "docker" not in g.lower() and "kubernetes" not in g.lower() and "container" not in g.lower()]
            data["weaknesses"] = [w for w in data["weaknesses"] if "docker" not in w.lower() and "kubernetes" not in w.lower()]
            data["strengths"].append("Hands-on exposure to containerized architectures (Docker/Kubernetes).")
            
    elif matched_role == "Software Engineer":
        if has_python:
            skills_discovered.append("Python")
            score_bump += 8
            data["strengths"].append("Solid programming proficiency in Python.")
        if has_sql:
            skills_discovered.append("SQL")
            score_bump += 6
            data["strengths"].append("Practical familiarity with SQL relational database queries.")
        if has_docker:
            skills_discovered.append("Docker/Containerization")
            score_bump += 8
            data["skill_gaps"] = [g for g in data["skill_gaps"] if "docker" not in g.lower() and "kubernetes" not in g.lower() and "container" not in g.lower()]
            data["weaknesses"] = [w for w in data["weaknesses"] if "docker" not in w.lower() and "kubernetes" not in w.lower()]
            data["strengths"].append("Hands-on exposure to containerized architectures (Docker/Kubernetes).")
        if has_cloud:
            skills_discovered.append("Cloud Platforms")
            score_bump += 6
            data["strengths"].append("Familiarity with cloud-based deployment architectures (AWS/Azure/GCP).")
            
    elif matched_role == "Cybersecurity Analyst":
        if num_primary_matches > 0:
            skills_discovered.append("Cybersecurity Fundamentals")
            score_bump += num_primary_matches * 6
        if has_python:
            skills_discovered.append("Scripting (Python)")
            score_bump += 5
            data["strengths"].append("Ability to automate tasks using Python scripting.")
        if has_cloud:
            skills_discovered.append("Cloud Security")
            score_bump += 5
            data["strengths"].append("Familiarity with cloud infrastructures and environment settings.")
            
    elif matched_role == "Product Manager":
        if num_primary_matches > 0:
            skills_discovered.append("Product Management")
            score_bump += num_primary_matches * 6
        if has_sql:
            skills_discovered.append("SQL Analytics")
            score_bump += 5
            data["strengths"].append("Data querying proficiency via SQL for product analytics.")
            
    elif matched_role == "Cloud/Devops":
        if has_cloud:
            skills_discovered.append("Cloud Platforms")
            score_bump += 12
            data["strengths"].append("Familiarity with cloud-based deployment architectures (AWS/Azure/GCP).")
        if has_docker:
            skills_discovered.append("Docker/Containerization")
            score_bump += 12
            data["skill_gaps"] = [g for g in data["skill_gaps"] if "docker" not in g.lower() and "kubernetes" not in g.lower() and "container" not in g.lower()]
            data["weaknesses"] = [w for w in data["weaknesses"] if "docker" not in w.lower() and "kubernetes" not in w.lower()]
            data["strengths"].append("Hands-on exposure to containerized architectures (Docker/Kubernetes).")
        if has_python:
            skills_discovered.append("Python Scripting")
            score_bump += 5
            data["strengths"].append("Solid programming proficiency in Python.")
            
    elif matched_role == "UI/UX Design":
        if num_primary_matches > 0:
            skills_discovered.append("UI/UX Design")
            score_bump += num_primary_matches * 8
            
    elif matched_role == "Marketing/Sales":
        if num_primary_matches > 0:
            skills_discovered.append("Growth/Marketing")
            score_bump += num_primary_matches * 8
        if has_sql:
            skills_discovered.append("SQL")
            score_bump += 3
            
    elif matched_role == "Finance":
        if num_primary_matches > 0:
            skills_discovered.append("Financial Analysis")
            score_bump += num_primary_matches * 8
        if has_sql:
            skills_discovered.append("SQL")
            score_bump += 5
            
    else:  # Generic
        if num_primary_matches > 0:
            skills_discovered.append(f"{target_role} Concepts")
            score_bump += num_primary_matches * 8
        if has_python:
            skills_discovered.append("Python")
            score_bump += 3
        if has_sql:
            skills_discovered.append("SQL")
            score_bump += 3

    # Calculate final score
    data["career_score"] = min(base_score + score_bump, 98)
    
    # Customize summary to mention recognized skills
    if skills_discovered:
        data["summary"] = f"Candidate shows strong indicators of {', '.join(skills_discovered)} skills on their CV. " + data["summary"]
        
    return data

def evaluate_resume_with_ai(cv_text: str, target_role: str, custom_api_key: str = None) -> dict:
    """
    Sends the resume and target role to Gemini (or OpenAI if selected) using the appropriate model.
    Enforces a strict JSON output format.
    Falls back to mock data if there are errors.
    """
    api_key = custom_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        logger.warning("No API key found. Using mock data fallback.")
        return generate_mock_data(target_role, cv_text)
    
    try:
        # Initialize HTTP client ignoring SSL validation to bypass Windows cert errors
        http_client = httpx.Client(verify=False)
        
        is_openai = api_key.startswith("sk-")
        if is_openai:
            client = OpenAI(api_key=api_key, http_client=http_client)
            model_name = "gpt-4o-mini"
            logger.info(f"Invoking OpenAI API for role: {target_role}...")
        else:
            client = OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                http_client=http_client
            )
            model_name = "gemini-2.5-flash"
            logger.info(f"Invoking Gemini API (primary: gemini-2.5-flash) for role: {target_role}...")
        
        user_content = USER_PROMPT_TEMPLATE.format(target_role=target_role, cv_text=cv_text)
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3, 
                timeout=45.0
            )
        except Exception as api_err:
            if not is_openai and model_name == "gemini-2.5-flash":
                logger.warning(f"Primary model {model_name} failed: {api_err}. Retrying with fallback: gemini-3.1-flash-lite...")
                model_name = "gemini-3.1-flash-lite"
                response = client.chat.completions.create(
                    model=model_name,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.3,
                    timeout=45.0
                )
            else:
                raise api_err
        
        raw_output = response.choices[0].message.content.strip()
        logger.info(f"Successfully received response from API using model: {model_name}")
        
        # Parse output as JSON
        analysis = json.loads(raw_output)
        return analysis
        
    except json.JSONDecodeError as je:
        logger.error(f"Failed to parse API response as JSON: {str(je)}")
        return generate_mock_data(target_role, cv_text)
    except Exception as e:
        logger.error(f"Error during API call: {str(e)}")
        return generate_mock_data(target_role, cv_text)

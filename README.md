# Match2 – AI Recruitment Agent

Match2 is an AI-powered recruitment matching system that analyzes job requirements and candidate profiles, maps both sides to a controlled professional discipline repository, evaluates compatibility, explains every recommendation, and calculates the geographic distance between the candidate and the job.

> **Privacy note:** This public repository contains fictional demonstration data only. No real candidate records, CVs, contact details, profile links, client information, or API keys are included.

## The problem

Recruiters often need to review a large number of candidate profiles for every open position. Traditional keyword matching is not sufficient because a profile may contain similar words while still being unsuitable because of:

- a different profession or role type;
- missing mandatory qualifications;
- incorrect seniority;
- industry mismatch;
- overqualification or underqualification;
- excessive geographic distance.

For example, a CFO may contain many accounting keywords but still be unsuitable for a Bookkeeper position. Match2 was created to identify candidates who realistically satisfy the complete requirements of a job, rather than candidates who merely share keywords.

## What Match2 does

1. Reads raw job records.
2. Sends new jobs to the OpenAI API for discipline classification.
3. Validates and saves approved job disciplines in a controlled repository.
4. Reads candidate records.
5. Maps candidates to disciplines already available in the repository.
6. Filters candidates by profession, discipline, seniority, industry, role type, and mandatory requirements.
7. Sends compatible job-candidate pairs to the OpenAI API.
8. Receives a score, decision, reasons, and missing skills.
9. Calculates geographic distance from latitude and longitude.
10. Produces ranked and explainable Excel reports.

## Workflow

```text
Raw Jobs Database
        |
        v
OpenAI API: Job Classification
        |
        v
Create and Validate Job Disciplines
        |
        v
Controlled Discipline Repository
        |
        v
Raw Candidates Database
        |
        v
Map Candidates to Existing Disciplines
        |
        v
Profession and Discipline Compatibility Filter
        |
        v
OpenAI API: Match Scoring
        |
        v
Score + Decision + Reasons + Missing Skills
        |
        v
Coordinate-Based Distance Calculation
        |
        v
Ranked Match Report by Job
```

## Prompt-controlled architecture

The workflow is controlled by structured prompts and deterministic validation rules.

### Discipline classification prompt

The classification prompt instructs the model to:

- identify the primary profession and relevant disciplines;
- use concise English discipline names;
- focus on the role rather than the employer or department;
- return valid structured JSON;
- avoid unsupported taxonomy values.

The Python application validates the returned disciplines against the enabled discipline repository. Unknown terms are removed or written to a warning report for review.

### Candidate matching prompt

The matching prompt evaluates the complete job requirements and instructs the model to return:

```json
{
  "candidate_index": 1,
  "score": 92,
  "decision": "YES",
  "reasons": "Strong FP&A, SQL and Power BI alignment with suitable seniority.",
  "missing_skills": ""
}
```

The prompt applies strict rules:

- same profession;
- correct seniority and realistic career level;
- correct role type;
- mandatory skills must be present;
- industry background must be relevant where required;
- overqualified and underqualified profiles are rejected;
- missing core requirements produce a `NO` decision.

Temperature is set to zero to improve repeatability.

## Controlled discipline repository

Jobs and candidates use the same approved taxonomy. This creates a common vocabulary for comparison and improves:

- consistency;
- multilingual matching;
- duplicate prevention;
- profession-level accuracy;
- explainability;
- future reuse of classifications.

The repository can include Hebrew and English skill aliases mapped to a canonical English discipline.

## Geographic distance

Match2 loads a city table containing latitude and longitude. It:

1. extracts the city from the job location;
2. extracts the city from the candidate location;
3. looks up both coordinate pairs;
4. calculates aerial distance with the Haversine formula;
5. multiplies the result by `1.35` as an estimated road-distance factor;
6. returns the rounded distance in kilometers.

Fallback values are used when a specific city is unavailable, rather than inventing a distance.

## Final output

The Excel output can contain:

- job and candidate links;
- job and candidate disciplines;
- candidate name and location;
- score;
- model decision;
- reasons;
- missing skills;
- distance in kilometers;
- English and Hebrew outreach messages;
- diagnostic and duplicate-control information.

## How GPT-5.6 was used

GPT-5.6 was the primary development assistant throughout the programming process. It supported:

- system architecture and workflow design;
- writing and improving the Python application;
- debugging and refactoring;
- validation and exception handling;
- prompt design and review;
- discipline mapping and taxonomy rules;
- mandatory-skill, seniority, profession, and industry checks;
- duplicate-control logic;
- JSON parsing and API error handling;
- geographic-distance calculations;
- Excel output and diagnostics;
- preparation of fictional demo data, documentation, and the demo video.

## How Codex was used

Codex was used together with GPT-5.6 to work with the codebase. It assisted with:

- inspecting and understanding existing Python functions;
- implementing and revising code;
- identifying bugs and edge cases;
- reviewing API calls and structured prompts;
- improving file-processing logic;
- improving maintainability and error handling;
- organizing the repository and technical documentation.

## Runtime model usage and cost control

The application was programmed with GPT-5.6 and Codex. To reduce recurring API costs, a lower-cost GPT-3.5 model was used for two limited runtime operations in the production workflow:

- translating a job-title role term into English;
- scoring candidate-to-job compatibility and returning the explanation.

The business logic, application architecture, validation rules, discipline repository, distance calculation, and report generation remain in the Python application developed with GPT-5.6 and Codex.

## Technology

- Python
- OpenAI API
- GPT-5.6 and Codex for development
- GPT-3.5 for selected cost-controlled runtime calls
- pandas
- openpyxl
- Excel
- JSON
- regular expressions
- Haversine geographic calculation

## Repository contents

```text
Match2-AI-Recruitment-Agent/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   └── match2_jobs_to_candidates_V2.py
├── demo_candidates.xlsx
├── demo_disciplines.xlsx
├── demo_jobs.xlsx
├── demo_locations.xlsx
├── demo_matches_output.xlsx
└── assets/
    ├── pipeline_diagram.png
    └── Match2_Project_Thumbnail_3x2.png
```

## Demo files

The fictional demo package contains:

- an English job database;
- an English candidate database;
- a controlled discipline repository;
- a table of cities and coordinates;
- an example ranked match report.

The demo email addresses use the reserved `example.com` domain.

## Installation

```bash
git clone https://github.com/goldov2/Match2-AI-Recruitment-Agent.git
cd Match2-AI-Recruitment-Agent
pip install -r requirements.txt
```

Set the OpenAI API key as an environment variable.

### Windows PowerShell

```powershell
$env:OPENAI_API_KEY="your-api-key"
```

### Linux or macOS

```bash
export OPENAI_API_KEY="your-api-key"
```

Run the application after adapting the input paths and schema to the local environment:

```bash
python -X utf8 src/match2_jobs_to_candidates_V2.py
```

## Security and privacy

Never commit:

- OpenAI API keys;
- real CVs or candidate databases;
- personal email addresses or phone numbers;
- LinkedIn profile links;
- private job or client records;
- passwords;
- local configuration files containing secrets.

The API key is read from `OPENAI_API_KEY`.

## Current limitations

The production script depends on locally configured input files, column mappings, taxonomy files, and thresholds. The public demo files illustrate the process but do not contain the full private production dataset or client-specific configuration.

## Future development

- web-based interface;
- direct job-description and CV upload;
- recruiter dashboard;
- improved multilingual taxonomy mapping;
- recruiter feedback loop;
- automatic CV-version recommendation;
- configurable matching thresholds;
- travel-time calculation;
- ATS integration;
- cloud deployment.

## Human oversight

Match2 is a decision-support system. AI recommendations must be reviewed by a human recruiter, who remains responsible for the final candidate decision.

## Author

**Dov Goldenberg** — financial analyst and automation developer specializing in Excel, Python, data analysis, financial systems, and business-process automation.

## License

This repository is provided for OpenAI Build Week demonstration and evaluation purposes.
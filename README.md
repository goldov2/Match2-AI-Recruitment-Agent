# Match2 – AI Recruitment Agent

Match2 is an AI-powered recruitment matching system that analyzes job requirements and candidate profiles, maps both sides to a controlled professional discipline repository, evaluates compatibility, explains every recommendation, and calculates the geographic distance between the candidate and the job.

The project was developed in Python with the assistance of GPT-5.6 and Codex.

---

## The Problem

Recruiters often need to review a large number of candidate profiles for every open position.

Traditional keyword matching is not sufficient because candidates may share similar words with a job description while still being unsuitable due to:

- A different profession
- Missing mandatory qualifications
- Incorrect seniority
- Industry mismatch
- Overqualification
- Underqualification
- Incompatible role type
- Excessive geographic distance

For example, a senior CFO may contain many accounting keywords but still be unsuitable for a Bookkeeper position.

Match2 was created to identify candidates who realistically satisfy the complete requirements of a job, rather than candidates who merely share similar keywords.

---

## Solution

Match2 combines AI-based text analysis with deterministic business rules.

The system:

1. Reads raw job records.
2. Sends each job to the OpenAI API.
3. Identifies professional disciplines for every job.
4. Saves approved disciplines in a controlled discipline repository.
5. Reads candidate records.
6. Maps every candidate to disciplines that already exist in the repository.
7. Filters candidates by profession, discipline, seniority, industry, and mandatory requirements.
8. Sends compatible job-candidate pairs to the OpenAI API.
9. Receives a compatibility score, decision, reasons, and missing skills.
10. Calculates the geographic distance between the job and candidate.
11. Produces a ranked and explainable Excel report.

---

## Main Workflow

```text
Raw Jobs Database
        |
        v
OpenAI API
        |
        v
Create Job Disciplines
        |
        v
Discipline Repository
        |
        v
Raw Candidates Database
        |
        v
Map Candidates to Existing Disciplines
        |
        v
Discipline Compatibility Filtering
        |
        v
OpenAI Match Scoring
        |
        v
Score + Decision + Reasons + Missing Skills
        |
        v
Geographic Distance Calculation
        |
        v
Ranked Match Report

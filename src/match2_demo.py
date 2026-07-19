# -*- coding: utf-8 -*-
"""Privacy-safe Match2 demonstration.

This script uses only the fictional Excel files included in this repository.
It demonstrates the core pipeline shown in the hackathon video:

1. Read jobs and candidates.
2. Classify jobs and candidates into a controlled discipline repository.
3. Score compatible job-candidate pairs with structured OpenAI prompts.
4. Calculate geographic distance from latitude/longitude coordinates.
5. Produce a ranked Excel match report.

Set OPENAI_API_KEY before running. Optional environment variables:
OPENAI_DISCIPLINE_MODEL and OPENAI_MATCH_MODEL.
"""

from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Any

import pandas as pd
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parents[1]
JOBS_FILE = BASE_DIR / "demo_jobs.xlsx"
CANDIDATES_FILE = BASE_DIR / "demo_candidates.xlsx"
DISCIPLINES_FILE = BASE_DIR / "demo_disciplines.xlsx"
LOCATIONS_FILE = BASE_DIR / "demo_locations.xlsx"
OUTPUT_FILE = BASE_DIR / "demo_matches_generated.xlsx"

DISCIPLINE_MODEL = os.getenv("OPENAI_DISCIPLINE_MODEL", "gpt-4o-mini")
MATCH_MODEL = os.getenv("OPENAI_MATCH_MODEL", "gpt-4o-mini")


def require_columns(df: pd.DataFrame, required: list[str], source: str) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def parse_json_object(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text or "", flags=re.DOTALL)
    if not match:
        raise ValueError("The model did not return a JSON object.")
    return json.loads(match.group(0))


def build_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY before running the demo.")
    return OpenAI(api_key=api_key)


def load_demo_data() -> tuple[pd.DataFrame, pd.DataFrame, list[str], dict[str, tuple[float, float]]]:
    jobs = pd.read_excel(JOBS_FILE, engine="openpyxl").fillna("")
    candidates = pd.read_excel(CANDIDATES_FILE, engine="openpyxl").fillna("")
    disciplines_df = pd.read_excel(DISCIPLINES_FILE, engine="openpyxl").fillna("")
    locations_df = pd.read_excel(LOCATIONS_FILE, engine="openpyxl").fillna("")

    require_columns(
        jobs,
        ["Job_ID", "Job_Title", "Job_Description", "Location", "Mandatory_Skills", "Seniority", "Industry"],
        JOBS_FILE.name,
    )
    require_columns(
        candidates,
        ["Candidate_ID", "Candidate_Name", "Location", "Professional_Summary", "Skills", "Seniority", "Industry_Background"],
        CANDIDATES_FILE.name,
    )
    require_columns(disciplines_df, ["Discipline", "Status"], DISCIPLINES_FILE.name)
    require_columns(locations_df, ["Location", "Latitude", "Longitude"], LOCATIONS_FILE.name)

    allowed_disciplines = [
        str(row["Discipline"]).strip()
        for _, row in disciplines_df.iterrows()
        if str(row["Status"]).strip().lower() == "enabled" and str(row["Discipline"]).strip()
    ]
    coordinates = {
        str(row["Location"]).strip().lower(): (float(row["Latitude"]), float(row["Longitude"]))
        for _, row in locations_df.iterrows()
        if str(row["Location"]).strip()
    }
    return jobs, candidates, allowed_disciplines, coordinates


def classify_text(client: OpenAI, record_type: str, text: str, allowed: list[str]) -> list[str]:
    prompt = f"""
You classify {record_type} records for an explainable recruitment system.
Choose only from this controlled discipline repository:
{json.dumps(allowed, ensure_ascii=False)}

Return ONLY valid JSON in this format:
{{"disciplines": ["Discipline 1", "Discipline 2"]}}

Rules:
- Select only disciplines directly supported by the text.
- Do not invent new values.
- Prefer the profession and strongest technical or functional specializations.
- Return at least one discipline when the text contains a clear profession.

TEXT:
{text[:5000]}
"""
    response = client.chat.completions.create(
        model=DISCIPLINE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    data = parse_json_object(response.choices[0].message.content or "")
    allowed_lookup = {item.lower(): item for item in allowed}
    result: list[str] = []
    for item in data.get("disciplines", []):
        canonical = allowed_lookup.get(str(item).strip().lower())
        if canonical and canonical not in result:
            result.append(canonical)
    return result


def disciplines_overlap(job_disciplines: list[str], candidate_disciplines: list[str]) -> bool:
    return bool({value.lower() for value in job_disciplines} & {value.lower() for value in candidate_disciplines})


def score_pair(client: OpenAI, job: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    prompt = f"""
You are a strict recruitment evaluator.
Compare one fictional demo candidate with one fictional demo job.

Return ONLY valid JSON:
{{
  "score": 0,
  "decision": "YES or NO",
  "reasons": ["short reason"],
  "missing_skills": ["missing mandatory requirement"]
}}

Mandatory rules:
- The candidate must match the profession and role type.
- Mandatory skills and qualifications have priority over keyword similarity.
- Reject clearly underqualified or overqualified candidates.
- Consider seniority, relevant industry, and evidence in the profile.
- Score from 0 to 100.
- Use YES only when the candidate is realistically suitable.

JOB:
{json.dumps(job, ensure_ascii=False, default=str)}

CANDIDATE:
{json.dumps(candidate, ensure_ascii=False, default=str)}
"""
    response = client.chat.completions.create(
        model=MATCH_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    data = parse_json_object(response.choices[0].message.content or "")
    score = max(0, min(100, int(data.get("score", 0))))
    decision = "YES" if str(data.get("decision", "NO")).strip().upper() == "YES" else "NO"
    reasons = data.get("reasons", [])
    missing = data.get("missing_skills", [])
    return {
        "score": score,
        "decision": decision,
        "reasons": reasons if isinstance(reasons, list) else [str(reasons)],
        "missing_skills": missing if isinstance(missing, list) else [str(missing)],
    }


def haversine_km(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
    lat1, lon1 = point_a
    lat2, lon2 = point_b
    radius = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return radius * 2 * math.asin(math.sqrt(a))


def estimated_road_distance_km(
    job_location: str,
    candidate_location: str,
    coordinates: dict[str, tuple[float, float]],
) -> int | None:
    job_point = coordinates.get(job_location.strip().lower())
    candidate_point = coordinates.get(candidate_location.strip().lower())
    if not job_point or not candidate_point:
        return None
    return round(haversine_km(job_point, candidate_point) * 1.35)


def main() -> None:
    client = build_client()
    jobs, candidates, allowed_disciplines, coordinates = load_demo_data()

    job_disciplines: dict[str, list[str]] = {}
    for _, row in jobs.iterrows():
        job_text = " | ".join(
            str(row[column])
            for column in ["Job_Title", "Job_Description", "Mandatory_Skills", "Seniority", "Industry"]
        )
        job_disciplines[str(row["Job_ID"])] = classify_text(client, "job", job_text, allowed_disciplines)

    candidate_disciplines: dict[str, list[str]] = {}
    for _, row in candidates.iterrows():
        candidate_text = " | ".join(
            str(row[column])
            for column in ["Professional_Summary", "Skills", "Seniority", "Industry_Background"]
        )
        candidate_disciplines[str(row["Candidate_ID"])] = classify_text(
            client, "candidate", candidate_text, allowed_disciplines
        )

    output_rows: list[dict[str, Any]] = []
    for _, job_row in jobs.iterrows():
        job = job_row.to_dict()
        job_id = str(job["Job_ID"])
        for _, candidate_row in candidates.iterrows():
            candidate = candidate_row.to_dict()
            candidate_id = str(candidate["Candidate_ID"])
            if not disciplines_overlap(job_disciplines[job_id], candidate_disciplines[candidate_id]):
                continue

            evaluation = score_pair(client, job, candidate)
            distance = estimated_road_distance_km(
                str(job["Location"]), str(candidate["Location"]), coordinates
            )
            output_rows.append(
                {
                    "Job_ID": job_id,
                    "Job_Title": job["Job_Title"],
                    "Job_Disciplines": " | ".join(job_disciplines[job_id]),
                    "Candidate_ID": candidate_id,
                    "Candidate_Name": candidate["Candidate_Name"],
                    "Candidate_Disciplines": " | ".join(candidate_disciplines[candidate_id]),
                    "Score": evaluation["score"],
                    "Decision": evaluation["decision"],
                    "Distance_km": distance if distance is not None else "Unknown",
                    "Reasons": " | ".join(evaluation["reasons"]),
                    "Missing_Skills": " | ".join(evaluation["missing_skills"]),
                }
            )

    output = pd.DataFrame(output_rows)
    if not output.empty:
        output = output.sort_values(["Job_ID", "Score", "Distance_km"], ascending=[True, False, True])
    output.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
    print(f"Created {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

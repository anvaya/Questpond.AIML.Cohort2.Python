from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateutil.parser as dparser

from typing import List
from Candidate.schemas.RawExperience import  ExtractedSkill

from Shared.normalizer import ROLE_TITLE_SKILL_MAP, normalize_and_match_skill, split_composite_skill
from Shared.Schema.Dto import SkillMetrics


def calculate_duration(start_raw, end_raw, ref_date="2026-01-01"):
    """
    Manual calculation of experience from the resume. LLM calculations are error-prone.
    
    :param start_raw: Start date extracted from resume.
    :param end_raw: End date extracted from resume (or 'Present' for ongoing role.)
    :param ref_date: Current Date to interpret "Present"
    """
    s_raw = start_raw
    e_raw = end_raw or "Present"
    today = datetime.strptime(ref_date, "%Y-%m-%d")

    try:
        start_dt = dparser.parse(s_raw)
        end_dt = today if "present" in e_raw.lower() or e_raw == "N/A" else dparser.parse(e_raw)
        delta = relativedelta(end_dt, start_dt)
        duration = (delta.years * 12) + delta.months
    except:
        duration = 0

    return duration

def get_job_skill_mentions(job):
    """
    Returns validated skill mentions for a job.    
    Implicit skills are excluded here.
    Used by the matching engine to extract hard skill requirements.
    """
    mentions = []

    for s in job.get("extracted_skills", []):
        if s["source"] == "implicit":
            #print("Excluded Implicit Skill ", s["raw_name"])
            continue  # hard exclusion        

        skills = split_composite_skill(s['raw_name'])
        for skl in skills:
            mentions.append({
                "raw_name": skl.strip(),
                "source": s["source"],
                "confidence": s.get("confidence", 1.0),
                "context": job.get("responsibilities", "")
            })

    return mentions

def infer_level_from_title(title: str) -> str:
    t = title.lower()

    if any(x in t for x in ["intern", "trainee"]):
        return "junior"
    if any(x in t for x in ["junior", "associate"]):
        return "junior"
    if any(x in t for x in ["senior", "lead", "principal"]):
        return "senior"
    return "mid"


def process_extracted_skills(skill_mentions, master_skills, vector_index, embed_fn, skill_map: defaultdict[str,SkillMetrics], 
                                level, months: int, start: datetime, end: datetime, role_title=None):
    
    """
    (SkillID, SkillCode, SkillType, confidence, method)
        OR (None, None, None, 0.0, "no_match")
    """   

    """
    It's important to understand how strongly the skill is reflected in the resume
    so that we rank candidates with strong demonstrated experience/skills higher.
    weights and strength give us the ability to tweak the rankings accordingly.
    """
    SOURCE_EVIDENCE_WEIGHT = {
        "skills_section": 1.0,
        "technology_list": 0.9,
        "responsibility": 0.7,
        "implicit": 0.0
    }    

    EVIDENCE_STRENGTH = {
        "responsibility": 3,
        "role_title": 2,
        "skills_section": 1
    }

    """
    I found that some of the skills (especially broad categorization like .Net developer) 
    are mentioned in the job-title and not explicitily in the experience detail. We, therefore,
    try and extract skills from role title in a resume experience section as well,
    and we let the further processing logic know, that we extracted it from role-title.
    """

    if role_title:
        for key, skill_codes in ROLE_TITLE_SKILL_MAP.items():
            if key in role_title:
                for skill_code in skill_codes:
                    acc = skill_map[skill_code]
                    acc.has_presence = True
                    acc.evidence_sources.add("role_title")

    if start and not isinstance(start, datetime): 
        start = dparser.parse(start)    

    for mention in skill_mentions:
        SkillID, SkillCode, SkillType, confidence, method = normalize_and_match_skill(
            raw_name=mention["raw_name"],
            master_skills=master_skills,
            vector_index=vector_index,
            embed_fn=embed_fn,
            context_text=mention["context"]
        )

        if not SkillCode:
            print(f"No match found for {mention['raw_name']}")
            continue  # disambiguation blocked / no match

        acc = skill_map[SkillCode]

        acc[f"{level}_months"] += months
        
        if acc["first_used"] and isinstance(acc["first_used"], str):            
            acc["first_used"] = dparser.parse(acc["first_used"])     

        acc["first_used"] = (
            (start if not acc["first_used"]
            else min( acc["first_used"], start)
            ) 
        )        

        """
        Very important to understand recency. A skill that was used long back
        will mean that the the candidate is not 'current' on that skill.
        """
        acc["last_used"] = (
            end if not acc["last_used"]
            else max(acc["last_used"], end)
        )

        evidence_weight = SOURCE_EVIDENCE_WEIGHT[mention["source"]]
        acc["evidence_score"] += evidence_weight
        acc["evidence_sources"].add(mention["source"])
        
        """
        has_presence indicates the skill is actually explicitly mentioned
        by the candidate in the resume.
        """
        if(mention["source"] == "skills_section"):
            acc.has_presence =  True
        
        acc["max_evidence_strength"] = max(
            EVIDENCE_STRENGTH[src] for src in acc['evidence_sources'] 
        )

        """
        Calculate the confidence level of the skill we are attributing to 
        this candidate.  60% from the resume, 40% from our matching alorithm
        whether it found a direct match, or through a soft-alignment or vector match.
        """
        blended_confidence = (
            0.6 * mention["confidence"]
            + 0.4 * confidence
        ) * evidence_weight

        acc["confidence_scores"].append(blended_confidence)
        acc["confidence_sources"].append(method)
        
    

def build_professional_profile(raw_experience, ref_date="2026-01-01", master_skills: List = [], vector_index = []):
    """
    Transforms raw experience into a verified profile.
    """
    profile = {"candidate_roles": [], "tech_seniority_matrix": {}}
    today = datetime.strptime(ref_date, "%Y-%m-%d")

    for role in raw_experience:
        # Calculate duration using our deterministic Python logic (as discussed)
        duration = calculate_duration(role['start_date_raw'], role['end_date_raw'])              

        end_dt = today if "present" in  (role['end_date_raw'] or "Present").lower() or role['end_date_raw'] == "N/A" else dparser.parse(role['end_date_raw'])

        technologies = role.get('technologies', [])
        extracted_skills: List[ExtractedSkill] = get_job_skill_mentions(role)
        skills = role.get('skills',[])
      
        # Merge skills into technologies, avoiding duplicates
        from flatten_json import flatten        

        try:
            flat = flatten(skills)
            skill_values = [v for v in flat.values() if isinstance(v, str)]
            #print("Flattened skill values:", skill_values)
            technologies.extend(sk for sk in skill_values if sk not in technologies)        
        except:
            print("Flatten failed with skills")

        #normalize technologies into standard naming convention
        from Shared.normalizer import normalize_skill_text
        technologies = set(normalize_skill_text(item) for item in technologies)

        profile['candidate_roles'].append({
            "title": role['job_title'],
            "verified_duration": duration,
            "start_date_raw": role['start_date_raw'],
            "end_date_raw": end_dt.strftime("%Y-%m-%d"), 
            "extracted_skills": extracted_skills,
            #"tech_stack": standardized_techs,
            "raw_technologies": technologies,
            "domains": role.get('domains', [])
        })

    return profile

def flatten_leaf_values(data):
    from collections.abc import Iterable

    result = []

    if isinstance(data, dict):
        for value in data.values():
            result.extend(flatten_leaf_values(value))

    elif isinstance(data, list):
        for item in data:
            result.extend(flatten_leaf_values(item))

    elif isinstance(data, Iterable):
        for item in data:
            result.extend(flatten_leaf_values(item))

    else:
        result.append(data)

    return result





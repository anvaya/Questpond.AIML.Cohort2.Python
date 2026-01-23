from collections import defaultdict
from datetime import datetime
import json
from Shared import embedder
from Shared.normalizer import normalize_and_match_skill, normalize_job_title
from Candidate.schemas.RawExperience import ExtractedSkill
from Candidate.postprocessor import process_extracted_skills

def get_embedding_cached(conn, text):
    """
    Get embedding from cache or generate and cache it.
    Returns the embedding as a JSON string for SQL Server VECTOR compatibility.

    Args:
        conn: Database connection object
        text: The input text to generate embedding for

    Returns:
        str: JSON string representation of the embedding vector
    """
    cursor = conn.cursor()

    # Check if embedding exists in cache
    cursor.execute("""
        SELECT CAST(Embedding as NVARCHAR(MAX)) as Embedding
        FROM EmbeddingCache
        WHERE InputText = ?
    """, (text,))

    cached_row = cursor.fetchone()

    if cached_row:
        # Update access statistics
        cursor.execute("""
            UPDATE EmbeddingCache
            SET AccessedAt = GETDATE(),
                AccessCount = AccessCount + 1
            WHERE InputText = ?
        """, (text,))
        conn.commit()

        # Return cached embedding as JSON string
        return cached_row.Embedding
        #return json.dumps(embedding_list)

    # Generate new embedding
    embedding = embedder.get_embedding(text)
    embedding_json = json.dumps(embedding)

    # Store in cache
    cursor.execute("""
        INSERT INTO EmbeddingCache (InputText, Embedding)
        VALUES (?, CAST(CAST(? AS NVARCHAR(MAX)) AS VECTOR(768)))
    """, (text, embedding_json))
    conn.commit()

    return embedding_json


def get_contextual_embedding(skill, domain, role, conn):
    """Creates a rich string for embedding to ensure semantic accuracy."""
    context_string = f"Skill: {skill} | Domain: {domain} | Role: {role}"
    return get_embedding_cached(conn, context_string)

def get_skill_embedding(skill, conn):
    """Creates a rich string for embedding to ensure semantic accuracy."""
    context_string = f"{skill}"
    return get_embedding_cached(conn, context_string)

from Candidate.postprocessor import process_extracted_skills
from Candidate.postprocessor import get_job_skill_mentions
from Shared.embedder import get_embedding
from Candidate.postprocessor import infer_level_from_title
from Shared.Schema.Dto import SkillMetrics
from pyodbc import Row
import numpy as np

NORMALIZATION_PRIORITY = {
    "exact": 4,
    "alias": 3,
    "rule": 2,
    "vector": 1
}

def resolve_normalization_method(methods):
    return max(
        methods,
        key=lambda m: NORMALIZATION_PRIORITY.get(m, 0),
        default="unknown"
    )

def sync_profile_to_master(profile, raw_experience, conn):
    
    candidate_name = profile.get('identity').get("full_name", "Unknown Candidate")
    cursor = conn.cursor()

    # 1. Register Candidate
    cursor.execute("INSERT INTO Candidates (FullName, ExperienceJson) OUTPUT INSERTED.CandidateID VALUES (?,CAST(? as nvarchar(MAX)))", (candidate_name, json.dumps(raw_experience) ))
    candidate_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT [SkillID],[SkillName],[SkillCode],[Tokens],[ParentSkillId],[Aliases],[DisambiguationRules],[SkillType] FROM [ATSCohort].[dbo].[MasterSkills]")
    master_skill_list = cursor.fetchall()
    
    cursor.execute("SELECT [SkillID],[SkillName],[SkillCode],[Aliases],[DisambiguationRules],[SkillType], [SkillVector] as embedding from [ATSCohort].[dbo].[MasterSkills]")
    vector_index = cursor.fetchall()        

    for row in vector_index:
        # 1. Parse the string '[...]' into a Python list
        # json.loads handles scientific notation and commas automatically
        python_list = json.loads(row.embedding)
        
        # 2. Convert to a numpy float array and assign it back to the row
        row.embedding = np.array(python_list).astype(float)

    skill_map = defaultdict(SkillMetrics)

    # 2. Iterate through candidate_roles (since tech_seniority_matrix is empty)
    for role in profile.get("candidate_roles", []):
        role_title_raw = role.get("title", "")
        role_title = normalize_job_title(role_title_raw)
        
        # Combine domains into a single string for context
        domains = ", ".join(role.get("domains", []))
        duration = role.get("verified_duration", 0)

        start_date = role.get('start_date_raw')
        end_date = role.get("end_date_raw",datetime.now().strftime("%Y-%m-%d")) # Default to current for 'Present'        

        #Fetch skills mentioned in experience, with 
        #their types (skill, role title, etc.)
        mentions = get_job_skill_mentions(role)
        process_extracted_skills(mentions, master_skill_list, vector_index, get_embedding, skill_map, infer_level_from_title(role_title), duration, start_date, end_date,role_title)            
       
    
    for acc in skill_map.values():
        acc.total_months = (
            acc.junior_months
            + acc.mid_months
            + acc.senior_months
        )
        acc.match_confidence = (
            #get the average confidence score. 
            sum(acc.confidence_scores) / len(acc.confidence_scores) if acc["confidence_scores"] else 0.0
        )        

    #print(skill_map)

    for skill_code, metrics in skill_map.items():
        store_candidate_skill(candidate_id, skill_code, metrics, cursor)        

    conn.commit()
    print(f"Sync complete for {candidate_name}.")

def store_candidate_skill(candidate_id, skill_code, metrics: SkillMetrics, cursor):

    evidence_sources = ', '.join(metrics.evidence_sources)
    confidence_sources =  resolve_normalization_method(metrics.confidence_sources)
    normalization_confidence = max(metrics.confidence_scores, default=0.0)

    result = cursor.execute("SELECT SkillID from MasterSkills where SkillCode = ?", skill_code).fetchone()
    if(result == None):
        print(f"Skill not found for code {skill_code}")
        return 
    
    master_id = result[0]

    cursor.execute("""
        IF EXISTS (SELECT 1 FROM CandidateSkills WHERE CandidateID = ? AND MasterSkillID = ?)
            UPDATE CandidateSkills 
            SET [ExperienceMonths] = ?
                ,[LastUsedDate] = ? 
                ,[MatchConfidence] = ? 
                ,[TotalMonths] = ?
                ,[JuniorMonths] = ?
                ,[MidMonths] = ?
                ,[SeniorMonths] = ?
                ,[FirstUsedDate] = ?
                ,[EvidenceSources] = ?
                ,[EvidenceScore] = ? 
                ,[NormalizationConfidence] = ?
                ,[NormalizationMethod] = ?  
                ,[MaxEvidenceStrength] = ?                    
            WHERE CandidateID = ? AND MasterSkillID = ?
        ELSE
            INSERT INTO CandidateSkills ([CandidateID],[MasterSkillID],[ExperienceMonths],[LastUsedDate],[MatchConfidence]
                                        ,[TotalMonths],[JuniorMonths],[MidMonths],[SeniorMonths],[FirstUsedDate],[EvidenceSources]
                                        ,[EvidenceScore],[NormalizationConfidence],[NormalizationMethod],[MaxEvidenceStrength])
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (candidate_id, master_id, 
                metrics.total_months, metrics.last_used, metrics.match_confidence, metrics.total_months, 
                metrics.junior_months, metrics.mid_months, metrics.senior_months, metrics.first_used, evidence_sources, metrics.evidence_score, normalization_confidence, confidence_sources, metrics.max_evidence_strength, candidate_id, master_id,
                 
                candidate_id, master_id, 
                metrics.total_months, metrics.last_used, metrics.match_confidence, metrics.total_months, 
                metrics.junior_months, metrics.mid_months, metrics.senior_months, metrics.first_used, evidence_sources, metrics.evidence_score, normalization_confidence , confidence_sources, metrics.max_evidence_strength
            ))


#not using anymore, but could be beneficial if our master skills
#database does not have a skill defined.
def store_unmapped_skill(candidate_id, tech, role, cursor):
    """
    Saves technical terms that failed to match the MasterSkills taxonomy.
    This preserves the 'Raw Truth' of the resume for keyword search and discovery.
    """
    # Extract metadata from the role object (derived from profile.json)
    role_title = role.get("title", "Unknown Role")
    duration = role.get("verified_duration", 0)
    last_used = role.get("end_date_raw")
    now = datetime.now()
    
    # In a professional ATS, we handle the case where the date might be 
    # 'Present' or empty by defaulting to the current system date (Jan 2026).
    if not last_used or str(last_used).lower() == "present":
        last_used =  now.strftime("%Y-%m-%d")

    insert_sql = """
    INSERT INTO UnmappedSkills (
        CandidateID, 
        RawSkillName, 
        RoleTitle, 
        ExperienceMonths, 
        LastUsedDate
    ) VALUES (?, ?, ?, ?, ?)
    """
    
    try:
        cursor.execute(insert_sql, (
            candidate_id, 
            tech, 
            role_title, 
            duration, 
            last_used
        ))
    except Exception as e:
        print(f"Error logging unmapped skill '{tech}': {e}")
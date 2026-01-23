import json
import math

from datetime import datetime
from Employer.PostProcessor import post_process_jd_profile
from Employer.schemas.LLMResponse import CategoryRequirement, JobSkillProfile, PrimaryDomain, RequirementLevel, SkillRequirement, SkillSource
from Shared.embedder import get_embedding
from Shared.llm_wrapper import llm, OllamaService, THINKING_CHAT_MODEL
from pydantic import TypeAdapter
from copy import deepcopy
from datetime import date, timedelta
from math import log
from datetime import date
from pyodbc import Cursor
from Shared.normalizer import normalize_and_match_skill
from math import log
from datetime import date
from Shared.db import fetch_primary_domains, rows_to_dict


SENIORITY_THRESHOLDS = {
    "Junior": {
        "min_total_months": 6,
        "min_mid_months": 0,
        "min_senior_months": 0,
    },
    "Mid": {
        "min_total_months": 18,
        "min_mid_months": 12,
        "min_senior_months": 0,
    },
    "Senior": {
        "min_total_months": 36,
        "min_mid_months": 24,
        "min_senior_months": 12,
    },
    "Lead": {
        "min_total_months": 60,
        "min_mid_months": 36,
        "min_senior_months": 24,
    },
}

RECENCY_MONTHS_LIMIT = 36  # configurable


class SOTAMatchingEngine:
    def __init__(self, db_conn):
        self.conn = db_conn
        self.cursor:Cursor = db_conn.cursor()
        self.current_date = datetime(2018, 1, 9) # Professional baseline
        
        self.cursor.execute("SELECT [SkillID],[SkillName],[SkillCode],[Tokens],[ParentSkillId],[Aliases],[DisambiguationRules],[SkillType] FROM [ATSCohort].[dbo].[MasterSkills]")
        self.master_skill_list = self.cursor.fetchall()
    
        self.cursor.execute("SELECT [SkillID],[SkillName],[SkillCode],[Aliases],[DisambiguationRules],[SkillType], [SkillVector] as embedding from [ATSCohort].[dbo].[MasterSkills]")
        self.vector_index = self.cursor.fetchall()        
        
        self.llm = llm()
   
    def get_embedding_cached(self, text):
        """
        Get embedding from cache or generate and cache it.
        Returns the embedding as a JSON string for SQL Server VECTOR compatibility.

        Args:
            text: The input text to generate embedding for

        Returns:
            str: JSON string representation of the embedding vector
        """
        # Check if embedding exists in cache
        self.cursor.execute("""
            SELECT CAST(Embedding AS NVARCHAR(MAX)) as Embedding
            FROM EmbeddingCache
            WHERE InputText = ?
        """, (text,))

        cached_row = self.cursor.fetchone()

        if cached_row:
            # Update access statistics
            self.cursor.execute("""
                UPDATE EmbeddingCache
                SET AccessedAt = GETDATE(),
                    AccessCount = AccessCount + 1
                WHERE InputText = ?
            """, (text,))
            self.cursor.commit()

            # Return cached embedding as JSON string
            embedding_list = cached_row.Embedding #.tolist() if hasattr(cached_row.Embedding, 'tolist') else list(cached_row.Embedding)
            return embedding_list #json.dumps(embedding_list)

        # Generate new embedding
        embedding = get_embedding(text)
        embedding_json = json.dumps(embedding)

        # Store in cache
        self.cursor.execute("""
            INSERT INTO EmbeddingCache (InputText, Embedding)
            VALUES (?, CAST(CAST(? AS NVARCHAR(MAX)) AS VECTOR(768)))
        """, (text, embedding_json))
        self.cursor.commit()

        return embedding_json

    

    def parse_jd_with_inference(self, jd_text):

        primary_domains = fetch_primary_domains  (self.cursor)

        """Uses LLM to extract explicit skills and infer companion technologies."""
        prompt = f"""
You are an expert technical job description parser.

Your task is to analyze the provided Job Description text and extract a structured
JobSkillProfile in STRICT JSON format that conforms exactly to the schema described below.

You MUST follow all rules carefully. Any deviation will cause validation failure.

────────────────────────────────────────────
INPUT
────────────────────────────────────────────
Job Description:
{jd_text}

────────────────────────────────────────────
OUTPUT FORMAT (STRICT)
────────────────────────────────────────────
Return ONLY a valid JSON object matching this structure:

{{
  "role_context": string,
  "job_metadata": {{
    "primary_domain": string,
    "seniority_level": string
  }},
  "requirements": [
    SkillRequirement | CategoryRequirement
  ]
}}

DO NOT include explanations, markdown, or extra text.
DO NOT invent fields.
DO NOT omit required fields.

────────────────────────────────────────────
PRIMARY DOMAIN (REQUIRED)
────────────────────────────────────────────
Choose EXACTLY ONE PrimaryDomain from the list below.
DO NOT invent new values.

Allowed values:
{primary_domains}

If unsure, choose the closest primary responsibility.
If the JD is generic or unclear, use "General".

────────────────────────────────────────────
SENIORITY LEVEL (REQUIRED)
────────────────────────────────────────────
Choose EXACTLY ONE value:

Junior | Mid | Senior | Lead

Base this on explicit wording such as:
- "Junior", "Entry level"
- "Mid-level", "3-5 years"
- "Senior", "5+ years"
- "Lead", "Principal", "Architect"

If not explicitly stated, choose the most reasonable level based on years mentioned.

────────────────────────────────────────────
REQUIREMENT TYPES
────────────────────────────────────────────

There are TWO types of requirements you can output.

You MUST choose the correct type based on the JD wording.

────────────────────────────────────────────
TYPE 1: SkillRequirement (EXACT SKILL)
────────────────────────────────────────────
Use this when the JD clearly requires a SPECIFIC skill or technology.

Examples:
- "Must have Java"
- "3+ years of AWS"
- "Experience with Spring Boot"

Format:

{{
  "raw_skill": string,
  "source": "explicit" | "inferred",
  "requirement_level": "hard" | "soft",
  "skill_type_hint": "programming" | "framework" | "cloud" | "database" | "tool" | "platform" | "methodology" | "other",
  "min_months": number,
  "skill_group_id": null,
  "expected_evidence": "resume_skill" | "experience_role" | "project" | "implicit"
}}

Rules:
• Use min_months = 0 if no duration is specified.
• Do NOT group multiple skills here unless ALL are required.
• Use "hard" only if the skill is mandatory.
• skill_type_hint must be one of "programming" | "framework" | "cloud" | "database" | "tool" | "platform" | "methodology" | "other".

────────────────────────────────────────────
TYPE 2: CategoryRequirement (FLEXIBLE / ONE-OF)
────────────────────────────────────────────
Use this ONLY when the JD uses flexible language such as:
- "at least one of"
- "such as"
- "or similar"
- "one or more frameworks/libraries"

This means the JD is asking for a CAPABILITY, not a specific brand/tool.

Format:

{{
  "group_id": string,
  "group_type": "category_any_of",
  "category": "AI Concept" | "AI DevOps" | "AI Domain" | "AI Engineering" | "AI Framework" | "AI Infrastructure" | "AI Soft Signal" | "AI Specialization" | "AI Tool" | "Architecture" | "Backend Framework" | "CI/CD" | "Cloud" | "Cloud Service" | "CSS Framework" | "Database" | "DevOps Tool" | "Frontend Framework" | "Programming Language" | "Security" | "Testing" | "Web Technology",
  "min_required": number,
  "example_skills": [string],
  "requirement_level": "hard" | "soft",
  "source": "explicit" | "inferred"
}}

Rules:
• category MUST correspond to a skill category (e.g. "Frontend Framework"), pick the best match from the values provided.
• example_skills are illustrative only, not mandatory.
• min_required is usually 1 unless explicitly stated otherwise.
• Do NOT create separate SkillRequirements for the example skills.

────────────────────────────────────────────
CATEGORY-BASED MATCHING RULES (IMPORTANT)
────────────────────────────────────────────
Use CategoryRequirement when the JD intent is flexible.

Examples:

JD: "Experience with at least one frontend framework such as React, Angular, or Knockout"

→ Output ONE CategoryRequirement:
- category = "Frontend Framework"
- min_required = 1
- example_skills = ["React", "Angular", "Knockout"]

JD: "Responsive design using Bootstrap or similar frameworks"

→ Output ONE CategoryRequirement:
- category = "Frontend Framework"
- example_skills = ["Bootstrap"]

DO NOT:
• Require all listed example skills.
• Invent categories not supported by the skill taxonomy.
• Use category-based requirements for programming languages,
  databases, or cloud providers unless flexibility is explicit.

────────────────────────────────────────────
GENERAL RULES (VERY IMPORTANT)
────────────────────────────────────────────
• At least ONE requirement must be "hard".
• Be conservative: do NOT infer skills unless strongly implied.
• Do NOT guess experience durations.
• Normalize obvious formatting issues (e.g., React.js → React.js).
• The output MUST be valid JSON and match the schema exactly.

────────────────────────────────────────────
IMPORTANT GROUPING RULE:
────────────────────────────────────────────
Only group skills together if they represent the SAME underlying capability.

Do NOT group:
• Frontend frameworks (React, Angular, Knockout)
  together with
• CSS or UI frameworks (Bootstrap, Tailwind, Material UI)

Even if both relate to frontend development, they represent DIFFERENT intents
and MUST be output as separate CategoryRequirements.


────────────────────────────────────────────
FINAL CHECK BEFORE OUTPUT
────────────────────────────────────────────
Before returning the JSON, verify:
✔ primary_domain is from the allowed list
✔ seniority_level is valid
✔ requirements is a list
✔ category-based requirements are grouped correctly
✔ no extra text is included

Now return the JSON.
"""
        
        # f"""
        # Analyze this JD. Extract Explicit skills and Infer Implicit/Companion skills.
        # Return ONLY valid JSON.
        # JD: {jd_text}
        # """
        
        ollama_service = OllamaService()        
        response = ollama_service.chat_completion(
            messages=[{'role': 'user', 'content': prompt}],
            model= THINKING_CHAT_MODEL,  # Using the configured model
            retry_count=2,
            retry_delay=3,
            extract_json=True,
            #json_schema= TypeAdapter(JobSkillProfile).json_schema()
        )
    
        #print(response['message']['content'])
        import pathlib    
        save_path = pathlib.Path(__file__).parent.parent / "temp" / "raw_jd_reponse.json" 
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(response['message']['content']))

        profile = JobSkillProfile.model_validate(response['message']['content'])

        if profile.job_metadata.primary_domain not in primary_domains:
            profile.job_metadata.primary_domain = PrimaryDomain.general

        return post_process_jd_profile( profile )
    

    def get_skill_type_weights(self) -> dict:
        """
        Returns:
        { SkillType -> weight }
        """

        self.cursor.execute(
            """
            SELECT SkillType, BaseWeight as Weight
            FROM SkillTypeWeights
            """
        )
        rows = rows_to_dict(self.cursor)

        return {
            row["SkillType"]: row["Weight"]
            for row in rows
        }


    def get_role_skill_type_weights(
        self,
        primary_domain,
        seniority_level
    ) -> dict:
        """
        Returns role-specific SkillType multipliers.
        """

        self.cursor.execute(
            """
            SELECT SkillType, WeightMultiplier as Weight
            FROM RoleSkillTypeWeights
            WHERE PrimaryDomain = ?
            AND SeniorityLevel = ?
            """,
            (primary_domain.value, seniority_level.value)
        )
        
        rows = rows_to_dict(self.cursor)

        return {
            row["SkillType"]: row["Weight"]
            for row in rows
        }

    def rank_candidates(self, jd_text: str, limit: int = 50) -> dict: 
        """
        Fully refactored deterministic ranking engine.
        Returns ranked, explainable candidates.
        """

        # --------------------------------------------------
        # 1. Parse + validate + post-process JD
        # --------------------------------------------------
        jd_profile = self.parse_jd_with_inference(jd_text)

        # --------------------------------------------------
        # 2. Eligibility gate (HARD FILTER)
        # --------------------------------------------------
        eligible_candidate_ids = self.get_eligible_candidates(jd_profile)

        print(f'candidates: {eligible_candidate_ids}')

        if not eligible_candidate_ids:
            return {"results": [], "role_context": jd_profile.role_context}

        # --------------------------------------------------
        # 3. Preload weights (once)
        # --------------------------------------------------
        skill_type_weights = self.get_skill_type_weights()
        role_type_weights = self.get_role_skill_type_weights(
            jd_profile.job_metadata.primary_domain,
            jd_profile.job_metadata.seniority_level
        )

        ranked_results = []

        print (f"Found {len(eligible_candidate_ids)} eligible candidates.")
        
        if(len(eligible_candidate_ids) > 0):
            placeholders = ', '.join(['?'] * len(eligible_candidate_ids))
            self.cursor.execute(f"SELECT CandidateID, FullName from Candidates where CandidateID in ({placeholders})", *eligible_candidate_ids)
            rows = self.cursor.fetchall()
            candidate_dict = {row.CandidateID: row.FullName for row in rows}
        else:
            candidate_dict = {}

        max_score: float=  self.calculate_max_possible_score(jd_profile)

        # --------------------------------------------------
        # 4. Score eligible candidates ONLY
        # --------------------------------------------------
        for candidate_id in eligible_candidate_ids:
            score, breakdown = self._score_candidate(
                candidate_id=candidate_id,
                jd_profile=jd_profile,                
                max_score=max_score 
                #skill_type_weights=skill_type_weights,
                #role_type_weights=role_type_weights
            ) # type: ignore


                # "skill": req.raw_skill,
                # "matched": True,
                # "months": row.TotalMonths,
                # "score": round(skill_score, 4),
                # "reason": self._build_explanation(
                #     req,
                #     row,
                #     skill_score
                # )

            ranked_results.append({
                "name": candidate_dict[candidate_id],
                "candidate_id": candidate_id,
                "score": round(score, 4),
                #"breakdown": breakdown,
                "matches": [f"{item['skill']} { ('(verified)' if 'explicitly' in item['reason'] else '(inferred)') }" for item in breakdown],
                "confidence": 'Strong Match',
                "skill_breakdown": [{ "skill_name": itm['skill'], "match_type": itm['match_type'], "type": itm["type"],  
                                        "last_used_date":  itm['last_used_date'].strftime('%m-%d-%Y') if isinstance(itm['last_used_date'], date) else itm['last_used_date'], 
                                         "weight": itm["weight"], "experience_months": itm['months'], "recency_score":itm['recency_score'], 
                                         "competency_score": 100 if itm['competency_score']>1 else itm['competency_score'] * 100, 
                                         "contribution_to_total": itm['score']*100/max_score if max_score else 0 }
                                          for itm in breakdown
                                    ],
                "unmatched_skills": [],
                "total_jd_skills":  len(jd_profile.requirements),
                "matched_skill_count": len(breakdown),
                "unmatched_skill_count": 0
            })

        # --------------------------------------------------
        # 5. Sort & return
        # --------------------------------------------------
        ranked_results.sort(
            key=lambda x: x["score"],
            reverse=True
        )   

        print(ranked_results)      
        return {"results": ranked_results[:limit], "role_context": jd_profile.role_context}


    def _get_hard_jd_skills(self, jd_data):
        return [
            r for r in jd_data.requirements
            if r.requirement_level == RequirementLevel.hard
        ]
    
    def _resolve_skill_tree(self, root_skill_code: str) -> set[int]:
        """
        Returns all SkillIDs in the subtree rooted at root_skill_code (inclusive).
        """

        self.cursor.execute(
            """
            WITH SkillTree AS (
                SELECT SkillID, SkillCode
                FROM MasterSkills
                WHERE SkillCode = ?

                UNION ALL

                SELECT ms.SkillID, ms.SkillCode
                FROM MasterSkills ms
                JOIN SkillTree st ON ms.ParentSkillId = st.SkillId
            )
            SELECT SkillID FROM SkillTree
            """,
            (root_skill_code,)
        )

        rows = rows_to_dict(self.cursor)
        return {r["SkillID"] for r in rows}

    def _resolve_implied_skills(self, skill_code: str) -> set[int]:
        """
        Returns SkillIDs implied by the given skill_code.
        """

        self.cursor.execute(
            """
            SELECT ms.SkillID
            FROM SkillImplications si
            JOIN MasterSkills ms ON ms.SkillCode = si.ToSkillCode
            WHERE si.FromSkillCode = ?
            """,
            (skill_code,)
        )

        rows = rows_to_dict(self.cursor)
        return {r["SkillID"] for r in rows}

    def _get_required_evidence_strength(self, requirement_level: RequirementLevel) -> int:
        """
        Hard skills require stronger evidence than soft skills.
        """

        if requirement_level == RequirementLevel.hard:
            return 2  # role_title or higher
        return 1     # skills_section acceptable


    def get_eligible_candidates(self, jd_data) -> set[int]:
        """
        Returns candidate IDs that satisfy ALL hard JD requirements using:
        - exact skills OR category-based requirements
        - skill hierarchy
        - skill implications
        - evidence strength
        - seniority thresholds
        - recency constraints
        """

        hard_requirements = [
            r for r in jd_data.requirements
            if r.requirement_level == RequirementLevel.hard
        ]

        if not hard_requirements:
            return set()

        seniority = jd_data.job_metadata.seniority_level.value
        thresholds = SENIORITY_THRESHOLDS[seniority]
        recency_cutoff = date.today() - timedelta(days=RECENCY_MONTHS_LIMIT * 30)

        eligible_candidates = None

        for req in hard_requirements:

            required_strength = self._get_required_evidence_strength(req.requirement_level)

            # =====================================================
            # CASE 1: Exact SkillRequirement
            # =====================================================
            if isinstance(req, SkillRequirement):

                skill_id, skill_code, _, _, _ = normalize_and_match_skill(
                    raw_name=req.raw_skill,
                    master_skills=self.master_skill_list,
                    vector_index=self.vector_index,
                    embed_fn=self.get_embedding_cached,
                    context_text=jd_data.role_context,
                    allow_implicit=False
                )

                if not skill_id:
                    continue
                    #return set()

                acceptable_skill_ids = set()
                acceptable_skill_ids |= self._resolve_skill_tree(skill_code) # type: ignore
                acceptable_skill_ids |= self._resolve_implied_skills(skill_code) # type: ignore

                placeholders = ",".join("?" * len(acceptable_skill_ids))

                query = f"""
                SELECT DISTINCT cs.CandidateID
                FROM CandidateSkills cs
                WHERE cs.MasterSkillID IN ({placeholders})
                AND (
                        cs.TotalMonths >= ?
                    OR cs.MaxEvidenceStrength >= ?
                )
                AND cs.MidMonths >= ?
                AND cs.SeniorMonths >= ?
                AND cs.LastUsedDate >= ?
                """

                params = (
                    *acceptable_skill_ids,
                    req.min_months,
                    required_strength,
                    thresholds["min_mid_months"],
                    thresholds["min_senior_months"],
                    recency_cutoff,
                )

            # =====================================================
            # CASE 2: CategoryRequirement (NEW)
            # =====================================================
            else:  # CategoryRequirement

                query = """
                SELECT cs.CandidateID, COUNT(DISTINCT cs.MasterSkillID) AS skill_count
                FROM CandidateSkills cs
                JOIN MasterSkills ms ON ms.SkillID = cs.MasterSkillID
                WHERE ms.Category = ?
                AND (
                        cs.TotalMonths > 0
                    OR cs.MaxEvidenceStrength >= ?
                )
                AND cs.MidMonths >= ?
                AND cs.SeniorMonths >= ?
                AND cs.LastUsedDate >= ?
                GROUP BY cs.CandidateID
                HAVING COUNT(DISTINCT cs.MasterSkillID) >= ?
                """

                params = (
                    req.category,
                    required_strength,
                    thresholds["min_mid_months"],
                    thresholds["min_senior_months"],
                    recency_cutoff,
                    req.min_required,
                )

                print("Category Search:", params )

            self.cursor.execute(query, params)
            rows = rows_to_dict(self.cursor)
            candidate_ids = {r["CandidateID"] for r in rows}

            

            if eligible_candidates is None:
                eligible_candidates = candidate_ids
            else:
                eligible_candidates &= candidate_ids

            if not eligible_candidates:                
                return set()

        print(f'candidates {eligible_candidates}')
        return eligible_candidates or set()
 
    def experience_factor(self, total_months: int, min_months: int) -> float:
        return min(
            1.0,
            math.log(1 + total_months / max(min_months, 1))
        )

    def calculate_max_possible_score(self, jd_profile) -> float:
        """
        Calculates the theoretical maximum score for a JD.
        Independent of any candidate.
        """

        max_score = 0.0

        # Load role-based skill type weights
        self.cursor.execute(
            """
            SELECT SkillType, WeightMultiplier
            FROM RoleSkillTypeWeights
            WHERE PrimaryDomain = ?
            AND (SeniorityLevel = ? OR SeniorityLevel = 'any')
            """,
            (
                jd_profile.job_metadata.primary_domain.value,
                jd_profile.job_metadata.seniority_level.value,
            )
        )

        skill_type_weights = {
            r["SkillType"]: r["WeightMultiplier"]
            for r in rows_to_dict(self.cursor)
        }

        for req in jd_profile.requirements:

            jd_weight = 1.0 if req.requirement_level == RequirementLevel.hard else 0.4

            # SkillRequirement
            if isinstance(req, SkillRequirement):
                skill_weight = skill_type_weights.get(
                    req.skill_type_hint.value,
                    1.0
                )

            # CategoryRequirement
            else:
                # Category defaults to framework weighting
                skill_weight = skill_type_weights.get("framework", 1.0)

            max_score += float(jd_weight) * float(skill_weight)

        return round(max_score, 4)


    def _score_candidate(self, candidate_id: int, jd_profile, max_score: float = 0):
        """
        Scores ONE eligible candidate and returns:
        - total_score (float)
        - breakdown (list of uniform breakdown objects)
        """

        total_score = 0.0
        breakdown = []

        # ---------------------------------------------
        # Load role-based weights
        # ---------------------------------------------
        self.cursor.execute(
            """
            SELECT SkillType, WeightMultiplier
            FROM RoleSkillTypeWeights
            WHERE PrimaryDomain = ?
            AND (SeniorityLevel = ? OR SeniorityLevel = 'any')
            """,
            (
                jd_profile.job_metadata.primary_domain.value,
                jd_profile.job_metadata.seniority_level.value,
            )
        )
        skill_type_weights = {
            r["SkillType"]: r["WeightMultiplier"]
            for r in rows_to_dict(self.cursor)
        }

        # ---------------------------------------------
        # Load candidate skills once
        # ---------------------------------------------
        self.cursor.execute(
            """
            SELECT
                cs.TotalMonths,
                cs.LastUsedDate,
                cs.MaxEvidenceStrength,
                cs.EvidenceSources,
                cs.NormalizationMethod,
                ms.SkillCode,
                ms.SkillType,
                ms.Category
            FROM CandidateSkills cs
            JOIN MasterSkills ms ON ms.SkillID = cs.MasterSkillID
            WHERE cs.CandidateID = ?
            """,
            (candidate_id,)
        )

        rows = rows_to_dict(self.cursor)
        by_skill = {r["SkillCode"]: r for r in rows}
        by_category = {}
        for r in rows:
            by_category.setdefault(r["Category"], []).append(r)

        # ---------------------------------------------
        # Iterate requirements
        # ---------------------------------------------
        for req in jd_profile.requirements:

            jd_weight = 1.0 if req.requirement_level == RequirementLevel.hard else 0.4
            
            skill_weight = skill_type_weights.get(
                getattr(req, "skill_type_hint", "framework"),
                1.0
            )

            # =====================================
            # SkillRequirement
            # =====================================
            if isinstance(req, SkillRequirement):

                _, skill_code, _, _, _ = normalize_and_match_skill(
                    raw_name=req.raw_skill,
                    master_skills=self.master_skill_list,
                    vector_index=self.vector_index,
                    embed_fn=self.get_embedding_cached,
                    context_text=jd_profile.role_context,
                    allow_implicit=False
                )

                row = by_skill.get(skill_code)

                if not row:
                    breakdown.append({
                        "weight": float(jd_weight) * float(skill_weight),
                        "skill": req.raw_skill,
                        "type": "Skill",
                        "matched": False,
                        "months": 0,
                        "last_used_date": None,
                        "score": 0.0,
                        "recency_score": 0.0,
                        "competency_score": 0.0,
                        "match_type": "Unmatched",
                        
                        "reason": "Skill not present on candidate profile"
                    })
                    continue

                exp_factor = min(
                    1.0,
                    log(1 + row["TotalMonths"] / max(req.min_months, 1)) # type:ignore
                )

                months_since = (date.today() - row["LastUsedDate"]).days / 30
                recency_factor = 1.0 if months_since <= 12 else \
                                0.8 if months_since <= 36 else \
                                0.6 if months_since <= 60 else 0.3

                evidence_factor = min(row["MaxEvidenceStrength"] / 3.0, 1.0)
                norm_penalty = 0.85 if row["NormalizationMethod"] == "vector" else 1.0

                final = (
                    float(jd_weight)
                    * float(skill_weight)
                    * float(exp_factor)
                    * float(recency_factor)
                    * float(evidence_factor)
                    * float(norm_penalty)
                )

                total_score += final

                composit_weight = float(jd_weight) * float(skill_weight)
                c_score = self.calculate_competency_score(row['TotalMonths'], row['LastUsedDate'], composit_weight)
                

                breakdown.append({
                    "weight": float(jd_weight) * float(skill_weight),
                    "skill": req.raw_skill,
                    "type": "Skill",
                    "matched": True,
                    "months": row["TotalMonths"],
                    "last_used_date": row["LastUsedDate"],
                    "score": round(c_score['final_score'],2), #round(final * 100, 2),
                    "recency_score": round(recency_factor * 100, 1),
                    "competency_score": round(c_score['competency_score'], 1),
                    "match_type": "Verified" if evidence_factor >= 1.0 else "Inferred",
                    
                    "reason": f"Matched via {skill_code}"
                })

            # =====================================
            # CategoryRequirement
            # =====================================
            else:
                matches = by_category.get(req.category, [])

                if not matches:
                    breakdown.append({
                        "weight": float(jd_weight) * float(skill_weight),
                        "skill": req.category,
                        "type": "Category",
                        "matched": False,
                        "months": 0,
                        "last_used_date": None,
                        "score": 0.0,
                        "recency_score": 0.0,
                        "competency_score": 0.0,
                        "match_type": "Unmatched",
                        
                        "reason": "No skills in required category"
                    })
                    continue

                best = max(
                    matches,
                    key=lambda r: (r["TotalMonths"], r["MaxEvidenceStrength"])
                )

                exp_factor = min(1.0, log(1 + best["TotalMonths"]))
                months_since = (date.today() - best["LastUsedDate"]).days / 30
                recency_factor = 1.0 if months_since <= 12 else \
                                0.8 if months_since <= 36 else \
                                0.6 if months_since <= 60 else 0.3

                evidence_factor = min(best["MaxEvidenceStrength"] / 3.0, 1.0)
                norm_penalty = 0.85 if best["NormalizationMethod"] == "vector" else 1.0

                final = (
                    float(jd_weight)
                    * float(skill_weight)
                    * float(exp_factor)
                    * float(recency_factor)
                    * float(evidence_factor)
                    * float(norm_penalty)
                )

                total_score += final

                composit_weight = float(jd_weight) * float(skill_weight)
                c_score = self.calculate_competency_score(best['TotalMonths'], best['LastUsedDate'], composit_weight)

                
                
                #c_score["score"] = round(normalized * 100, 2)
                #c_score["confidence"] = self.confidence(c["score"])

                breakdown.append({
                    "weight": composit_weight,
                    "skill": req.category,
                    "type": "Category",
                    "matched": True,
                    "months": best["TotalMonths"],
                    "last_used_date": best["LastUsedDate"],
                    "score": c_score['final_score'], #round(final, 2),
                    "recency_score": round(recency_factor * 100, 1),
                    "competency_score": round(c_score['competency_score'] * 100 if c_score['competency_score']<1 else 100), #round(evidence_factor, 1),
                    "match_type": "Verified" if evidence_factor >= 1.0 else "Inferred",
                    
                    "reason": f"Matched via {best['SkillCode']} ({req.category})"
                })

        normalized = (total_score / max_score if max_score else 0)*100

        return round(normalized, 4), breakdown
    

    def _build_explanation(self, req, row, score):
        reasons = []

        reasons.append(f"{row.TotalMonths} months experience")

        if row.SeniorMonths > 0:
            reasons.append("senior-level exposure")

        if "skills_section" in row.EvidenceSources:
            reasons.append("explicitly listed by candidate")

        if row.NormalizationMethod == "vector":
            reasons.append("semantic match")

        return "; ".join(reasons)


    
    def calculate_competency_score(self, months, last_used, weight):
        """
        Calculates competency score components for detailed breakdown.

        Returns a dictionary with all score components:
        - depth: Experience depth (0-1, based on 36 months max)
        - recency_score: How recent the skill was used (0-1)
        - competency_score: Depth × Recency (0-1)
        - final_score: Competency × Weight (final contribution)
        - experience_months: Raw input months
        - last_used_date: Raw input last used date
        """
        experience_months = months
        last_used_date = last_used

        # Calculate depth and recency separately
        depth = min(1.0, experience_months / 36.0)
        gap_months = (self.current_date.year - last_used_date.year) * 12 + (self.current_date.month - last_used_date.month)

        # 2026 baseline: Sagun's 2017 roles get legacy penalty
        recency_score = 1.0 if gap_months < 12 else (0.6 if gap_months < 48 else 0.25)

        # Competency score (depth * recency)
        competency_score = depth * recency_score

        # Final score with weight applied
        final_score = competency_score * weight

        return {
            "depth": depth,
            "recency_score": recency_score,
            "competency_score": competency_score,
            "final_score": final_score,
            "experience_months": experience_months,
            "last_used_date": last_used_date
        }
    
    def confidence(self, score: float):
        if score >= 80: return "Strong Match"
        if score >= 60: return "Good Match"
        if score >= 40: return "Partial Match"
        return "Weak Match" 

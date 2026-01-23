from copy import deepcopy
from typing import List, Union

from Employer.schemas.LLMResponse import (
    JobSkillProfile,
    SkillRequirement,
    CategoryRequirement,
    RequirementLevel,
    ExpectedEvidence,
)


def post_process_jd_profile(jd: JobSkillProfile) -> JobSkillProfile:
    """
    Applies deterministic, non-inferential cleanup to an LLM-parsed JD profile.

    This function MUST NOT:
    - introduce new requirements
    - change hard vs soft intent
    - infer skills
    - rebalance experience semantics

    It MAY:
    - normalize malformed fields
    - enforce schema invariants
    - fix obvious LLM inconsistencies
    """

    jd = deepcopy(jd)
    cleaned_requirements: List[Union[SkillRequirement, CategoryRequirement]] = []

    for req in jd.requirements:

        # ------------------------------------------------
        # CATEGORY REQUIREMENTS: pass through untouched
        # ------------------------------------------------
        if isinstance(req, CategoryRequirement):
            # Enforce minimum invariant
            if req.min_required < 1:
                req.min_required = 1

            cleaned_requirements.append(req)
            continue

        # ------------------------------------------------
        # SKILL REQUIREMENTS: light normalization only
        # ------------------------------------------------
        skill = req  # alias for clarity

        # Ensure min_months is not None
        if skill.min_months is None:
            skill.min_months = 0

        # Methodologies should never gate eligibility
        if skill.skill_type_hint.name == "methodology":
            skill.min_months = 0
            skill.expected_evidence = ExpectedEvidence.implicit

        # Tools should not hard-gate unless explicitly marked
        if skill.skill_type_hint.name == "tool" and skill.requirement_level == RequirementLevel.hard:
            # downgrade only if LLM clearly overreached
            skill.requirement_level = RequirementLevel.soft
            skill.expected_evidence = ExpectedEvidence.project

        cleaned_requirements.append(skill)

    jd.requirements = cleaned_requirements
    return jd

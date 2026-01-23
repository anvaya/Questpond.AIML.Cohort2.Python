from dataclasses import dataclass
from typing import Optional

@dataclass
class NormalizedSkillResult:
    skill_code: Optional[str]
    skill_type: Optional[str]
    confidence: float
    method: str  # exact | alias | vector | rule | none


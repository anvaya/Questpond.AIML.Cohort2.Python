from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List

@dataclass
class SkillMetrics:
    junior_months: int = 0
    mid_months: int = 0
    senior_months: int = 0
    first_used: Optional[date] = None
    last_used: Optional[date] = None
    evidence_score: float = 0.0
    total_months: int = 0
    # Use field(default_factory=list) for mutable types like lists
    confidence_scores: List[float] = field(default_factory=list)
    match_confidence: float = 0.0
    evidence_sources: set = field(default_factory=set)
    max_evidence_strength: int = 1
    confidence_sources = []    
    normalization_confidence: float = 0.00
    normalization_methods = []
    has_presence: bool = False

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
       setattr(self, key, value)
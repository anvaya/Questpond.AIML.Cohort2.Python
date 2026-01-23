from dataclasses import dataclass
import numpy as np

@dataclass
class VectorSkillEntry:
    skill_code: str
    skill_type: str
    embedding: np.ndarray
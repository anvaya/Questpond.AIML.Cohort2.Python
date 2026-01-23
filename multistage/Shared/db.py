from typing import Any
import pyodbc
from pyodbc import Cursor

SQL_CONFIG = {
    'server': 'Anvaya-Ryzen5\\SQLEXPRESS_2025',
    'database': 'ATSCohort',
    'driver': '{ODBC Driver 18 for SQL Server}' # Ensure you have this driver
}

def connect_db():
    conn_str = f"DRIVER={SQL_CONFIG['driver']};SERVER={SQL_CONFIG['server']};DATABASE={SQL_CONFIG['database']};Trusted_Connection=yes;Encrypt=no;"
    return pyodbc.connect(conn_str)


def rows_to_dict(cursor: Cursor) -> list[dict[str, Any]]:
    columns = [column[0] for column in cursor.description]
    results_as_dict_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return results_as_dict_list

def fetch_primary_domains(cursor) -> list[str]:
    """
    Fetch distinct PrimaryDomain values from RoleSkillTypeWeights.
    Excludes NULLs and returns a sorted list.
    """
    cursor.execute(
        """
        SELECT DISTINCT PrimaryDomain
        FROM RoleSkillTypeWeights
        WHERE PrimaryDomain IS NOT NULL
        """
    )

    rows = cursor.fetchall()
    domains = [row[0] for row in rows if row[0]]

    # Defensive: sort for deterministic prompt output
    return sorted(set(domains))

def resolve_acceptable_skill_ids(cursor, root_skill_code: str) -> set[int]:
    """
    Resolves a skill to all acceptable SkillIDs via:
    - taxonomy (parent/child)
    - implications
    """

    # 1. Hierarchy
    cursor.execute(
        """
        WITH SkillTree AS (
            SELECT SkillID, SkillCode
            FROM MasterSkills
            WHERE SkillCode = ?

            UNION ALL

            SELECT ms.SkillID, ms.SkillCode
            FROM MasterSkills ms
            JOIN SkillTree st ON ms.ParentSkillId = st.SkillCode
        )
        SELECT SkillID FROM SkillTree
        """,
        (root_skill_code,)
    )

    skill_ids = {row.SkillID for row in cursor.fetchall()}

    # 2. Implications
    cursor.execute(
        """
        SELECT ms.SkillID
        FROM SkillImplications si
        JOIN MasterSkills ms ON ms.SkillCode = si.ToSkillCode
        WHERE si.FromSkillCode = ?
        """,
        (root_skill_code,)
    )

    skill_ids |= {row.SkillID for row in cursor.fetchall()}

    return skill_ids

def candidates_for_skill_requirement(
    cursor,
    skill_code: str,
    min_months: int,
    required_strength: int
) -> set[int]:

    acceptable_skill_ids = resolve_acceptable_skill_ids(cursor, skill_code)
    if not acceptable_skill_ids:
        return set()

    placeholders = ",".join("?" * len(acceptable_skill_ids))

    query = f"""
    SELECT DISTINCT CandidateID
    FROM CandidateSkills
    WHERE MasterSkillID IN ({placeholders})
      AND (
            TotalMonths >= ?
         OR MaxEvidenceStrength >= ?
      )
    """

    cursor.execute(query, (*acceptable_skill_ids, min_months, required_strength))
    return {row.CandidateID for row in cursor.fetchall()}

def candidates_for_category_requirement(
    cursor,
    category: str,
    min_required: int,
    required_strength: int
) -> set[int]:

    cursor.execute(
        """
        SELECT cs.CandidateID, COUNT(DISTINCT cs.MasterSkillID) AS match_count
        FROM CandidateSkills cs
        JOIN MasterSkills ms ON ms.SkillID = cs.MasterSkillID
        WHERE ms.Category = ?
          AND (
                cs.TotalMonths > 0
             OR cs.MaxEvidenceStrength >= ?
          )
        GROUP BY cs.CandidateID
        HAVING COUNT(DISTINCT cs.MasterSkillID) >= ?
        """,
        (category, required_strength, min_required)
    )

    return {row.CandidateID for row in cursor.fetchall()}

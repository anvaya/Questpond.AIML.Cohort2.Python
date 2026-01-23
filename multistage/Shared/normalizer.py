import re
from typing import List, Dict
from Shared.Schema.Normalized import NormalizedSkillResult
import json
from Shared.vector import cosine_similarity
from pyodbc import Row

# Pre-normalization rewrite rules
REWRITE_RULES: Dict[str, str] = {
    ".net": "dotnet",
    "asp.net": "asp dotnet",
    "node.js": "node js",
    "nodejs": "node js",
    "knockout.js": "knockout js",
    "react.js": "react js",
    "vue.js": "vue js",
    "next.js": "next js",
    "nuxt.js": "nuxt js",
    "c sharp": "c#",
    "c plus plus": "c++",
    "javascript": "javascript",  # explicitly preserved
    "jscript": "javascript",
}

ROLE_TITLE_SKILL_MAP = {
    "dot net developer": ["framework_dotnet"],
    "java developer": ["language_java"],
    "python developer": ["language_python"],
    "frontend developer": ["web_html", "web_css", "language_javascript"],
    "backend developer": [],
}


CAMEL_CASE_PATTERN = re.compile(r'(?<!^)(?=[A-Z])')

PUNCTUATION_PATTERN = re.compile(r'[^\w\s\+#]')

WHITESPACE_PATTERN = re.compile(r'\s+')



def normalize_job_title(title: str) -> str:
    """
    Canonicalizes job titles for deterministic matching.
    This is NOT inference.
    """
    if not title:
        return ""

    t = title.lower()

    # Normalize separators
    t = re.sub(r"[_\-\/]+", " ", t)

    # Normalize .NET variants
    t = t.replace(".net", " dot net ")
    t = t.replace("dotnet", " dot net ")
    t = t.replace("asp.net", " asp net ")

    # Remove non-alphanumerics
    t = re.sub(r"[^a-z0-9\s]", "", t)

    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()

    return t



def normalize_text(text: str) -> str:    
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s\.\+#]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def passes_disambiguation(skill: Row, normalized: str, context: str) -> bool:
    """
    We can define set of rules in the db
    to prevent false positives/negatives on
    matching. Rules are stored with MasterSkills.
    
    :param skill: Database SkillMaster row
    :type skill: Row
    :param normalized: Cleaned up text to match
    :type normalized: str
    :param context: Context received such as framwork 
    :type context: str
    :return: Returns true if matched text is a valid match.
    :rtype: bool
    """
    rules_raw = skill.DisambiguationRules
    if not rules_raw:
        return True

    try:
        rules = json.loads(rules_raw)
    except Exception:
        return True  # fail-open, but log in real system

    combined = f"{normalized} {context}".lower()

    for blocked in rules.get("block_if_contains", []):
        if blocked.lower() in combined:
            return False

    allow_list = rules.get("allow_if_contains", [])
    if allow_list:
        return any(a.lower() in combined for a in allow_list)

    return True



def normalize_and_match_skill(
    raw_name: str,
    master_skills: List[Row],
    vector_index=None,
    embed_fn=None,
    context_text: str = "",
    allow_implicit: bool = False
):
    """
    Returns:
      (SkillID, SkillCode, SkillType, confidence, method)
      OR (None, None, None, 0.0, "no_match")
    """

    normalized = normalize_skill_text2(normalize_text(raw_name))
    if not normalized:
        return None, None, None, 0.0, "empty"

    context = normalize_text(context_text)

    # ---------- 1️⃣ EXACT MATCH ----------
    for skill in master_skills:
        if normalize_skill_text2(normalize_text(skill.SkillName)) == normalized:
            if not passes_disambiguation(skill, normalized, context):
                return None, None, None, 0.0, "disambiguation_blocked"

            return (
                skill.SkillID,
                skill.SkillCode,
                skill.SkillType,
                1.00,
                "exact"
            )

    # ---------- 2️⃣ ALIAS MATCH ----------
    for skill in master_skills:
        aliases_raw = skill.Aliases
        if not aliases_raw:
            continue

        try:
            aliases = json.loads(aliases_raw)
        except Exception:
            continue

        for alias in aliases:
            if normalize_skill_text2(normalize_text(alias)) == normalized:
                if not passes_disambiguation(skill, normalized, context):
                    return None, None, None, 0.0, "disambiguation_blocked"

                return (
                    skill.SkillID,
                    skill.SkillCode,
                    skill.SkillType,
                    0.95,
                    "alias"
                )

    # ---------- 3️⃣ TOKEN / RULE MATCH ----------
    for skill in master_skills:
        tokens_raw = skill.Tokens
        if not tokens_raw:
            continue

        try:
            tokens = json.loads(tokens_raw)
        except Exception:
            continue

        normalized_tokens = tokenize_text(normalized)
        # Guardrail for single-letter tokens
        if any(len(tok) == 1 for tok in tokens):
            if len(normalized_tokens) > 1:
                continue

        if all(tok.lower() in normalized_tokens for tok in tokens):        
            if not passes_disambiguation(skill, normalized, context):
                return None, None, None, 0.0, "disambiguation_blocked"

            print(f"Token matched {raw_name} with {skill.SkillCode}")
            return (
                skill.SkillID,
                skill.SkillCode,
                skill.SkillType,
                0.90,
                "rule"
            )

    # ---------- 4️⃣ VECTOR MATCH (STRICT, OPTIONAL) ----------
    if vector_index and embed_fn:
        embeddings = embed_fn(normalized)
        query_vec = (embeddings if isinstance(embeddings, list) else json.loads(embeddings)) 

        best_skill = None
        best_score = 0.0
        
        for entry in vector_index:
            score = cosine_similarity(query_vec, entry.embedding if not isinstance(entry.embedding, str) else json.loads(entry.embedding) ) # type: ignore
            if score > best_score:
                best_score = score
                best_skill = entry

        # VERY STRICT threshold
        if best_skill and best_score >= 0.92:
            skill = best_skill.skill_ref  # reference to MasterSkill row

            # matched, now check for false positives. Java Vs. JavaScript for example.
            if not passes_disambiguation(skill, normalized, context):
                return None, None, None, 0.0, "disambiguation_blocked"

            #print(f"Vector matched {raw_name} with {skill.SkillCode}")
            return (
                skill.SkillID,
                skill.SkillCode,
                skill.SkillType,
                round(best_score, 3),
                "vector"
            )

    # ---------- 5️⃣ NO MATCH ----------
    return None, None, None, 0.0, "no_match"


"""
Useful to break skills term into invidual
skills. HTML/CSS for example are HTML, CSS.
"""
COMPOSITE_SEPARATORS = [
    "/",        # HTML/CSS
    "\\",       # rare but seen
    ",",        # HTML, CSS
    " & ",      # HTML & CSS
    " and ",    # HTML and CSS
    "+",        # C++/CLI + .NET (rare)
]

def split_composite_skill(raw_skill: str) -> List[str]:
    """
    Splits explicit composite skill mentions into atomic skills.
    This is NOT inference.
    """
    if not raw_skill:
        return []

    text = raw_skill.lower().strip()

    # Normalize separators to a single delimiter
    for sep in COMPOSITE_SEPARATORS:
        text = text.replace(sep, "|")

    # Split
    parts = [p.strip() for p in text.split("|")]

    # Remove empty / trivial fragments
    cleaned = []
    for p in parts:
        if len(p) < 2:
            continue
        cleaned.append(p)

    return cleaned


def normalize_skill_text2(text: str) -> str:
    """
    Canonicalizes raw skill text before matching.
    This is NOT inference.
    """
    if not text:
        return ""

    t = text.lower().strip()

    # Normalize separators & punctuation
    t = re.sub(r"[\.]", "", t)          # react.js → reactjs
    t = re.sub(r"[_\-\/]+", " ", t)

    # Normalize common suffixes
    t = re.sub(r"\bprogramming\b", "", t)
    t = re.sub(r"\blanguage\b", "", t)
    t = re.sub(r"\bframework\b", "", t)

    # Normalize versions
    t = re.sub(r"\bhtml\s*5\b", "html", t)
    t = re.sub(r"\bcss\s*3\b", "css", t)

    # Normalize C#
    t = t.replace("c sharp", "c#")
    t = t.replace("csharp", "c#")

    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()

    return t


def normalize_skill_text(text: str) -> str:
    """
    Normalize a skill/technology string for ATS matching.

    Examples:
    - ".NET" -> "dotnet"
    - "ASP.NET MVC" -> "asp dotnet mvc"
    - "Knockout.js" -> "knockout js"
    - "C#" -> "c#"
    - "JavaScript" -> "javascript"
    """

    if not text:
        return ""

    text = text.strip()

    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Apply rewrite rules (order matters)
    for src, target in REWRITE_RULES.items():
        text = text.replace(src, target)

    # Step 3: Split camelCase (ReactJS → React JS)
    text = CAMEL_CASE_PATTERN.sub(' ', text)

    # Step 4: Remove punctuation except + and #
    text = PUNCTUATION_PATTERN.sub(' ', text)

    # Step 5: Normalize whitespace
    text = WHITESPACE_PATTERN.sub(' ', text).strip()

    return text

"""
This was added to prevent false positives where
the skill's name is a single char like `C` or `R`
"""
def is_single_char_token(tok: str) -> bool:
    return len(tok) == 1

def tokenize_text(text: str) -> set[str]:
    """
    Tokenizes text into lowercase word tokens.
    """
    return set(re.findall(r"\b[a-z0-9\+#\.]+\b", text.lower()))


def tokenize_skill(text: str) -> List[str]:
    """
    Tokenize normalized skill text.

    Example:
    - "asp dotnet mvc" -> ["asp", "dotnet", "mvc"]
    """
    normalized = normalize_skill_text(text)
    return normalized.split(" ")

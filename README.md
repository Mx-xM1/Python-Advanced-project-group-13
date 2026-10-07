# Python-Advanced-project-group-13
Food label analyzer 
# ============================================================
# NUTRITION / INGREDIENT EXTRACTION
# ============================================================

NUTRITION_PATTERNS = {
    "calories": r"(?:calories|energy)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
    "sugar": r"(?:total\s+sugars?|sugars?)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g?",
    "fat": r"(?:total\s+fat|fat)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g?",
    "protein": r"protein\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g?",
    "sodium": r"sodium\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*mg?",
}


def extract_nutrition(text):
    normalized = " ".join(text.lower().split())
    nutrition = {}

    for name, pattern in NUTRITION_PATTERNS.items():
        match = re.search(pattern, normalized)
        nutrition[name] = float(match.group(1)) if match else None

    return nutrition


def extract_ingredients(text):
    match = re.search(
        r"ingredients?\s*[:\-]\s*(.*?)"
        r"(?=(?:nutrition facts|calories|allergen|serving size|$))",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return []

    raw = match.group(1).replace("\n", " ")

    return [
        item.strip(" .")
        for item in re.split(r",|;", raw)
        if item.strip()
    ]

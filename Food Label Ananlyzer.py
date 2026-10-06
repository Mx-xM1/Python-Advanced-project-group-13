"""
MEMBER 1 MODULE: Database & Core Analytics
File: database_and_analysis.py
"""

import re
import sqlite3
from pathlib import Path

BASE_DIR = Path(_file_).parent
DB_PATH = BASE_DIR / "food_labels.db"

NUTRITION_PATTERNS = {
    "calories": r"(?:calories|energy)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
    "sugar": r"(?:total\s+sugars?|sugars?)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g?",
    "fat": r"(?:total\s+fat|fat)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g?",
    "protein": r"protein\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g?",
    "sodium": r"sodium\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:mg|g)?",
}

def init_database():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                calories REAL,
                sugar REAL,
                fat REAL,
                protein REAL,
                sodium REAL,
                ingredients TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_analysis(result):
    nutrition = result["nutrition"]
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO analyses (
                product_name, calories, sugar, fat, protein,
                sodium, ingredients, category
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result["product_name"],
            nutrition.get("calories"),
            nutrition.get("sugar"),
            nutrition.get("fat"),
            nutrition.get("protein"),
            nutrition.get("sodium"),
            ", ".join(result["ingredients"]) if result["ingredients"] else "Not detected",
            result["category"],
        ))

def get_history():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("""
            SELECT product_name, calories, sugar, fat, protein,
                   sodium, category, created_at
            FROM analyses
            ORDER BY id DESC
        """).fetchall()

def extract_nutrition(text):
    normalized = " ".join(text.lower().split())
    nutrition = {}
    for name, pattern in NUTRITION_PATTERNS.items():
        match = re.search(pattern, normalized)
        nutrition[name] = float(match.group(1)) if match else None
    return nutrition

def extract_ingredients(text):
    match = re.search(
        r"ingredients?\s*[:\-]\s*(.*?)(?=(?:nutrition facts|calories|allergen|serving size|$))",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return []
    raw = match.group(1).replace("\n", " ")
    return [item.strip(" .") for item in re.split(r",|;", raw) if item.strip()]

def classify_food(nutrition):
    sugar = nutrition.get("sugar") or 0
    sodium = nutrition.get("sodium") or 0
    high_sugar = sugar > 15
    high_sodium = sodium > 500

    if high_sugar and high_sodium:
        return "Higher sugar and sodium"
    if high_sugar:
        return "Higher sugar"
    if high_sodium:
        return "Higher sodium"
    return "General nutrition profile"

def generate_notes(nutrition):
    notes = []
    sugar = nutrition.get("sugar")
    sodium = nutrition.get("sodium")
    protein = nutrition.get("protein")
    calories = nutrition.get("calories")

    if sugar is not None and sugar > 15:
        notes.append("Sugar is relatively high per serving.")
    if sodium is not None and sodium > 500:
        notes.append("Sodium is relatively high per serving.")
    if protein is not None and protein >= 10:
        notes.append("The label reports a notable amount of protein.")
    if calories is not None:
        notes.append(f"Reported calories per serving: {calories}.")
    if not notes:
        notes.append("No notable threshold was detected from the available values.")
    return notes

def analyze_label(text, product_name):
    if not text.strip():
        raise ValueError("Please enter or scan food-label information.")
    nutrition = extract_nutrition(text)
    ingredients = extract_ingredients(text)
    category = classify_food(nutrition)
    notes = generate_notes(nutrition)

    return {
        "product_name": product_name.strip() or "Unknown Product",
        "nutrition": nutrition,
        "ingredients": ingredients,
        "category": category,
        "notes": notes,
    }

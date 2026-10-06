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
    ''''
    Member 2: Computer Vision & OCR Processing Module
    File Name: ocr_processing.py

Repository Name: food-label-analyzer-ocr

Role: Image Processing & Computer Vision Engineer

Code Scope: Handles image loading using OpenCV, grayscale conversion, Otsu threshold image preprocessing, and optical character recognition via PyTesseract.

Python

MEMBER 2 MOPULE: Computer Vision & OCR Processing
File: ocr_processing.py
''''
import platform

try:

import cvz import pytesseract OCR_AVAILABLE = True pytesseract.pytesseract.t esseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" except ImportError:

OCR_AVAILABLE = False

def extract_text_from_image(imag e_path):

if not OCR_AVAILABLE: raise RuntimeError( "OCR dependencies are missing. Run: pip install opencv-python pytesseract" )

image =

if not text.strip():

cvz.imread(str(image_path)) if image is None:

raise ValueError ("The selected image could not be opened.")

# 

import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Import modules written by Member 1 and Member 2
from database_and_analysis import (
    init_database,
    save_analysis,
    get_history,
    analyze_label,
)
from ocr_processing import extract_text_from_image

class FoodLabelAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Food Label Analyzer")
        self.root.geometry("1000x750")
        self.root.minsize(850, 650)
        self.build_interface()

    def build_interface(self):
        title = tk.Label(
            self.root,
            text="FOOD LABEL ANALYZER",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            self.root,
            text="Analyze food-label information using OCR, nutrition extraction and AI analysis",
            font=("Arial", 11)
        )
        subtitle.pack(pady=(0, 15))

        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=25)

        tk.Label(top_frame, text="Product name:").pack(side="left")
        self.product_name = tk.Entry(top_frame, width=40)
        self.product_name.insert(0, "Sample Product")
        self.product_name.pack(side="left", padx=10)

        tk.Button(
            top_frame,
            text="Upload Label Image",
            command=self.upload_image
        ).pack(side="left", padx=5)

        tk.Button(
            top_frame,
            text="Clear",
            command=self.clear_all
        ).pack(side="left", padx=5)

        tk.Label(
            self.root,
            text="Label Information",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", padx=25, pady=(15, 5))

        self.input_box = scrolledtext.ScrolledText(
            self.root,
            height=12,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.input_box.pack(fill="both", expand=True, padx=25)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=12)

        tk.Button(
            button_frame,
            text="ANALYZE LABEL",
            font=("Arial", 12, "bold"),
            command=self.analyze
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="VIEW HISTORY",
            font=("Arial", 12),
            command=self.show_history
        ).pack(side="left", padx=5)

        tk.Label(
            self.root,
            text="Analysis Result",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", padx=25, pady=(5, 5))

        self.result_box = scrolledtext.ScrolledText(
            self.root,
            height=14,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.result_box.pack(fill="both", expand=True, padx=25, pady=(0, 20))

    def upload_image(self):
        path = filedialog.askopenfilename(
            title="Select Food Label Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            text = extract_text_from_image(path)
            self.input_box.delete("1.0", tk.END)
            self.input_box.insert(tk.END, text)
            messagebox.showinfo("OCR Complete", "Text successfully extracted from image.")
        except Exception as error:
            messagebox.showerror("OCR Error", str(error))

    def analyze(self):
        try:
            text = self.input_box.get("1.0", tk.END)
            name = self.product_name.get()
            result = analyze_label(text, name)
            save_analysis(result)
            self.display_result(result)
        except Exception as error:
            messagebox.showerror("Analysis Error", str(error))

    def display_result(self, result):
        nutrition = result["nutrition"]
        lines = [
            "=" * 60,
            f"PRODUCT: {result['product_name']}",
            "=" * 60,
            "",
            "AI ANALYSIS",
            f"Classification: {result['category']}",
            "",
            "NUTRITION INFORMATION",
            "-" * 30,
            f"Calories: {nutrition.get('calories')}",
            f"Sugar: {nutrition.get('sugar')} g",
            f"Fat: {nutrition.get('fat')} g",
            f"Protein: {nutrition.get('protein')} g",
            f"Sodium: {nutrition.get('sodium')} mg",
            "",
            "INGREDIENTS",
            "-" * 30,
            ", ".join(result["ingredients"]) or "Not detected",
            "",
            "ANALYSIS NOTES",
            "-" * 30,
        ]
        lines.extend(f"- {note}" for note in result["notes"])
        lines.extend([
            "",
            "Note: This application provides educational label analysis.",
            "It is not a medical diagnosis or personalized dietary advice.",
        ])

        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, "\n".join(lines))

    def show_history(self):
        history = get_history()
        window = tk.Toplevel(self.root)
        window.title("Analysis History")
        window.geometry("900x500")

        box = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Consolas", 10))
        box.pack(fill="both", expand=True, padx=15, pady=15)

        if not history:
            box.insert(tk.END, "No previous analyses found.")
            return

        for row in history:
            product, calories, sugar, fat, protein, sodium, category, date = row
            box.insert(
                tk.END,
                f"Product: {product}\n"
                f"Calories: {calories} | Sugar: {sugar} g | Fat: {fat} g\n"
                f"Protein: {protein} g | Sodium: {sodium} mg\n"
                f"Classification: {category}\n"
                f"Date: {date}\n"
                + "-" * 70 + "\n"
            )

    def clear_all(self):
        self.product_name.delete(0, tk.END)
        self.product_name.insert(0, "Sample Product")
        self.input_box.delete("1.0", tk.END)
        self.result_box.delete("1.0", tk.END)

if __name__ == "__main__":
    init_database()
    root = tk.Tk()
    app = FoodLabelAnalyzerApp(root)
    root.mainloop() to grayscale and apply Otsu thresholding for higher text readability

gray = cvz.cvtColor (image, cvz.COLOR_BGRZGRAY)

processed = cvz.threshold (gray, 0, 255, cu2.THRESH_BINARY + CUZ.THRESH_OTSU) [I]
text = pytesseract.image_to_strin g(processed) if not text.strip(): raise ValueError ("No readable text was found in the image.")

return text

# Configure default Windows installation path if applicable if platform.system () == "Windows":

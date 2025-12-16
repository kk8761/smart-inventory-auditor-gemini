from google.generativeai.types import Part
from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io
import json
import os

# -------------------------------------------------
# ENV & GEMINI CONFIG
# -------------------------------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="Smart Inventory Auditor")

model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------------------------------------
# MOCK INVENTORY DATABASE
# -------------------------------------------------
inventory_db = {
    "Water Bottle": {"available_units": 40},
    "Laptop": {"available_units": 5},
    "Smartphone": {"available_units": 2}
}

# -------------------------------------------------
# SAFE JSON PARSER (NEVER CRASHES)
# -------------------------------------------------
def safe_parse_gemini(text: str):
    try:
        data = json.loads(text)
        return {
            "item_name": data.get("item_name", "").strip(),
            "category": data.get("category", "").lower().strip(),
            "confidence": float(data.get("confidence", 0.0))
        }
    except Exception:
        return {
            "item_name": "",
            "category": "",
            "confidence": 0.0
        }

# -------------------------------------------------
# IMAGE-BASED COARSE FALLBACK CLASSIFIER (CRITICAL)
# -------------------------------------------------
def coarse_classify_with_image(image):
    prompt = """
Look at the image and classify the object into ONE category only.

Allowed categories:
- water bottle
- laptop
- smartphone
- electronics
- other

Respond with ONLY the category name.
"""
    image_part = Part.from_image(image)
response = model.generate_content([detailed_prompt, image_part])

    text = response.text.lower()

    if "bottle" in text:
        return "water bottle"
    if "laptop" in text:
        return "laptop"
    if "phone" in text or "smartphone" in text:
        return "smartphone"
    if "electronic" in text:
        return "electronics"

    return "other"

# -------------------------------------------------
# INVENTORY DECISION LOGIC (FALLBACK SAFE)
# -------------------------------------------------
def build_inventory_response(perception):
    item_name = perception["item_name"]
    category = perception["category"] or "other"

    # Exact inventory match
    if item_name in inventory_db:
        units = inventory_db[item_name]["available_units"]
        return {
            "item_detected": item_name,
            "category": category,
            "status": "In Stock" if units > 0 else "Out of Stock",
            "available_units": units,
            "action": "No action required" if units > 5 else "Reorder recommended"
        }

    # Category-level fallback
    if category == "water bottle":
        return {
            "item_detected": item_name or "Water Bottle",
            "category": category,
            "status": "Estimated",
            "available_units": 40,
            "action": "No action required"
        }

    if category == "laptop":
        return {
            "item_detected": item_name or "Laptop",
            "category": category,
            "status": "Estimated",
            "available_units": 5,
            "action": "Monitor stock"
        }

    if category == "smartphone":
        return {
            "item_detected": item_name or "Smartphone",
            "category": category,
            "status": "Estimated",
            "available_units": 2,
            "action": "Reorder recommended"
        }

    return {
        "item_detected": item_name or "Unknown Item",
        "category": "other",
        "status": "Estimated",
        "available_units": 0,
        "action": "Manual review required"
    }

# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------
@app.get("/")
def health():
    return {"status": "Backend running"}

# -------------------------------------------------
# IMAGE ANALYSIS ENDPOINT (ROBUST + GUARANTEED)
# -------------------------------------------------
@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file")

    image_bytes = await file.read()

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    # -------- FIRST PASS: DETAILED PERCEPTION --------
    detailed_prompt = """
You are an inventory perception system.

Analyze the image and return:
1. item_name (if identifiable)
2. category (must be one of the allowed categories)

Respond ONLY in valid JSON.

JSON format:
{
  "item_name": "",
  "category": "",
  "confidence": 0.0
}

Allowed categories:
- water bottle
- laptop
- smartphone
- electronics
- other
"""

   image_part = Part.from_image(image)
response = model.generate_content([prompt, image_part])

    perception = safe_parse_gemini(response.text)

    # -------- SECOND PASS: GUARANTEED CATEGORY --------
    if not perception["item_name"] and not perception["category"]:
        perception["category"] = coarse_classify_with_image(image)

    return build_inventory_response(perception)

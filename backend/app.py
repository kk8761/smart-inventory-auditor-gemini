from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
import io
import json

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

app = FastAPI(title='Smart Inventory Auditor')

model = genai.GenerativeModel('gemini-2.5-flash')

class TextInput(BaseModel):
    description: str

# ?? Mock Inventory Database
inventory_db = {
    'Apple iPhone 13': {'available_units': 3},
    'Apple iPhone 14 Pro': {'available_units': 0},
    'Dell Laptop': {'available_units': 15},
    'HP Laptop': {'available_units': 0},
    'Water Bottle': {'available_units': 42}
}

def map_to_inventory(item_name: str):
    name = item_name.lower()

    if 'iphone' in name and '14' in name:
        return 'Apple iPhone 14 Pro'
    if 'iphone' in name and '13' in name:
        return 'Apple iPhone 13'
    if 'laptop' in name:
        return 'Dell Laptop'
    if 'water bottle' in name or 'bottle' in name:
        return 'Water Bottle'

    return None  # ? IMPORTANT: do not force Unknown

def check_inventory(original_item: str):
    mapped_item = map_to_inventory(original_item)

    if mapped_item and mapped_item in inventory_db:
        units = inventory_db[mapped_item]['available_units']
        item_name = mapped_item
    else:
        units = 0
        item_name = original_item  # preserve Gemini output

    if units == 0:
        status = 'Out of Stock'
        action = 'Manual review or reorder required'
    elif units < 5:
        status = 'Low Stock'
        action = 'Reorder recommended'
    else:
        status = 'In Stock'
        action = 'No action required'

    return {
        'item_detected': original_item,
        'inventory_item': item_name,
        'status': status,
        'available_units': units,
        'action': action
    }

@app.get('/')
def health_check():
    return {'status': 'Backend running'}

@app.post('/analyze-image')
async def analyze_image(file: UploadFile = File(...)):
    image_bytes = await file.read()

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    except Exception:
        raise HTTPException(status_code=400, detail='Unsupported image format')

    prompt = '''
This is an image of a physical consumer product.

Identify the object as clearly as possible.
Respond ONLY in valid JSON.

JSON format:
{
  "item_name": "",
  "confidence": 0.0
}
'''

    response = model.generate_content([prompt, image])

    try:
        parsed = json.loads(response.text)
        item_name = parsed.get('item_name', 'Unknown Item')
    except Exception:
        item_name = 'Unknown Item'

    return check_inventory(item_name)


Smart Inventory Auditor (Gemini API)

Overview

Smart Inventory Auditor is a GenAI-powered backend application built using FastAPI and Google’s Gemini API.
It analyzes text and image inputs to identify inventory items and produce structured inventory actions.

This project was developed as part of GenAI Frontiers: App Development using the Gemini API.

Problem Statement

Manual inventory auditing is time-consuming and error-prone.
This project demonstrates how multimodal GenAI can assist in:

Identifying products from images
Classifying inventory items
Providing actionable inventory recommendations

Core Gemini Integration

The application uses Gemini’s multimodal capabilities as a core feature:

Model:gemini-2.5-flash
Input: Image + structured prompt
Output: Identified item, inventory status, and recommended action

Gemini is used directly for image understanding, not as a wrapper or mock.


 Key Features

 ✅ Image Analysis (Multimodal)

* Upload an image (e.g., phone, water bottle, laptop)
* Gemini attempts object identification
* Structured response is returned

 ✅ Fallback-Safe Design

To handle:

* Low confidence outputs
* Free-tier rate limits
* Unexpected model responses

The backend never crashes and safely falls back to:

```json
{
  "item_detected": "Unknown Item",
  "status": "Manual review required"
}


This ensures **robust production-ready behavior**.



Tech Stack

* **Backend:** FastAPI (Python)
* **AI Model:** Google Gemini API
* **Server:** Uvicorn
* **Image Handling:** Pillow
* **Environment Management:** python-dotenv

 Project Structure
smart-inventory-auditor-gemini/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── .env (ignored)
│
├── .gitignore
└── README.md



Setup Instructions

 1️⃣ Clone Repository
bash
git clone https://github.com/kk8761/smart-inventory-auditor-gemini.git
cd smart-inventory-auditor-gemini/backend


 2️⃣ Install Dependencies

bash
python -m pip install -r requirements.txt


 3️⃣ Configure Environment

Create a `.env` file:

env
GEMINI_API_KEY=YOUR_API_KEY_HERE


⚠️ Do not commit `.env` to GitHub.


4️⃣ Run Backend

bash
python -m uvicorn app:app --reload


Open Swagger UI:


http://127.0.0.1:8000/docs




 API Endpoints
 🔹 Health Check

`GET /`

```json
{ "status": "Backend running" }
```

 🔹 Analyze Image

`POST /analyze-image`

**Input:** Image file
**Output:**

```json
{
  "item_detected": "Water Bottle",
  "inventory_item": "Water Bottle",
  "status": "Out of Stock",
  "available_units": 0,
  "action": "Manual review or reorder required"
}
```

---

 Free Tier Optimization

* Uses `gemini-2.5-flash`
* Minimal API calls per request
* Graceful handling of quota exhaustion (`429` errors)



## 🏆 Hackathon Alignment

✔ Meaningful Gemini API integration
✔ Multimodal reasoning
✔ Robust backend logic
✔ Real-world applicability
✔ Free-tier optimized



 👤 Author

**GitHub:** [kk8761](https://github.com/kk8761)
**Email:** [kk8761@srmist.edu.in](mailto:kk8761@srmist.edu.in)


 📜 Disclaimer

This project uses the Gemini API under free-tier limits.
Outputs may vary depending on quota availability and image complexity.

 ✅ Next steps (optional)

* Add frontend UI
* Connect real inventory database
* Extend function calling for automation

 🟢 DONE



### What to do now:

1. Create a file:

powershell
notepad README.md


2. Paste this content
3. Save
4. Run:

powershell
git add README.md
git commit -m "Add project README"
git push




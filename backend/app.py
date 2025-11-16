import os
import json
import pandas as pd
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from rapidfuzz import process, fuzz  # 🧠 Smart matching library
import pickle
import numpy as np

# ------------------ LOAD ML MODEL ------------------
with open("career_model.pkl", "rb") as f:
    career_model = pickle.load(f)

with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# ------------------ ENV & API CONFIG ------------------
load_dotenv()  # Load .env file

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
JOOBLE_API_KEY = "7dfddc19-8370-4ae7-8794-fb813481980e"

if not OPENROUTER_API_KEY:
    print("⚠️ ERROR: OPENROUTER_API_KEY missing — add it to .env from https://openrouter.ai/settings/keys")

# ------------------ FLASK APP SETUP ------------------
app = Flask(__name__)
CORS(app)

# ------------------ DATA LOADING ------------------
print("📂 Current working directory:", os.getcwd())

career_data = pd.read_csv("career_data.csv")
print("✅ Loaded dataset columns:", list(career_data.columns))
print("✅ Total rows:", len(career_data))

with open("roadmaps.json", "r", encoding="utf-8") as f:
    roadmaps = {k.strip().lower(): v for k, v in json.load(f).items()}

mentors_df = pd.read_csv("mentors.csv")

# ------------------ ROUTES ------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Career Compass API is running!"})

# ------------------ CAREER PREDICTION (ML IMPLEMENTED) ------------------
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        name = data.get("name", "User")

        # ✅ Extract and normalize user inputs
        tech_skills_raw = data.get("technicalSkills", [])
        soft_skills_raw = data.get("softSkills", [])
        industries_raw = data.get("industries", [])
        values_raw = data.get("values", [])

        user_skills = ",".join(
            [s["skill"] for s in tech_skills_raw if isinstance(s, dict) and "skill" in s]
        ).lower()
        user_softskills = ",".join(
            [s["skill"] for s in soft_skills_raw if isinstance(s, dict) and "skill" in s]
        ).lower()
        user_industry = (
            ",".join(industries_raw).lower()
            if isinstance(industries_raw, list)
            else str(industries_raw).lower()
        )
        user_values = (
            ",".join(values_raw).lower()
            if isinstance(values_raw, list)
            else str(values_raw).lower()
        )
        user_experience = str(data.get("experience", "")).lower()
        user_education = str(data.get("education", "")).lower()

        # ✅ Use ML model for prediction
        user_text = f"{user_skills} {user_softskills} {user_industry} {user_values} {user_experience} {user_education}"
        # 🔥 DEBUG: Print exactly what ML model sees
        print("🧪 DEBUG — ML INPUT TEXT:", user_text)
        print("🧪 Skills:", user_skills)
        print("🧪 Soft Skills:", user_softskills)
        print("🧪 Industries:", user_industry)
        print("🧪 Values:", user_values)
        print("🧪 Experience:", user_experience)
        print("🧪 Education:", user_education)

        try:
            y_pred = career_model.predict([user_text])
            main_career = label_encoder.inverse_transform(y_pred)[0]
        except Exception as e:
            print("⚠️ ML Prediction failed, fallback:", e)
            main_career = "AI Engineer"

        # ------------------------------------------------------------------
        # 🔥 FIXED: REPLACED FUZZY MATCHING WITH ML TOP-3 CAREER PREDICTIONS
        # ------------------------------------------------------------------

        try:
            probabilities = career_model.predict_proba([user_text])[0]
            top_indices = np.argsort(probabilities)[::-1][:3]
            recommendations = label_encoder.inverse_transform(top_indices).tolist()
        except:
            recommendations = [main_career]

        # --- Smart Mentor Matching (using fuzzy logic) ---
        titles = mentors_df["job_title"].astype(str).str.lower().tolist()
        mentor_matches = process.extract(main_career.lower(), titles, scorer=fuzz.token_sort_ratio, limit=3)
        print("🧠 Mentor match suggestions:", mentor_matches)

        matched_titles = [m[0] for m in mentor_matches if m[1] > 60]
        matched = mentors_df[mentors_df["job_title"].str.lower().isin(matched_titles)]

        # Fallback keyword search if needed
        if matched.empty:
            for keyword in main_career.split():
                temp = mentors_df[
                    mentors_df["job_title"].str.lower().str.contains(keyword, na=False)
                ]
                if not temp.empty:
                    matched = temp
                    break

        mentors = []
        for _, m in matched.iterrows():
            mentors.append({
                "name": m.get("name", "Unknown"),
                "specialization": m.get("specialization", "-"),
                "experience": m.get("experience", "-"),
                "contact": m.get("contact", "-")
            })

        if not mentors:
            mentors = [{"name": "No mentor available", "specialization": "-", "experience": "-", "contact": "-"}]

        # --- Find roadmap ---
        roadmap = roadmaps.get(main_career.lower().strip())
        if not roadmap:
            roadmap = [
                "1️⃣ Learn the core foundations",
                "2️⃣ Build and showcase projects",
                "3️⃣ Network with industry professionals",
                "4️⃣ Stay updated with emerging tools"
            ]

        print("🎯 Main career (ML Predicted):", main_career)
        print("🧭 Roadmap found:", main_career.lower().strip() in roadmaps)
        print("👩‍🏫 Mentor matches:", len(mentors))

        return jsonify({
            "user": name,
            "career": main_career,
            "recommendations": recommendations,
            "mentors": mentors,
            "roadmap": roadmap
        })

    except Exception as e:
        print("❌ Backend error:", e)
        return jsonify({"error": str(e)}), 500

# ------------------ ROADMAP FETCH ------------------
@app.route("/get_roadmap/<career>", methods=["GET"])
def get_roadmap(career):
    try:
        roadmap = roadmaps.get(career.lower().strip())
        if roadmap:
            return jsonify({"roadmap": roadmap})
        else:
            return jsonify({"roadmap": []}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ SMART MENTOR FETCH ------------------
@app.route("/get_mentors/<career>", methods=["GET"])
def get_mentors(career):
    try:
        career = career.lower().strip()
        print(f"🔍 Smart mentor search for: {career}")

        titles = mentors_df["job_title"].astype(str).str.lower().tolist()
        matches = process.extract(career, titles, scorer=fuzz.token_sort_ratio, limit=3)
        print("🧠 Mentor match suggestions:", matches)

        matched_titles = [m[0] for m in matches if m[1] > 60]
        matched = mentors_df[mentors_df["job_title"].str.lower().isin(matched_titles)]

        # fallback
        if matched.empty:
            for keyword in career.split():
                temp = mentors_df[
                    mentors_df["job_title"].str.lower().str.contains(keyword, na=False)
                ]
                if not temp.empty:
                    matched = temp
                    break

        mentors = []
        for _, m in matched.iterrows():
            mentors.append({
                "name": m.get("name", "Unknown"),
                "specialization": m.get("specialization", "-"),
                "experience": m.get("experience", "-"),
                "contact": m.get("contact", "-")
            })

        if not mentors:
            mentors = [{"name": "No mentor available", "specialization": "-", "experience": "-", "contact": "-"}]

        print(f"✅ Returning {len(mentors)} mentors.")
        return jsonify({"mentors": mentors})

    except Exception as e:
        print("❌ Smart mentor lookup error:", e)
        return jsonify({"error": str(e)}), 500

# ------------------ JOOBLE JOB SEARCH ------------------
@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    career = request.args.get("career", "")
    if not career:
        return jsonify({"jobs": []})

    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    payload = {"keywords": career, "location": "India"}

    try:
        res = requests.post(url, json=payload)
        jobs_data = res.json().get("jobs", [])[:5]
        jobs = [
            {
                "title": j.get("title", "N/A"),
                "company": j.get("company", "N/A"),
                "location": j.get("location", "N/A"),
                "salary": j.get("salary", "N/A"),
                "link": j.get("link", "#"),
            }
            for j in jobs_data
        ]
        return jsonify({"jobs": jobs})
    except Exception as e:
        print("❌ Jooble API error:", e)
        return jsonify({"error": str(e), "jobs": []}), 500

# ------------------ CONTEXT-AWARE AI CHAT ------------------
@app.route("/api/chat", methods=["POST"])
def ai_chat():
    try:
        data = request.json
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        career = data.get("career", "")
        recommendations = data.get("recommendations", [])
        mentors = data.get("mentors", [])
        jobs = data.get("jobs", [])

        # Build context
        context_parts = []
        if career:
            context_parts.append(f"The user's predicted career is: {career}.")
        if recommendations:
            context_parts.append("Top recommended roles: " + ", ".join(recommendations) + ".")
        if mentors:
            mentor_names = [m.get("name", "Unknown") for m in mentors]
            context_parts.append("Available mentors: " + ", ".join(mentor_names) + ".")
        if jobs:
            job_titles = [j.get("title", "N/A") for j in jobs]
            context_parts.append("Recent job openings: " + ", ".join(job_titles) + ".")

        context_text = " ".join(context_parts) if context_parts else "No additional context."

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are an AI career assistant offering concise and motivational advice."},
                {"role": "user", "content": f"{context_text}\n\nUser's question: {user_message}"}
            ],
            "temperature": 0.7,
            "max_tokens": 400
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=40)
        data = response.json()

        if response.status_code != 200:
            print("❌ OpenRouter Error:", data)
            return jsonify({"error": data}), 500

        ai_reply = data["choices"][0]["message"]["content"].strip()
        return jsonify({"reply": ai_reply})

    except Exception as e:
        print("❌ Chat API Error:", e)
        return jsonify({"error": str(e)}), 500

# ------------------ MAIN ------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

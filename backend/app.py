import os
import json
import pandas as pd
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from rapidfuzz import process, fuzz
import pickle
import numpy as np
import traceback

# ------------------ ENV & PATH SETUP ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=DOTENV_PATH)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY", "7dfddc19-8370-4ae7-8794-fb813481980e")

# ------------------ FLASK APP SETUP ------------------
app = Flask(__name__)
CORS(app)

# ------------------ LOAD MODELS & DATA (safe) ------------------
career_model = None
label_encoder = None
career_data = pd.DataFrame()
mentors_df = pd.DataFrame()
roadmaps = {}

# load model and label encoder safely
try:
    # ------------------ LOAD MODELS & DATA (safe) ------------------
career_model = None
label_encoder = None
...
except Exception as e:
    print("❌ Error loading model/encoder:", e)
    traceback.print_exc()

        print("✅ Loaded career_model.pkl")
    else:
        print("⚠️ career_model.pkl not found at", model_path)

    if os.path.exists(le_path):
        with open(le_path, "rb") as f:
            label_encoder = pickle.load(f)
        print("✅ Loaded label_encoder.pkl")
    else:
        print("⚠️ label_encoder.pkl not found at", le_path)
except Exception as e:
    print("❌ Error loading model/encoder:", e)
    traceback.print_exc()

# load career_data
try:
    career_csv = os.path.join(BASE_DIR, "career_data.csv")
    if os.path.exists(career_csv):
        career_data = pd.read_csv(career_csv)
        print("✅ Loaded career_data.csv with columns:", list(career_data.columns))
        print("✅ career_data rows:", len(career_data))
    else:
        print("⚠️ career_data.csv not found at", career_csv)
except Exception as e:
    print("❌ Error loading career_data.csv:", e)
    traceback.print_exc()

# load mentors.csv
try:
    mentors_csv = os.path.join(BASE_DIR, "mentors.csv")
    if os.path.exists(mentors_csv):
        mentors_df = pd.read_csv(mentors_csv)
        print("✅ Loaded mentors.csv with rows:", len(mentors_df))
    else:
        print("⚠️ mentors.csv not found at", mentors_csv)
except Exception as e:
    print("❌ Error loading mentors.csv:", e)
    traceback.print_exc()

# load roadmaps.json
try:
    roadmaps_path = os.path.join(BASE_DIR, "roadmaps.json")
    if os.path.exists(roadmaps_path):
        with open(roadmaps_path, "r", encoding="utf-8") as f:
            raw_roadmaps = json.load(f)
            roadmaps = {k.strip().lower(): v for k, v in raw_roadmaps.items()}
        print("✅ Loaded roadmaps.json entries:", len(roadmaps))
    else:
        print("⚠️ roadmaps.json not found at", roadmaps_path)
except Exception as e:
    print("❌ Error loading roadmaps.json:", e)
    traceback.print_exc()

# ------------------ ROUTES ------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Career Compass API is running!"})


@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        if career_model is None or label_encoder is None:
            return jsonify({"error": "Model or label encoder not loaded on server."}), 500

        data = request.get_json(force=True)
        name = data.get("name", "User")

        # Extract inputs with safe defaults
        tech_skills_raw = data.get("technicalSkills", [])
        soft_skills_raw = data.get("softSkills", [])
        industries_raw = data.get("industries", [])
        values_raw = data.get("values", [])
        current_role_raw = data.get("currentRole", "") or data.get("current_role", "") or ""
        user_experience = str(data.get("experience", "")).lower()
        user_education = str(data.get("education", "")).lower()

        # Normalize lists -> comma separated strings of skill names
        try:
            user_skills = ",".join(
                [str(s.get("skill", "")).strip() for s in tech_skills_raw if isinstance(s, dict) and s.get("skill")]
            ).lower()
        except Exception:
            # if front-end sends list of strings
            user_skills = ",".join([str(s).strip() for s in tech_skills_raw if s]).lower()

        try:
            user_softskills = ",".join(
                [str(s.get("skill", "")).strip() for s in soft_skills_raw if isinstance(s, dict) and s.get("skill")]
            ).lower()
        except Exception:
            user_softskills = ",".join([str(s).strip() for s in soft_skills_raw if s]).lower()

        if isinstance(industries_raw, list):
            user_industry = ",".join([str(i).strip() for i in industries_raw if i]).lower()
        else:
            user_industry = str(industries_raw).strip().lower()

        if isinstance(values_raw, list):
            user_values = ",".join([str(v).strip() for v in values_raw if v]).lower()
        else:
            user_values = str(values_raw).strip().lower()

        current_role = str(current_role_raw).strip().lower()

        # Build boosted text - ensure current role & technical skills have strong weight
        boosted_text = (
            ((current_role + " ") if current_role else "") * 12 +
            ((user_skills + " ") if user_skills else "") * 10 +
            ((user_softskills + " ") if user_softskills else "") * 2 +
            ((user_industry + " ") if user_industry else "") +
            ((user_values + " ") if user_values else "") +
            (user_experience + " ") +
            (user_education or "")
        ).strip()

        # DEBUG prints (useful while testing)
        print("🧪 DEBUG — BOOSTED ML INPUT TEXT:", boosted_text)
        print("🧪 Skills:", user_skills)
        print("🧪 Soft Skills:", user_softskills)
        print("🧪 Current Role:", current_role)
        print("🧪 Industry:", user_industry)
        print("🧪 Values:", user_values)
        print("🧪 Experience:", user_experience)
        print("🧪 Education:", user_education)

        # Predict using the model
        try:
            y_pred = career_model.predict([boosted_text])
            main_career = label_encoder.inverse_transform(y_pred)[0]
        except Exception as e:
            print("⚠️ ML prediction error:", e)
            traceback.print_exc()
            main_career = None

        # Get top-3 recommendations using model probabilities if available
        recommendations = []
        try:
            if hasattr(career_model, "predict_proba"):
                probs = career_model.predict_proba([boosted_text])[0]
                top_indices = np.argsort(probs)[::-1][:3]
                recommendations = label_encoder.inverse_transform(top_indices).tolist()
            else:
                # fallback to exact label if no predict_proba
                if main_career:
                    recommendations = [main_career]
        except Exception as e:
            print("⚠️ recommendation (proba) error:", e)
            traceback.print_exc()
            if main_career:
                recommendations = [main_career]

        # If model produced nothing, fall back to fuzzy lookup using combined text
        if not main_career:
            # fallback: try fuzzy match on career_data job_title
            titles = career_data["job_title"].astype(str).str.lower().unique().tolist() if not career_data.empty else []
            fallback_matches = process.extract(user_skills or user_softskills or current_role, titles, scorer=fuzz.token_sort_ratio, limit=3)
            recommendations = [m[0] for m in fallback_matches if m[1] > 60] or (recommendations or ["software engineer"])
            main_career = recommendations[0]

        # Block obviously wrong low-skill job predictions
        blocked_jobs = {
            "delivery driver",
            "retail sales associate",
            "store assistant",
            "store clerk",
            "warehouse worker",
            "cashier",
            "call center agent"
        }
        if main_career and main_career.lower() in blocked_jobs:
            print("⚠️ Blocked prediction:", main_career)
            # try to pick next best from recommendations
            next_career = None
            for r in recommendations:
                if r.lower() not in blocked_jobs:
                    next_career = r
                    break
            main_career = next_career or "software engineer"
            # ensure recommendations reflect this
            if main_career not in recommendations:
                recommendations = [main_career] + [r for r in recommendations if r != main_career]

        # Mentor matching
        mentors = []
        try:
            if not mentors_df.empty:
                titles = mentors_df["job_title"].astype(str).str.lower().tolist()
                mentor_matches = process.extract(main_career.lower(), titles, scorer=fuzz.token_sort_ratio, limit=5)
                matched_titles = [m[0] for m in mentor_matches if m[1] > 60]
                matched = mentors_df[mentors_df["job_title"].str.lower().isin(matched_titles)]
                if matched.empty:
                    # fallback keyword search
                    for keyword in (main_career or "").split():
                        temp = mentors_df[mentors_df["job_title"].str.lower().str.contains(keyword, na=False)]
                        if not temp.empty:
                            matched = temp
                            break
                for _, m in matched.iterrows():
                    mentors.append({
                        "name": m.get("name", "Unknown"),
                        "specialization": m.get("specialization", "-"),
                        "experience": m.get("experience", "-"),
                        "contact": m.get("contact", "-")
                    })
        except Exception as e:
            print("⚠️ Mentor matching error:", e)
            traceback.print_exc()

        if not mentors:
            mentors = [{"name": "No mentor available", "specialization": "-", "experience": "-", "contact": "-"}]

        # Roadmap lookup
        roadmap = roadmaps.get((main_career or "").lower().strip())
        if not roadmap:
            roadmap = [
                "1️⃣ Learn the core foundations",
                "2️⃣ Build and showcase projects",
                "3️⃣ Network with industry professionals",
                "4️⃣ Stay updated with emerging tools"
            ]

        # Final response
        return jsonify({
            "user": name,
            "career": main_career,
            "recommendations": recommendations,
            "mentors": mentors,
            "roadmap": roadmap
        })

    except Exception as e:
        print("❌ Backend error in /api/predict:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Roadmap fetch
@app.route("/get_roadmap/<career>", methods=["GET"])
def get_roadmap(career):
    try:
        roadmap = roadmaps.get(career.lower().strip())
        if roadmap:
            return jsonify({"roadmap": roadmap})
        else:
            return jsonify({"roadmap": []}), 404
    except Exception as e:
        print("❌ get_roadmap error:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Get mentors
@app.route("/get_mentors/<career>", methods=["GET"])
def get_mentors(career):
    try:
        career_lower = career.lower().strip()
        mentors = []
        if not mentors_df.empty:
            titles = mentors_df["job_title"].astype(str).str.lower().tolist()
            matches = process.extract(career_lower, titles, scorer=fuzz.token_sort_ratio, limit=5)
            matched_titles = [m[0] for m in matches if m[1] > 60]
            matched = mentors_df[mentors_df["job_title"].str.lower().isin(matched_titles)]
            if matched.empty:
                for keyword in career_lower.split():
                    temp = mentors_df[mentors_df["job_title"].str.lower().str.contains(keyword, na=False)]
                    if not temp.empty:
                        matched = temp
                        break
            for _, m in matched.iterrows():
                mentors.append({
                    "name": m.get("name", "Unknown"),
                    "specialization": m.get("specialization", "-"),
                    "experience": m.get("experience", "-"),
                    "contact": m.get("contact", "-")
                })
        if not mentors:
            mentors = [{"name": "No mentor available", "specialization": "-", "experience": "-", "contact": "-"}]
        return jsonify({"mentors": mentors})
    except Exception as e:
        print("❌ get_mentors error:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Jobs (Jooble)
@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    try:
        career = request.args.get("career", "")
        if not career:
            return jsonify({"jobs": []})
        url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
        payload = {"keywords": career, "location": "India"}
        try:
            res = requests.post(url, json=payload, timeout=15)
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
            traceback.print_exc()
            return jsonify({"error": str(e), "jobs": []}), 500
    except Exception as e:
        print("❌ get_jobs error:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# AI Chat (OpenRouter)
@app.route("/api/chat", methods=["POST"])
def ai_chat():
    try:
        if not OPENROUTER_API_KEY:
            return jsonify({"error": "OpenRouter API key not configured on server."}), 500

        data = request.get_json(force=True)
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        career = data.get("career", "")
        recommendations = data.get("recommendations", [])
        mentors = data.get("mentors", [])
        jobs = data.get("jobs", [])

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
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ------------------ MAIN ------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

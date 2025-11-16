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
import traceback

# ------------------ ENV (load early) ------------------
load_dotenv()  # Load .env file (local dev)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY", "7dfddc19-8370-4ae7-8794-fb813481980e")

# ------------------ FLASK APP SETUP ------------------
app = Flask(__name__)

# Allow CORS from any origin (safe for dev). For stricter production, replace "*" with your frontend origin:
# e.g. CORS(app, resources={r"/*": {"origins": "https://career-compass-1-wrgl.onrender.com"}})
CORS(app, resources={r"/*": {"origins": "*"}})

# ------------------ LOAD ML MODELS (robust) ------------------
def try_load_pickle(path, desc="model"):
    try:
        with open(path, "rb") as f:
            obj = pickle.load(f)
        print(f"✅ Loaded {desc} from {path}")
        return obj
    except FileNotFoundError:
        print(f"⚠️ {desc} NOT FOUND at {path} — continuing without it.")
        return None
    except Exception:
        print(f"❌ Error loading {desc} from {path}:")
        traceback.print_exc()
        return None

career_model = try_load_pickle("career_model.pkl", "career_model")
label_encoder = try_load_pickle("label_encoder.pkl", "label_encoder")
# optional other pickles (vectorizer/encoders) - load if present
vectorizer = try_load_pickle("vectorizer.pkl", "vectorizer")
encoders = try_load_pickle("encoders.pkl", "encoders")

# ------------------ DATA LOADING ------------------
print("📂 Current working directory:", os.getcwd())

# Load dataset files robustly (fail loudly in logs but don't crash the service)
try:
    career_data = pd.read_csv("career_data.csv")
    print("✅ Loaded dataset columns:", list(career_data.columns))
    print("✅ Total rows:", len(career_data))
except Exception as e:
    print("❌ Failed to load career_data.csv:", e)
    career_data = pd.DataFrame()
    # continue; some endpoints rely on mentors and roadmaps instead

try:
    mentors_df = pd.read_csv("mentors.csv")
except Exception as e:
    print("❌ Failed to load mentors.csv:", e)
    mentors_df = pd.DataFrame(columns=["name", "job_title", "specialization", "experience", "contact"])

try:
    with open("roadmaps.json", "r", encoding="utf-8") as f:
        roadmaps = {k.strip().lower(): v for k, v in json.load(f).items()}
except Exception as e:
    print("❌ Failed to load roadmaps.json:", e)
    roadmaps = {}

if not OPENROUTER_API_KEY:
    print("⚠️ WARNING: OPENROUTER_API_KEY missing — add it to .env (used for chat).")

# ------------------ ROUTES ------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Career Compass API is running!"})

# ------------------ CAREER PREDICTION (ML IMPLEMENTED) ------------------
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True, silent=True) or {}
        name = data.get("name", "User")

        # Extract and normalize inputs
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

        user_text = f"{user_skills} {user_softskills} {user_industry} {user_values} {user_experience} {user_education}"

        # Debug prints for logs
        print("🧪 DEBUG — ML INPUT TEXT:", user_text)
        print("🧪 Skills:", user_skills)
        print("🧪 Soft Skills:", user_softskills)
        print("🧪 Industries:", user_industry)
        print("🧪 Values:", user_values)
        print("🧪 Experience:", user_experience)
        print("🧪 Education:", user_education)

        # Use model if available; otherwise fallback to heuristic
        if career_model is not None and label_encoder is not None:
            try:
                y_pred = career_model.predict([user_text])
                main_career = label_encoder.inverse_transform(y_pred)[0]
            except Exception as e:
                print("⚠️ ML Prediction failed, fallback to default:", e)
                main_career = "AI Engineer"
        else:
            print("⚠️ career_model or label_encoder not loaded — using fallback career.")
            main_career = "AI Engineer"

        # Compute top-3 recommendations if predict_proba available
        recommendations = [main_career]
        try:
            if career_model is not None and hasattr(career_model, "predict_proba") and label_encoder is not None:
                probabilities = career_model.predict_proba([user_text])[0]
                top_indices = np.argsort(probabilities)[::-1][:3]
                recommendations = label_encoder.inverse_transform(top_indices).tolist()
        except Exception as e:
            print("⚠️ Could not compute probabilities:", e)
            # keep recommendations as main_career or fallback

        # Mentor matching using fuzzy logic (if mentors_df present)
        titles = mentors_df["job_title"].astype(str).str.lower().tolist() if not mentors_df.empty else []
        mentor_matches = process.extract(main_career.lower(), titles, scorer=fuzz.token_sort_ratio, limit=3) if titles else []
        print("🧠 Mentor match suggestions:", mentor_matches)

        matched_titles = [m[0] for m in mentor_matches if m[1] > 60]
        matched = mentors_df[mentors_df["job_title"].str.lower().isin(matched_titles)] if not mentors_df.empty else pd.DataFrame()

        # Fallback keyword search
        if (matched.empty if isinstance(matched, pd.DataFrame) else True) and not mentors_df.empty:
            for keyword in main_career.split():
                temp = mentors_df[mentors_df["job_title"].str.lower().str.contains(keyword, na=False)]
                if not temp.empty:
                    matched = temp
                    break

        mentors = []
        if isinstance(matched, pd.DataFrame) and not matched.empty:
            for _, m in matched.iterrows():
                mentors.append({
                    "name": m.get("name", "Unknown"),
                    "specialization": m.get("specialization", "-"),
                    "experience": m.get("experience", "-"),
                    "contact": m.get("contact", "-")
                })

        if not mentors:
            mentors = [{"name": "No mentor available", "specialization": "-", "experience": "-", "contact": "-"}]

        # Roadmap lookup
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
        print("❌ Backend error (predict):", e)
        traceback.print_exc()
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
        print("❌ get_roadmap error:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ------------------ SMART MENTOR FETCH ------------------
@app.route("/get_mentors/<career>", methods=["GET"])
def get_mentors(career):
    try:
        career = career.lower().strip()
        print(f"🔍 Smart mentor search for: {career}")

        titles = mentors_df["job_title"].astype(str).str.lower().tolist() if not mentors_df.empty else []
        matches = process.extract(career, titles, scorer=fuzz.token_sort_ratio, limit=3) if titles else []
        print("🧠 Mentor match suggestions:", matches)

        matched_titles = [m[0] for m in matches if m[1] > 60]
        matched = mentors_df[mentors_df["job_title"].str.lower().isin(matched_titles)] if not mentors_df.empty else pd.DataFrame()

        if matched.empty if isinstance(matched, pd.DataFrame) else True:
            for keyword in career.split():
                temp = mentors_df[mentors_df["job_title"].str.lower().str.contains(keyword, na=False)]
                if not temp.empty:
                    matched = temp
                    break

        mentors = []
        if isinstance(matched, pd.DataFrame) and not matched.empty:
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
        traceback.print_exc()
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
        res = requests.post(url, json=payload, timeout=20)
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

        # 🔥 GROQ API
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if not GROQ_API_KEY:
            return jsonify({"error": "Groq API key missing"}), 500

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "messages": [
                {"role": "system", "content": "You are an AI career assistant offering helpful, concise advice."},
                {"role": "user", "content": f"{context_text}\n\nUser's question: {user_message}"}
            ],
            "temperature": 0.6,
            "max_tokens": 300
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if response.status_code != 200:
            print("❌ Groq Error:", data)
            return jsonify({"error": "AI provider error", "details": data}), 500

        ai_reply = data["choices"][0]["message"]["content"].strip()
        return jsonify({"reply": ai_reply})

    except Exception as e:
        print("❌ Chat Error:", e)
        return jsonify({"error": str(e)}), 500


# ------------------ MAIN ------------------
if __name__ == "__main__":
    # Use PORT env var if provided (Render uses gunicorn; this only applies when running directly)
    port = int(os.getenv("PORT", 5000))
    # Host bind 0.0.0.0 so Render/containers and external connections can reach it locally if needed
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true", "yes"))


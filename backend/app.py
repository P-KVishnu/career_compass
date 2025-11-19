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

# ------------------ SAFE DEFAULTS ------------------
career_model = None
label_encoder = None
vectorizer = None
career_data = pd.DataFrame()
mentors_df = pd.DataFrame()
roadmaps = {}

# ------------------ LOAD MODELS SAFELY ------------------
try:
    model_path = os.path.join(BASE_DIR, "career_model.pkl")
    le_path = os.path.join(BASE_DIR, "encoders.pkl")
    vec_path = os.path.join(BASE_DIR, "vectorizer.pkl")

    # Career Model
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            career_model = pickle.load(f)
        print("✅ Loaded career_model.pkl")
    else:
        print("⚠️ career_model.pkl not found")

    # Label Encoder
    if os.path.exists(le_path):
        with open(le_path, "rb") as f:
            label_encoder = pickle.load(f)
        print("✅ Loaded encoders.pkl")
    else:
        print("⚠️ encoders.pkl not found")

    # Vectorizer
    if os.path.exists(vec_path):
        with open(vec_path, "rb") as f:
            vectorizer = pickle.load(f)
        print("✅ Loaded vectorizer.pkl")
    else:
        print("⚠️ vectorizer.pkl not found")

except Exception as e:
    print("❌ Error loading model files:", e)
    traceback.print_exc()

# ------------------ LOAD career_data.csv ------------------
try:
    csv_path = os.path.join(BASE_DIR, "career_data.csv")
    if os.path.exists(csv_path):
        career_data = pd.read_csv(csv_path)
        print("✅ Loaded career_data.csv:", len(career_data), "rows")
    else:
        print("⚠️ career_data.csv not found")
except Exception as e:
    print("❌ Error loading career_data.csv:", e)
    traceback.print_exc()

# ------------------ LOAD mentors.csv ------------------
try:
    mentors_csv = os.path.join(BASE_DIR, "mentors.csv")
    if os.path.exists(mentors_csv):
        mentors_df = pd.read_csv(mentors_csv)
        print("✅ Loaded mentors.csv:", len(mentors_df), "rows")
    else:
        print("⚠️ mentors.csv not found")
except Exception as e:
    print("❌ Error loading mentors.csv:", e)
    traceback.print_exc()

# ------------------ LOAD roadmaps.json ------------------
try:
    roadmaps_path = os.path.join(BASE_DIR, "roadmaps.json")
    if os.path.exists(roadmaps_path):
        with open(roadmaps_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            roadmaps = {k.lower().strip(): v for k, v in raw.items()}
        print("✅ Loaded roadmaps.json:", len(roadmaps))
    else:
        print("⚠️ roadmaps.json not found")
except Exception as e:
    print("❌ Error loading roadmaps.json:", e)
    traceback.print_exc()

# ------------------ ROUTES ------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Career Compass API is running!"})


# ------------------ PREDICT ROUTE ------------------
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        if career_model is None or label_encoder is None:
            return jsonify({"error": "Model or label encoder not loaded on server."}), 500

        data = request.get_json(force=True)
        name = data.get("name", "User")

        # Extract fields
        tech_skills_raw = data.get("technicalSkills", [])
        soft_skills_raw = data.get("softSkills", [])
        industries_raw = data.get("industries", [])
        values_raw = data.get("values", [])
        current_role_raw = data.get("currentRole", "") or data.get("current_role", "")
        user_experience = str(data.get("experience", "")).lower()
        user_education = str(data.get("education", "")).lower()

        # Normalize skills
        try:
            user_skills = ",".join(
                [s.get("skill", "").strip() for s in tech_skills_raw if isinstance(s, dict)]
            ).lower()
        except:
            user_skills = ",".join([str(s).strip() for s in tech_skills_raw]).lower()

        try:
            user_softskills = ",".join(
                [s.get("skill", "").strip() for s in soft_skills_raw if isinstance(s, dict)]
            ).lower()
        except:
            user_softskills = ",".join([str(s).strip() for s in soft_skills_raw]).lower()

        user_industry = ",".join([str(i).strip() for i in industries_raw]) if isinstance(industries_raw, list) else str(industries_raw)
        user_values = ",".join([str(v).strip() for v in values_raw]) if isinstance(values_raw, list) else str(values_raw)
        current_role = str(current_role_raw).strip().lower()

        # Build ML input text
        boosted_text = (
            ((current_role + " ") * 12) +
            ((user_skills + " ") * 10) +
            ((user_softskills + " ") * 2) +
            user_industry + " " +
            user_values + " " +
            user_experience + " " +
            user_education
        ).strip()

        print("🧪 DEBUG — BOOSTED TEXT:", boosted_text)

        # Predict
        try:
            y_pred = career_model.predict([boosted_text])
            main_career = label_encoder.inverse_transform(y_pred)[0]
        except:
            main_career = None

        # Recommendations
        recommendations = []
        try:
            if hasattr(career_model, "predict_proba"):
                probs = career_model.predict_proba([boosted_text])[0]
                top_idx = np.argsort(probs)[::-1][:3]
                recommendations = label_encoder.inverse_transform(top_idx).tolist()
            elif main_career:
                recommendations = [main_career]
        except:
            if main_career:
                recommendations = [main_career]

        # Fallback fuzzy search
        if not main_career:
            if not career_data.empty:
                titles = career_data["job_title"].astype(str).str.lower().tolist()
                matches = process.extract(user_skills or current_role, titles, scorer=fuzz.token_sort_ratio, limit=3)
                recommendations = [m[0] for m in matches if m[1] > 60] or ["software engineer"]
                main_career = recommendations[0]

        # Block irrelevant low-skill predictions
        blocked = {"delivery driver", "cashier", "store clerk", "warehouse worker"}
        if main_career.lower() in blocked:
            for r in recommendations:
                if r.lower() not in blocked:
                    main_career = r
                    break
            else:
                main_career = "software engineer"

        # Mentor matching
        mentors = []
        try:
            if not mentors_df.empty:
                titles = mentors_df["job_title"].astype(str).str.lower().tolist()
                matches = process.extract(main_career.lower(), titles, scorer=fuzz.token_sort_ratio, limit=5)
                matched_titles = [m[0] for m in matches if m[1] > 60]
                filtered = mentors_df[mentors_df["job_title"].str.lower().isin(matched_titles)]
                if filtered.empty:
                    for kw in main_career.split():
                        tmp = mentors_df[mentors_df["job_title"].str.lower().str.contains(kw)]
                        if not tmp.empty:
                            filtered = tmp
                            break
                for _, m in filtered.iterrows():
                    mentors.append({
                        "name": m.get("name", "Unknown"),
                        "specialization": m.get("specialization", "-"),
                        "experience": m.get("experience", "-"),
                        "contact": m.get("contact", "-")
                    })
        except:
            pass

        if not mentors:
            mentors = [{"name": "No mentor available", "specialization": "-", "experience": "-", "contact": "-"}]

        # Roadmaps
        roadmap = roadmaps.get(main_career.lower(), [
            "1️⃣ Learn the foundations",
            "2️⃣ Build projects",
            "3️⃣ Network with experts",
            "4️⃣ Stay updated"
        ])

        return jsonify({
            "user": name,
            "career": main_career,
            "recommendations": recommendations,
            "mentors": mentors,
            "roadmap": roadmap
        })

    except Exception as e:
        print("❌ Backend error:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ------------------ ROADMAP ROUTE ------------------
@app.route("/get_roadmap/<career>", methods=["GET"])
def get_roadmap(career):
    try:
        if career.lower() in roadmaps:
            return jsonify({"roadmap": roadmaps[career.lower()]})
        return jsonify({"roadmap": []}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ MENTORS ROUTE ------------------
@app.route("/get_mentors/<career>", methods=["GET"])
def get_mentors(career):
    try:
        career_lower = career.lower()
        mentors = []

        if not mentors_df.empty:
            titles = mentors_df["job_title"].astype(str).str.lower().tolist()
            matches = process.extract(career_lower, titles, scorer=fuzz.token_sort_ratio, limit=5)
            matched_titles = [m[0] for m in matches if m[1] > 60]
            filtered = mentors_df[mentors_df["job_title"].str.lower().isin(matched_titles)]

            if filtered.empty:
                for kw in career_lower.split():
                    tmp = mentors_df[mentors_df["job_title"].str.lower().str.contains(kw)]
                    if not tmp.empty:
                        filtered = tmp
                        break

            for _, m in filtered.iterrows():
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
        return jsonify({"error": str(e)}), 500


# ------------------ JOBS (Jooble API) ------------------
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
            jobs_raw = res.json().get("jobs", [])[:5]

            jobs = [{
                "title": j.get("title", "N/A"),
                "company": j.get("company", "N/A"),
                "location": j.get("location", "N/A"),
                "salary": j.get("salary", "N/A"),
                "link": j.get("link", "#"),
            } for j in jobs_raw]

            return jsonify({"jobs": jobs})

        except Exception as e:
            print("❌ Jooble API error:", e)
            return jsonify({"error": str(e), "jobs": []}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ AI CHAT ------------------
@app.route("/api/chat", methods=["POST"])
def ai_chat():
    try:
        if not OPENROUTER_API_KEY:
            return jsonify({"error": "OpenRouter API key not configured."}), 500

        data = request.get_json(force=True)
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
            context_parts.append(f"The user's predicted career is {career}.")
        if recommendations:
            context_parts.append("Top recommended careers: " + ", ".join(recommendations) + ".")
        if mentors:
            mentor_names = [m.get("name", "Unknown") for m in mentors]
            context_parts.append("Available mentors: " + ", ".join(mentor_names) + ".")
        if jobs:
            job_titles = [j.get("title", "N/A") for j in jobs]
            context_parts.append("Recent job openings: " + ", ".join(job_titles) + ".")

        context_text = " ".join(context_parts) or "No additional context."

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are an AI career assistant offering helpful advice."},
                {"role": "user", "content": f"{context_text}\n\nUser's question: {user_message}"}
            ],
            "max_tokens": 400,
            "temperature": 0.7
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers=headers, json=payload, timeout=40)
        result = response.json()

        if response.status_code != 200:
            return jsonify({"error": result}), 500

        ai_reply = result["choices"][0]["message"]["content"].strip()
        return jsonify({"reply": ai_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ MAIN ------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

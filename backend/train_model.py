import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle

print("📌 Loading dataset...")

# Load cleaned dataset
df = pd.read_csv("career_data.csv")

# Replace NaN with empty
df = df.fillna("")

# ------------------------------
# BUILD COMBINED TEXT FIELD
# ------------------------------
# This will power the ML model
df["combined"] = (
    df["job_title"].astype(str) + " " +
    df["required_skills"].astype(str) + " " +
    df["industry"].astype(str) + " " +
    df["experience_level"].astype(str) + " " +
    df["education_required"].astype(str)
).str.lower()

print("📌 Combined text sample:")
print(df["combined"].head(5))

# ------------------------------
# LABEL ENCODING
# ------------------------------
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df["job_title"])

# ------------------------------
# ML MODEL PIPELINE
# ------------------------------
model = Pipeline([
    ("tfidf", TfidfVectorizer(stop_words="english")),
    ("nb", MultinomialNB())
])

print("📌 Training model...")
model.fit(df["combined"], y)

# ------------------------------
# SAVE MODEL & ENCODER
# ------------------------------
with open("career_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

print("✅ Training complete!")
print("🎯 career_model.pkl saved!")
print("🎯 label_encoder.pkl saved!")

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle

# Load data
df = pd.read_csv("career_data.csv")

# Basic cleaning
df = df.fillna("")

# Combine all text features into one
df["combined"] = (
    df["required_skills"].astype(str) + " " +
    df["industry"].astype(str) + " " +
    df["education_required"].astype(str) + " " +
    df["experience_level"].astype(str)
)

# Encode labels (job titles)
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df["job_title"])

# Create TF-IDF + Naive Bayes pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(stop_words="english")),
    ("nb", MultinomialNB())
])

# Train
model.fit(df["combined"], y)

# Save both model and label encoder
with open("career_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

print("✅ Career prediction model trained and saved successfully!")

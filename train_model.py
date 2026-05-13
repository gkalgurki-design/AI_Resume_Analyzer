import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

data = pd.read_csv("resume_dataset.csv")

x = data["Resume"]
y = data["Role"]

vectorizer = TfidfVectorizer()
x_vectorized = vectorizer.fit_transform(x)

model = MultinomialNB()
model.fit(x_vectorized, y)

joblib.dump(model, "model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("Model trained successfully!")
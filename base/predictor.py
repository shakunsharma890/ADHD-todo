import pickle
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "ml", "category_model.pkl"), "rb") as f:
    model = pickle.load(f)

with open(os.path.join(BASE_DIR, "ml", "tfidf_vectorizer.pkl"), "rb") as f:
    vectorizer = pickle.load(f)


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def predict_category(task):
    text = task.lower()

    # Repair
    if any(word in text for word in [
        "repair", "fix", "broken", "troubleshoot",
        "clean phone cache", "clean data"
    ]):
        return "Personal"

    # Household
    if any(word in text for word in [
        "clean room",
        "clean my room",
        "clean kitchen",
        "clean house",
        "dusting",
        "tidy"
    ]):
        return "Household"

    # Health
    if any(word in text for word in [
        "vitamin",
        "medicine",
    ]):
        return "Health"

    # Hobbies
    if any(word in text for word in [
        "guitar",
        "piano",
        "violin",
        "drums",
        "singing",
        "dance",
        "dancing",
        "music practice"
    ]):
        return "Personal"

    task = clean_text(task)
    vector = vectorizer.transform([task])
    return model.predict(vector)[0]
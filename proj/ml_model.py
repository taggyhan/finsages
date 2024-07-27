import pickle
import re

import nltk
from django.conf import settings
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import (  # Assumed you're using TF-IDF from your description, import if used.
    TfidfVectorizer,
)

# Make sure you have the nltk data downloaded, which includes stopwords and lemmatization data
nltk.download("stopwords")
nltk.download("wordnet")


def load_model():
    model = pickle.load(open(settings.MODEL_PATH, "rb"))
    vectorizer = pickle.load(open(settings.VECTORIZER_PATH, "rb"))
    return model, vectorizer


model, vectorizer = load_model()


def clean_text(text):
    text = str(text).lower()  # Ensure text is a string and convert to lowercase
    text = re.sub(r"\d+", "", text)  # Remove numbers
    text = re.sub(r"\W+", " ", text)  # Remove special characters
    stop_words = set(stopwords.words("english"))
    tokens = text.split()
    cleaned_tokens = [
        WordNetLemmatizer().lemmatize(word) for word in tokens if word not in stop_words
    ]
    return " ".join(cleaned_tokens)


def predict_category(new_input):
    # Preprocess the input data
    cleaned_input = clean_text(new_input)
    # Transform the cleaned input using the same TF-IDF vectorizer
    transformed_input = vectorizer.transform([cleaned_input])
    # Predict the category using the trained model
    predicted_category = model.predict(transformed_input)
    return predicted_category[0]

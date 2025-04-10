# -*- coding: utf-8 -*-
"""DS340W Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1joWfuBqvYrjio7ChlJcwygYkaAFpB0DE
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import MultinomialNB
from transformers import BertTokenizer, BertModel
import torch

# Set device to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load a smaller multilingual model (DistilBERT)
tokenizer = BertTokenizer.from_pretrained('distilbert-base-multilingual-cased')
bert_model = BertModel.from_pretrained('distilbert-base-multilingual-cased').to(device)

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

from google.colab import drive

drive.mount('/content/drive')
df=pd.read_csv('/content/drive/MyDrive/DS 340W/data-augmented.csv', sep= ',', header = 0)

df.head()

# Check missing values
df.isnull().sum()

df = df.dropna()

df.isnull().sum()

# Check spam and ham values
df['labels'].value_counts().plot(kind='bar')

spam = []

# Iterate over the DataFrame rows
for index in df.index:
    row = df.loc[index]  # Get the row as a Series
    formatted_row = f"{row['labels']}\t{row['text']}"  # Format as "label\ttext" # need to change format !!!
    spam.append(formatted_row)  # Append the formatted row to spam

# Create preprocesing function
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove special characters (keep apostrophes for contractions)
    text = re.sub(r"[^a-zA-Z\s']", '', text)

    # Tokenize the text
    tokens = word_tokenize(text)

    # Remove stopwords
    filtered_tokens = [word for word in tokens if word not in stop_words]

    # Join the tokens back into a single string
    preprocessed_text = ' '.join(filtered_tokens)

    return preprocessed_text

def preprocess_line(data):
    preprocessed_data = []
    for line in data:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            label, text = parts
            preprocessed_text = preprocess_text(text)
            preprocessed_data.append([label, preprocessed_text])
    return preprocessed_data

preprocessed_spam = preprocess_line(spam)

preprocessed_spam[1]

# Convert to DataFrame
df = pd.DataFrame(preprocessed_spam, columns=["labels", "text"]) # need to change format !!!

# Display the first few rows
print(df.head())

# Encode labels
label_encoder = LabelEncoder()
df['labels'] = label_encoder.fit_transform(df['labels'])

# Feature extraction
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['text'])
y = df['labels']

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize models
models = {
    "SVM": SVC(),
    "Decision Tree": DecisionTreeClassifier(),
    "KNN": KNeighborsClassifier(),
    "Logistic Regression": LogisticRegression(),
    "MLP": MLPClassifier(),
    "Naive Bayes": MultinomialNB()
}

# Train and evaluate models
accuracy_scores = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    accuracy_scores[name] = acc
    print(f"{name} Accuracy: {acc:.4f}")

# Encode labels
label_encoder = LabelEncoder()
df['labels'] = label_encoder.fit_transform(df['labels'])

# Function to encode texts in batches
def encode_texts_in_batches(texts, tokenizer, model, batch_size=32, max_length=128):
    encoded_features = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size].tolist()
        encoded_inputs = tokenizer(batch_texts, padding=True, truncation=True, max_length=max_length, return_tensors='pt').to(device)

        with torch.no_grad():
            outputs = model(**encoded_inputs)

        batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        encoded_features.append(batch_embeddings)

    return np.vstack(encoded_features)

# Feature extraction using DistilBERT
X = encode_texts_in_batches(df['text'], tokenizer, bert_model)
y = df['labels']

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize models
models = {
    "SVM": SVC(),
    "Decision Tree": DecisionTreeClassifier(),
    "KNN": KNeighborsClassifier(),
    "Logistic Regression": LogisticRegression(),
    "MLP": MLPClassifier()
}

# Train and evaluate models
accuracy_scores = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    accuracy_scores[name] = acc
    print(f"{name} Accuracy: {acc:.4f}")
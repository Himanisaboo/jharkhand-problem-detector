import os
import sys
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

DATA_DIR = r"c:\Users\Himani\Desktop\sih2026"
COMPLAINTS_CSV = os.path.join(DATA_DIR, "samadhan_setu_synthetic_complaints_v4.csv")
TAXONOMY_CSV = os.path.join(DATA_DIR, "samadhan_setu_innovation_taxonomy_v1.csv")
INSTITUTION_CSV = os.path.join(DATA_DIR, "samadhan_setu_institution_mapping_v1.csv")
MODEL_SAVE_PATH = os.path.join(DATA_DIR, "samadhan_setu_model.joblib")

def load_data():
    print(f"[*] Loading dataset from: {COMPLAINTS_CSV}")
    df = pd.read_csv(COMPLAINTS_CSV, encoding="utf-8-sig")
    df = df.fillna("None")
    print(f"[+] Loaded {len(df)} complaint records.")
    return df

def build_vectorizer():
    """Builds a combined word and character n-gram TF-IDF vectorizer to robustly handle

    English, Hinglish, Hindi, spelling errors, and short inputs.
    """
    word_vec = TfidfVectorizer(
        ngram_range=(1, 3),
        analyzer='word',
        sublinear_tf=True,
        min_df=1
    )
    char_vec = TfidfVectorizer(
        ngram_range=(2, 5),
        analyzer='char_wb',
        sublinear_tf=True,
        min_df=1
    )
    union = FeatureUnion([
        ('word', word_vec),
        ('char', char_vec)
    ])
    return union

def train_and_evaluate():
    df = load_data()
    
    # Split train/test
    train_df, test_df = train_test_split(df, test_size=0.20, random_state=42, stratify=df['domain'])
    print(f"[*] Train set size: {len(train_df)} | Test set size: {len(test_df)}")

    X_train_text = train_df['complaint_text']
    X_test_text = test_df['complaint_text']

    # Vectorize
    vectorizer = build_vectorizer()
    print("[*] Fitting TF-IDF FeatureUnion (Word + Char n-grams)...")
    X_train_vec = vectorizer.fit_transform(X_train_text)
    X_test_vec = vectorizer.transform(X_test_text)
    print(f"[+] Feature matrix shape: {X_train_vec.shape}")

    # Targets to predict
    target_cols = [
        'domain',
        'category',
        'route',
        'severity',
        'recurrence',
        'innovation_required',
        'innovation_area'
    ]

    models = {}
    metrics_report = {}

    print("\n================ ML MODEL TRAINING & EVALUATION ================")
    for target in target_cols:
        y_train = train_df[target]
        y_test = test_df[target]

        # Train Logistic Regression model with C=5.0 for strong regularization-performance balance
        clf = LogisticRegression(max_iter=1000, C=5.0, random_state=42)
        clf.fit(X_train_vec, y_train)

        y_pred = clf.predict(X_test_vec)
        acc = accuracy_score(y_test, y_pred)
        
        models[target] = clf
        metrics_report[target] = acc

        print(f"\n---> Target: {target.upper()}")
        print(f"     Test Accuracy: {acc * 100:.2f}%")
        # Print top classes classification report sample
        report_dict = classification_report(y_test, y_pred, zero_division=0, output_dict=True)
        weighted_f1 = report_dict.get('weighted avg', {}).get('f1-score', 0)
        print(f"     Weighted F1-Score: {weighted_f1 * 100:.2f}%")

    # Package model bundle
    bundle = {
        'vectorizer': vectorizer,
        'models': models,
        'target_cols': target_cols,
        'metrics': metrics_report
    }

    joblib.dump(bundle, MODEL_SAVE_PATH)
    print(f"\n[SUCCESS] Trained model pipeline saved to: {MODEL_SAVE_PATH}")

if __name__ == '__main__':
    train_and_evaluate()

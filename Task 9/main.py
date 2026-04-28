from pathlib import Path
import math
import random
import re
from collections import Counter, defaultdict
from typing import DefaultDict

from flask import Flask, render_template, request

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))

# Small custom dataset for assignment demo (binary sentiment classification)
# label: 1 = positive, 0 = negative
samples = [
    ("This movie was fantastic and full of emotions", 1),
    ("I really liked the direction and acting", 1),
    ("What a wonderful and heart touching story", 1),
    ("The film was boring and too long", 0),
    ("Worst script I have seen this year", 0),
    ("The acting was poor and the plot was weak", 0),
    ("Amazing visuals and a great soundtrack", 1),
    ("I enjoyed every scene of this movie", 1),
    ("The experience was disappointing and dull", 0),
    ("Not worth the ticket price", 0),
    ("Excellent screenplay and strong performances", 1),
    ("The ending was predictable and bad", 0),
    ("I would recommend this to my friends", 1),
    ("The dialogues were unnatural and forced", 0),
    ("A very refreshing and entertaining film", 1),
    ("Too much noise and no real story", 0),
    ("Superb camera work and editing", 1),
    ("It felt like a waste of time", 0),
    ("Great pacing and impressive character development", 1),
    ("Music was loud and irritating", 0),
    ("The cast delivered a memorable performance", 1),
    ("I almost slept during the second half", 0),
    ("Storyline was creative and engaging", 1),
    ("Nothing new, very average and forgettable", 0),
]

Sample = tuple[str, int]
Vocabulary = dict[str, int]
Vector = dict[int, int]


TOKEN_PATTERN = re.compile(r"[a-zA-Z']+")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
    "this",
    "i",
    "what",
    "very",
    "too",
    "no",
    "not",
}


def tokenize(text: str) -> list[str]:
    tokens = [match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)]
    return [token for token in tokens if token not in STOP_WORDS]


def split_dataset_stratified(
    data: list[Sample], test_size: float = 0.25, random_state: int = 42
) -> tuple[list[Sample], list[Sample]]:
    grouped: DefaultDict[int, list[Sample]] = defaultdict(list)
    for text, label in data:
        grouped[label].append((text, label))

    rng = random.Random(random_state)
    train: list[Sample] = []
    test: list[Sample] = []
    for label_samples in grouped.values():
        local: list[Sample] = label_samples[:]
        rng.shuffle(local)
        test_count = max(1, int(round(len(local) * test_size)))
        test.extend(local[:test_count])
        train.extend(local[test_count:])

    rng.shuffle(train)
    rng.shuffle(test)
    return train, test


def build_vocabulary(texts: list[str]) -> Vocabulary:
    vocab: Vocabulary = {}
    for text in texts:
        for token in tokenize(text):
            if token not in vocab:
                vocab[token] = len(vocab)
    return vocab


def vectorize_text(text: str, vocabulary: Vocabulary) -> Vector:
    counts = Counter(tokenize(text))
    return {vocabulary[token]: freq for token, freq in counts.items() if token in vocabulary}


def vectorize_texts(texts: list[str], vocabulary: Vocabulary) -> list[Vector]:
    return [vectorize_text(text, vocabulary) for text in texts]


class SimpleMultinomialNB:
    def __init__(self, alpha: float = 1.0) -> None:
        self.alpha = alpha
        self.classes_: list[int] = []
        self.class_log_prior_: dict[int, float] = {}
        self.feature_log_prob_: dict[int, dict[int, float]] = {}

    def fit(self, vectors: list[Vector], labels: list[int], vocab_size: int) -> "SimpleMultinomialNB":
        self.classes_ = sorted(set(labels))
        class_counts = Counter(labels)
        total_docs = len(labels)

        token_counts_by_class: dict[int, Counter[int]] = {
            cls: Counter() for cls in self.classes_
        }
        total_tokens_by_class = {cls: 0 for cls in self.classes_}

        for vector, label in zip(vectors, labels):
            token_counts_by_class[label].update(vector)
            total_tokens_by_class[label] += sum(vector.values())

        for cls in self.classes_:
            self.class_log_prior_[cls] = math.log(class_counts[cls] / total_docs)
            denom = total_tokens_by_class[cls] + self.alpha * vocab_size
            self.feature_log_prob_[cls] = {
                idx: math.log((token_counts_by_class[cls].get(idx, 0) + self.alpha) / denom)
                for idx in range(vocab_size)
            }
        return self

    def predict_log_scores(self, vector: Vector) -> dict[int, float]:
        scores: dict[int, float] = {}
        for cls in self.classes_:
            score = self.class_log_prior_[cls]
            for idx, count in vector.items():
                score += count * self.feature_log_prob_[cls].get(idx, 0.0)
            scores[cls] = score
        return scores

    def predict(self, vectors: list[Vector]) -> list[int]:
        predictions: list[int] = []
        for vector in vectors:
            scores = self.predict_log_scores(vector)
            predictions.append(max(scores.items(), key=lambda item: item[1])[0])
        return predictions

    def predict_proba(self, vectors: list[Vector]) -> list[list[float]]:
        probabilities: list[list[float]] = []
        for vector in vectors:
            log_scores = self.predict_log_scores(vector)
            max_log = max(log_scores.values())
            exp_scores = {cls: math.exp(value - max_log) for cls, value in log_scores.items()}
            norm = sum(exp_scores.values())
            probabilities.append([exp_scores[cls] / norm for cls in self.classes_])
        return probabilities


def format_classification_report(y_true: list[int], y_pred: list[int]) -> str:
    labels = [0, 1]
    names = {0: "negative", 1: "positive"}
    lines = ["label      precision    recall  f1-score   support"]

    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        support = sum(1 for t in y_true if t == label)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        lines.append(
            f"{names[label]:<10} {precision:>9.2f} {recall:>9.2f} {f1:>9.2f} {support:>9}"
        )

    return "\n".join(lines)


def train_sentiment_model() -> tuple[SimpleMultinomialNB, Vocabulary, float, str]:
    train_set, test_set = split_dataset_stratified(samples, test_size=0.25, random_state=42)
    X_train = [text for text, _ in train_set]
    y_train = [label for _, label in train_set]
    X_test = [text for text, _ in test_set]
    y_test = [label for _, label in test_set]

    vocabulary = build_vocabulary(X_train)
    X_train_vec = vectorize_texts(X_train, vocabulary)
    X_test_vec = vectorize_texts(X_test, vocabulary)

    model = SimpleMultinomialNB(alpha=1.0)
    model.fit(X_train_vec, y_train, vocab_size=len(vocabulary))

    predictions = model.predict(X_test_vec)
    accuracy = sum(1 for y, p in zip(y_test, predictions) if y == p) / len(y_test)
    report = format_classification_report(y_test, predictions)

    return model, vocabulary, accuracy, report


model, vectorizer, accuracy, report = train_sentiment_model()


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    input_text = ""
    prediction = None
    confidence = None
    positive_score = None
    negative_score = None
    word_count = 0
    char_count = 0

    if request.method == "POST":
        raw_input = request.form.get("review_text", "")
        input_text = str(raw_input).strip()
        if input_text:
            text_vec = vectorize_text(input_text, vectorizer)
            pred = model.predict([text_vec])[0]
            prediction = "positive" if pred == 1 else "negative"

            probabilities = model.predict_proba([text_vec])[0]
            class_to_prob = {
                int(label): float(prob)
                for label, prob in zip(model.classes_, probabilities)
            }

            positive_score = round(class_to_prob.get(1, 0.0) * 100, 2)
            negative_score = round(class_to_prob.get(0, 0.0) * 100, 2)
            confidence = max(positive_score, negative_score)
            word_count = len(input_text.split())
            char_count = len(input_text)

    return render_template(
        "index.html",
        accuracy=round(accuracy * 100, 2),
        report=report,
        input_text=input_text,
        prediction=prediction,
        confidence=confidence,
        positive_score=positive_score,
        negative_score=negative_score,
        word_count=word_count,
        char_count=char_count,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

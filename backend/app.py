from flask import Flask, render_template, request, redirect, url_for, session
import os, random, spacy, PyPDF2
from docx import Document

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_key_for_dev")
# Needed for session storage
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

nlp = spacy.load("en_core_web_sm")

# ---------- UTILITIES ----------
def extract_text(path):
    ext = path.split(".")[-1].lower()
    if ext == "pdf":
        text = ""
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    elif ext == "docx":
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        return open(path, encoding="utf-8", errors="ignore").read()

def generate_quiz(text):
    doc = nlp(text)
    quiz = []
    sentences = [s.text for s in doc.sents if len(s.text) > 30]
    for s in sentences[:5]:
        nouns = [t.text for t in nlp(s) if t.pos_ in ["NOUN", "PROPN"]]
        if not nouns:
            continue
        ans = random.choice(nouns)
        q = s.replace(ans, "_____")
        options = list(set(random.sample(nouns, min(3, len(nouns))) + [ans]))
        random.shuffle(options)
        quiz.append({"question": q, "choices": options, "answer": ans})
    return quiz

def generate_puzzles(text):
    words = [w.text.lower() for w in nlp(text) if w.is_alpha and len(w.text) > 5]
    unique = list(set(words))
    random.shuffle(unique)
    puzzles = []
    for w in unique[:5]:
        j = "".join(random.sample(w, len(w)))
        puzzles.append({"puzzle": f"Unscramble this word: {j}", "answer": w})
    return puzzles

# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)
    text = extract_text(path)

    quiz = generate_quiz(text)
    puzzles = generate_puzzles(text)

    # store in Flask session
    session["quiz"] = quiz
    session["puzzles"] = puzzles

    return render_template("quiz.html", quiz=quiz)

@app.route("/submit", methods=["POST"])
def submit():
    quiz = session.get("quiz", [])
    results = []
    score = 0
    for i, q in enumerate(quiz):
        user = request.form.get(f"q{i}")
        correct = q["answer"]
        status = "✅" if user == correct else "❌"
        if status == "✅":
            score += 1
        results.append({
            "question": q["question"],
            "user": user,
            "correct": correct,
            "status": status
        })
    return render_template("quiz_result.html", results=results, score=score, total=len(quiz))

@app.route("/puzzle")
def puzzle():
    puzzles = session.get("puzzles", [])
    return render_template("puzzle.html", puzzles=puzzles)

@app.route("/check_puzzles", methods=["POST"])
def check_puzzles():
    puzzles = session.get("puzzles", [])
    results = []
    correct_count = 0
    for i, p in enumerate(puzzles):
        user = request.form.get(f"p{i}", "").strip().lower()
        ans = p["answer"].lower()
        is_correct = user == ans
        if is_correct:
            correct_count += 1
        results.append({
            "puzzle": p["puzzle"],
            "user": user,
            "answer": ans,
            "is_correct": is_correct
        })
    return render_template("puzzle_result.html", results=results, correct=correct_count, total=len(puzzles))
@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


if __name__ == "__main__":
    app.run(debug=True)


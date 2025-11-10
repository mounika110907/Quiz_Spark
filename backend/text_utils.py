import os, random, spacy, PyPDF2
from docx import Document

nlp = spacy.load("en_core_web_sm")

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

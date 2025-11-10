import os, random, spacy, PyPDF2
from docx import Document

nlp = spacy.load("en_core_web_sm")

def extract_text(path):
    ext = os.path.splitext(path)[-1].lower()
    if ext == ".pdf":
        text = ""
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    elif ext == ".docx":
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()

def _get_nouns(sentence):
    return [t.text for t in nlp(sentence) if t.pos_ in ["NOUN", "PROPN"]]

def generate_quiz(text, sentence_length=30, max_questions=5, max_options=3):
    doc = nlp(text)
    sentences = [s.text for s in doc.sents if len(s.text) > sentence_length]
    quiz = []
    for s in sentences[:max_questions]:
        nouns = _get_nouns(s)
        if not nouns:
            continue
        ans = random.choice(nouns)
        options = list(set(random.sample(nouns, min(max_options, len(nouns))) + [ans]))
        random.shuffle(options)
        quiz.append({"question": s.replace(ans, "_____"), "choices": options, "answer": ans})
    return quiz

def generate_puzzles(text, min_word_length=6, max_puzzles=5):
    words = [w.text.lower() for w in nlp(text) if w.is_alpha and len(w.text) >= min_word_length]
    unique = list(set(words))
    random.shuffle(unique)
    puzzles = []
    for w in unique[:max_puzzles]:
        scrambled = "".join(random.sample(w, len(w)))
        puzzles.append({"puzzle": f"Unscramble this word: {scrambled}", "answer": w})
    return puzzles

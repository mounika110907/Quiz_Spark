import os
import random
import spacy
import PyPDF2
from docx import Document

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")

def extract_text(path):
    """
    Extracts text from txt, pdf, or docx files.
    Returns empty string for unsupported or empty files.
    """
    if not os.path.exists(path) or not os.path.isfile(path):
        return ""
    ext = os.path.splitext(path)[-1].lower()
    try:
        if ext == ".pdf":
            return _extract_pdf_text(path)
        elif ext == ".docx":
            return _extract_docx_text(path)
        else:
            with open(path, encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception:
        return ""

def _extract_pdf_text(path):
    text = ""
    with open(path, "rb") as f:
        try:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t
        except Exception:
            return ""
    return text

def _extract_docx_text(path):
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception:
        return ""

def _get_nouns(sentence):
    doc = nlp(sentence)
    return [t.text for t in doc if t.pos_ in ["NOUN", "PROPN"]]

def generate_quiz(text, sentence_length=30, max_questions=5, max_options=3):
    doc = nlp(text)
    sentences = [s.text for s in doc.sents if len(s.text) > sentence_length]
    quiz = []
    for s in sentences[:max_questions]:
        nouns = _get_nouns(s)
        if not nouns:
            continue
        ans = random.choice(nouns)
        # Ensure options are unique and include the answer
        base_options = list(set(nouns))
        if ans not in base_options:
            base_options.append(ans)
        option_sample = [x for x in base_options if x != ans]
        options = random.sample(option_sample, min(max_options, len(option_sample)))
        options.append(ans)
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

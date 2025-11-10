import os
import random
import spacy
import PyPDF2
from docx import Document

# Load spaCy English model once for efficiency
nlp = spacy.load("en_core_web_sm")

def extract_text(path):
    """
    Extract text content from files.
    Supports .txt, .pdf, .docx; returns empty string if file not readable or unsupported.
    """
    if not os.path.isfile(path):
        return ""
    ext = os.path.splitext(path)[1].lower()
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
    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception:
        # Return empty string if PDF reading fails
        return ""
    return text

def _extract_docx_text(path):
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception:
        return ""

def _get_nouns(sentence):
    """
    Extract noun and proper noun tokens from a given sentence string.
    """
    doc = nlp(sentence)
    return [token.text for token in doc if token.pos_ in ("NOUN", "PROPN")]

def generate_quiz(text, sentence_length=30, max_questions=5, max_options=3):
    """
    Generate a quiz as a list of questions from the text using noun blanks.
    Only sentences longer than 'sentence_length' are used.
    Each question has multiple options including the correct noun answer.
    """
    doc = nlp(text)
    sentences = [s.text for s in doc.sents if len(s.text) > sentence_length]
    quiz = []
    for sentence in sentences[:max_questions]:
        nouns = _get_nouns(sentence)
        if not nouns:
            continue
        ans = random.choice(nouns)
        base_options = list(set(nouns))
        if ans not in base_options:
            base_options.append(ans)
        choices = random.sample([x for x in base_options if x != ans], min(max_options, len(base_options)-1))
        choices.append(ans)
        random.shuffle(choices)
        question = sentence.replace(ans, "_____")
        quiz.append({"question": question, "choices": choices, "answer": ans})
    return quiz

def generate_puzzles(text, min_word_length=6, max_puzzles=5):
    """
    Generate a list of scrambled word puzzles from words in the text.
    Only words longer than or equal to 'min_word_length' are considered.
    Each puzzle consists of a scrambled version and the original answer.
    """
    words = [token.text.lower() for token in nlp(text) if token.is_alpha and len(token.text) >= min_word_length]
    unique_words = list(set(words))
    random.shuffle(unique_words)
    puzzles = []
    for word in unique_words[:max_puzzles]:
        scrambled = "".join(random.sample(word, len(word)))
        puzzles.append({"puzzle": f"Unscramble this word: {scrambled}", "answer": word})
    return puzzles

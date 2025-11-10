import os
import random
import spacy
import PyPDF2
from docx import Document

# Load spaCy English model just once for better performance
nlp = spacy.load("en_core_web_sm")

def extract_text(path):
    """
    Extracts text from .txt, .pdf, .docx files.
    Returns empty string for unsupported files or read errors.
    """
    if not os.path.isfile(path):
        return ""

    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            return _extract_pdf_text(path)
        elif ext == ".docx":
            return _extract_docx_text(path)
        elif ext == ".txt":
            with open(path, encoding="utf-8", errors="ignore") as f:
                return f.read()
        else:
            # Unsupported file extension returns empty string
            return ""
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
    Returns list of noun and proper noun tokens in a sentence string.
    """
    doc = nlp(sentence)
    return [token.text for token in doc if token.pos_ in ("NOUN", "PROPN")]

def generate_quiz(text, sentence_length=30, max_questions=5, max_options=3, min_nouns=1):
    """
    Generates quiz questions by replacing randomly chosen noun in each sentence with blanks.
    Only sentences longer than sentence_length with at least min_nouns nouns are used.
    Returns list of dict: question, choices, answer.
    """
    doc = nlp(text)
    sentences = [s.text for s in doc.sents if len(s.text) > sentence_length]
    quiz = []

    for sentence in sentences:
        nouns = _get_nouns(sentence)
        if len(nouns) < min_nouns:
            continue

        ans = random.choice(nouns)
        base_options = list(set(nouns))
        if ans not in base_options:
            base_options.append(ans)

        # sample options excluding answer from base options, limiting by max_options and available nouns
        filtered_options = [opt for opt in base_options if opt != ans]
        sample_options = random.sample(filtered_options, min(max_options, len(filtered_options)))

        choices = sample_options + [ans]
        random.shuffle(choices)

        question = sentence.replace(ans, "_____")
        quiz.append({"question": question, "choices": choices, "answer": ans})

        if len(quiz) == max_questions:
            break

    return quiz

def generate_puzzles(text, min_word_length=6, max_puzzles=5):
    """
    Generates a list of word scramble puzzles from the input text.
    Only words of at least min_word_length are used.
    Returns list of dict with puzzle text and answer.
    """
    words = [token.text.lower() for token in nlp(text) if token.is_alpha and len(token.text) >= min_word_length]
    unique_words = list(set(words))
    random.shuffle(unique_words)
    puzzles = []

    for word in unique_words[:max_puzzles]:
        scrambled = "".join(random.sample(word, len(word)))
        puzzles.append({"puzzle": f"Unscramble this word: {scrambled}", "answer": word})

    return puzzles

import os
import random
import spacy
import PyPDF2
from docx import Document

# Load spaCy English model once for better performance
nlp = spacy.load("en_core_web_sm")

def extract_text(path):
    """
    Extracts text from .txt, .pdf, .docx files.
    Returns empty string for unsupported, unreadable files or errors.
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
            # Unsupported extensions return empty string
            return ""
    except Exception as e:
        # You can connect this to logging for cleanup
        print(f"Error extracting text from {path} ({ext}): {e}")
        return ""

def _extract_pdf_text(path):
    text = ""
    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                except Exception as e:
                    print(f"PDF page extraction error in {path}: {e}")
    except Exception as e:
        print(f"PDF file open error: {e}")
        return ""
    return text

def _extract_docx_text(path):
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        print(f"DOCX load error: {e}")
        return ""

def _get_nouns(sentence):
    """
    Extract noun and proper noun tokens from sentence string.
    """
    doc = nlp(sentence)
    return [token.text for token in doc if token.pos_ in ("NOUN", "PROPN")]

def generate_quiz(text, sentence_length=30, max_questions=5, max_options=3, min_nouns=1):
    """
    Create quiz questions from text by blanking nouns in sentences.
    Only use sentences longer than sentence_length having min_nouns nouns.
    Randomly sample answer and choices per question.
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

        filtered_options = [opt for opt in base_options if opt != ans]
        if filtered_options:
            sample_options = random.sample(filtered_options, min(max_options, len(filtered_options)))
        else:
            sample_options = []

        choices = sample_options + [ans]
        random.shuffle(choices)

        question = sentence.replace(ans, "_____")
        quiz.append({"question": question, "choices": choices, "answer": ans})

        if len(quiz) == max_questions:
            break
    return quiz

def generate_puzzles(text, min_word_length=6, max_puzzles=5):
    """
    Generate word scramble puzzles from words in text.
    Only words with length >= min_word_length considered.
    """
    words = [token.text.lower() for token in nlp(text) if token.is_alpha and len(token.text) >= min_word_length]
    unique_words = list(set(words))
    random.shuffle(unique_words)
    puzzles = []

    for word in unique_words[:max_puzzles]:
        if len(word) < 2:
            continue
        try:
            scrambled = "".join(random.sample(word, len(word)))
            puzzles.append({"puzzle": f"Unscramble this word: {scrambled}", "answer": word})
        except Exception as e:
            print(f"Error scrambling word {word}: {e}")
            continue
    return puzzles

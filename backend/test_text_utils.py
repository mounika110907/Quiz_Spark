import tempfile
import os
from text_utils import extract_text, generate_quiz, generate_puzzles

def test_extract_text_txt():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
        f.write("Hello, pytest!")
        f.seek(0)
        path = f.name
    result = extract_text(path)
    assert result == "Hello, pytest!"
    os.remove(path)

def test_extract_text_empty():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
        path = f.name
    result = extract_text(path)
    assert result == ""
    os.remove(path)

def test_extract_text_docx():
    from docx import Document
    path = os.path.join(tempfile.gettempdir(), "test.docx")
    doc = Document()
    doc.add_paragraph("Docx test paragraph.")
    doc.save(path)
    result = extract_text(path)
    assert "Docx test paragraph." in result
    os.remove(path)

def test_generate_quiz_basic():
    text = "This is a test sentence with some nouns like apple and banana. Another sentence with cat and dog."
    quiz = generate_quiz(text)
    assert isinstance(quiz, list)
    assert len(quiz) > 0
    for q in quiz:
        assert "question" in q
        assert "choices" in q
        assert "answer" in q
        assert q["answer"] in q["choices"]

def test_generate_quiz_no_nouns():
   text = "Quickly running, always jumping, happily laughing."
    quiz = generate_quiz(text)
    assert quiz == []

def test_generate_quiz_short_sentences():
    text = "Cat. Dog. Apple."
    quiz = generate_quiz(text)
    # All sentences too short for quiz
    assert quiz == []

def test_generate_puzzles_basic():
    text = "Python programming language provides powerful features."
    puzzles = generate_puzzles(text)
    assert isinstance(puzzles, list)
    assert len(puzzles) > 0
    for p in puzzles:
        assert "puzzle" in p
        assert "answer" in p
        scrambled = p["puzzle"].replace("Unscramble this word: ", "").replace(" ", "")
        # The scrambled should be an anagram of the answer
        assert sorted(scrambled.lower()) == sorted(p["answer"].lower())

def test_generate_puzzles_min_word_length():
    text = "Short small tiniest apple programming"
    puzzles = generate_puzzles(text)
    # Only "programming" and "apple" are long enough (>5 chars)
    assert any(p["answer"] == "programming" for p in puzzles) or any(p["answer"] == "apple" for p in puzzles)

import tempfile
import os
from text_utils import extract_text, generate_quiz, generate_puzzles

# ... (all your existing tests here) ...

def test_extract_text_nonexistent_file():
    # Should return "" for non-existent file path
    result = extract_text("no_such_file.txt")
    assert result == ""

def test_extract_text_folder():
    # Should return "" if given a directory instead of a file
    tmp_dir = tempfile.gettempdir()
    result = extract_text(tmp_dir)
    assert result == ""

def test_generate_quiz_max_questions():
    # Should not return more questions than max_questions
    text = ("An apple a day keeps the doctor away. "
            "Banana is yellow. "
            "Cat on the mat. "
            "Dog barked loudly at the stranger in the alley. "
            "Elephant is the largest land animal. "
            "Fox is quick and clever. "
            "Giraffe has a long neck.")
    quiz = generate_quiz(text, max_questions=3)
    assert len(quiz) <= 3

def test_generate_puzzles_handles_duplicates():
    # Duplicate words in input should only create one puzzle per unique word
    text = "programming programming programming Python Python"
    puzzles = generate_puzzles(text, max_puzzles=10)
    seen = set()
    for p in puzzles:
        # No duplicate answers in puzzles (answers must be unique)
        assert p["answer"] not in seen
        seen.add(p["answer"])

def test_generate_puzzles_empty_text():
    # Should return empty list for empty input
    puzzles = generate_puzzles("")
    assert puzzles == []

def test_generate_quiz_empty_text():
    # Should return empty list for empty input
    quiz = generate_quiz("")
    assert quiz == []

def test_extract_docx_exception(monkeypatch):
    # Simulate exception in docx extraction (e.g., file can't be opened)
    def always_fail_docx(path):
        raise Exception("Docx load failed!")
    monkeypatch.setattr('text_utils.Document', lambda x: (_ for _ in ()).throw(Exception("fail")))
    result = extract_text("somefile.docx")
    assert result == ""

def test_pdf_exception(monkeypatch):
    # Simulate exception in PDF extraction (e.g., PDF reading fails)
    def always_fail_pdf(path):
        raise Exception("PDF load failed!")
    monkeypatch.setattr('text_utils.PyPDF2.PdfReader', lambda x: (_ for _ in ()).throw(Exception("fail")))
    result = extract_text("somefile.pdf")
    assert result == ""

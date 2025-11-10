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
        assert sorted(scrambled.lower()) == sorted(p["answer"].lower())

def test_generate_puzzles_min_word_length():
    text = "Short small tiniest apple programming"
    puzzles = generate_puzzles(text)
    assert any(p["answer"] == "programming" for p in puzzles) or any(p["answer"] == "apple" for p in puzzles)

def test_extract_text_pdf():
    from fpdf import FPDF
    path = os.path.join(tempfile.gettempdir(), "test.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Test PDF content.", ln=True)
    pdf.output(path)
    result = extract_text(path)
    assert "Test PDF content." in result
    os.remove(path)

def test_extract_text_malformed_docx():
    path = os.path.join(tempfile.gettempdir(), "corrupt.docx")
    with open(path, "w") as f:
        f.write("not a real docx file")
    result = extract_text(path)
    assert result == ""
    os.remove(path)

# --- Additional Coverage Extension ---

def test_extract_text_nonexistent_file():
    result = extract_text("no_such_file.txt")
    assert result == ""

def test_extract_text_folder():
    tmp_dir = tempfile.gettempdir()
    result = extract_text(tmp_dir)
    assert result == ""

def test_generate_quiz_max_questions():
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
    text = "programming programming programming Python Python"
    puzzles = generate_puzzles(text, max_puzzles=10)
    seen = set()
    for p in puzzles:
        assert p["answer"] not in seen
        seen.add(p["answer"])

def test_generate_puzzles_empty_text():
    puzzles = generate_puzzles("")
    assert puzzles == []

def test_generate_quiz_empty_text():
    quiz = generate_quiz("")
    assert quiz == []

def test_extract_docx_exception(monkeypatch):
    monkeypatch.setattr('text_utils.Document', lambda x: (_ for _ in ()).throw(Exception("fail")))
    result = extract_text("somefile.docx")
    assert result == ""

def test_pdf_exception(monkeypatch):
    monkeypatch.setattr('text_utils.PyPDF2.PdfReader', lambda x: (_ for _ in ()).throw(Exception("fail")))
    result = extract_text("somefile.pdf")
    assert result == ""

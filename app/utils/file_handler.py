from pathlib import Path
import json
from werkzeug.datastructures import FileStorage
import zipfile
import re

# BASE FOLDERS
BASE_UPLOADS= Path("data/uploads")
BASE_QUIZZES= Path("data/quizzes")
BASE_UPLOADS.mkdir(parents=True, exist_ok=True)
BASE_QUIZZES.mkdir(parents=True, exist_ok=True)

# Safety sanitization
_SAFE_RE = re.compile(r"[^a-zA-Z0-9_-]+")

def _safe_name(value: str) -> str:
    value= (value or "").strip()
    value= _SAFE_RE.sub("_", value)
    if not value:
        raise ValueError("Invalid empty name after sanitization")
    return value


# USER FOLDERS-> ASSIGNMENTS-> FILES LISTING
def get_user_folder(username: str) -> Path:
    username= _safe_name(username)
    folder= BASE_UPLOADS / username
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_user_assignment_folder(username: str, assignment_id: str) -> Path:
    username= _safe_name(username)
    assignment_id= _safe_name(assignment_id)
    folder= get_user_folder(username)/ assignment_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def list_user_assignments(username: str) -> list:
    user_folder= get_user_folder(username)
    return sorted([p.name for p in user_folder.iterdir() if p.is_dir()])


# JSON HELPERS
def save_json(data, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_json(path: Path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# TEACHER SPECS
def save_teacher_spec_user(username: str, assignment_id: str, spec):
    folder= get_user_assignment_folder(username, assignment_id)
    save_json(spec, folder/ "teacher_spec.json")


def load_teacher_spec_user(username: str, assignment_id: str):
    folder= get_user_assignment_folder(username, assignment_id)
    return load_json(folder/ "teacher_spec.json")


# STUDENT CODE + SUMMARIES
def save_uploaded_code_user(file: FileStorage, username: str, assignment_id: str) -> Path:
    folder= get_user_assignment_folder(username, assignment_id) / "uploads"
    folder.mkdir(parents=True, exist_ok=True)
    filename= file.filename or "uploaded.zip"
    filename= _SAFE_RE.sub("_", filename)  # sanitize filename too
    
    saved_path= folder/ filename
    file.save(saved_path)
    return saved_path


def save_code_summaries_user(username: str, assignment_id: str, summaries):
    folder= get_user_assignment_folder(username, assignment_id)
    save_json(summaries, folder/ "code_summaries.json")


def load_code_summaries_user(username: str, assignment_id: str):
    folder= get_user_assignment_folder(username, assignment_id)
    return load_json(folder/ "code_summaries.json")


# EXTRACTION
def extract_zip(zip_path: Path) -> Path:
    zip_path= Path(zip_path)
    extract_folder= zip_path.parent/ "extracted"
    extract_folder.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_folder)
    
    return extract_folder


# AIKEN CONVERSION
def extract_letter_from_text(text: str) -> str | None:
    text= (text or "").strip().upper()
    match= re.search(r"([Α-ΩA-Z])\.?\s*", text)
    if not match:
        return None
    
    char= match.group(1)
    greek_map= {"Α": "A", "Β": "B", "Γ": "C", "Δ": "D", "Ε": "E", "Ζ": "F"}
    if "Α" <= char <= "Ω":
        return greek_map.get(char)
    if "A" <= char <= "F":
        return char
    return None


def clean_choice_text(choice: str) -> str:
    choice= choice or ""
    #καθαρισμός αρχικών γραμμάτων επιλογών ώστε να τα χτίσει σωστά το AIKEN
    return re.sub(r"^[Α-ΩA-Z][\.\)\:\,]\s*", "", choice.strip())


def convert_quiz_to_aiken(quiz: list) -> str:
    output_lines= []
    letters= ["A", "B", "C", "D", "E", "F"]
    for idx, item in enumerate(quiz or [], 1):
        question= (item.get("question") or "").strip()
        choices= item.get("choices") or []
        answer= (item.get("answer") or "").strip()
        
        if not question or not choices:
            continue
        output_lines.append(question)
        
        for i, choice in enumerate(choices[:6]):
            output_lines.append(f"{letters[i]}. {clean_choice_text(str(choice))}")
        
        # Find correct
        correct_idx= 0
        letter= extract_letter_from_text(answer)
        if letter and "A" <= letter <= "F":
            correct_idx= ord(letter)- ord("A")
        else:
            ans= answer.lower()
            for i, choice in enumerate(choices[:6]):
                clean= clean_choice_text(str(choice)).lower()
                if ans== clean or ans in clean or clean.startswith(ans):
                    correct_idx= i
                    break
        output_lines.append(f"ANSWER: {letters[correct_idx]}")
        output_lines.append("")
    
    return "\n".join(output_lines)


# SAVE QUIZ
def save_quiz_text_user(text: str, username: str, assignment_id: str) -> Path:
    username= _safe_name(username)
    assignment_id= _safe_name(assignment_id)
    
    out_path= BASE_QUIZZES/ username/f"{assignment_id}.aiken.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text or "")
    return out_path
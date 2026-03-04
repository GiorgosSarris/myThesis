from flask import Blueprint, request, jsonify
from app.utils.file_handler import (save_uploaded_code_user, extract_zip, save_code_summaries_user)
from agent.astParsing import parse_code, create_llm_summary
from agent.languageDetector import detect_language
from pathlib import Path
import re
from datetime import datetime

student_bp= Blueprint("student_bp", __name__)
SUPPORTED_PARSE_LANGS = {"python", "c", "cpp", "java", "javascript"}

def clean_filename(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]+', '_', name)

@student_bp.route("/upload", methods=["POST"])
def upload_student():
    # Λήψη Username από τα headers (στέλνει το Streamlit)
    username= request.headers.get("X-Username")
    if not username:
        return jsonify({"error": "Authentication required (X-Username missing)"}), 401
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file= request.files["file"]
    if file.filename== "":
        return jsonify({"error": "No file selected"}), 400

    base_name= Path(file.filename).stem
    safe_name= clean_filename(base_name)
    timestamp= datetime.now().strftime("%Y%m%d_%H%M%S")
    assignment_id= f"{safe_name}_{timestamp}"

    # Χρήση των _user συναρτήσεων
    try:
        # Αποθήκευση στον χρήστη
        zip_path= save_uploaded_code_user(file, username, assignment_id)
        extracted_folder= extract_zip(zip_path)
    except Exception as e:
        return jsonify({"error": f"File save failed: {str(e)}"}), 500
    extracted_path= Path(extracted_folder)
    summaries= []
    
    # Parsing Logic
    for code_file in extracted_path.rglob("*"):
        if code_file.is_file():
            # detect language from content+extension
            try:
                content = code_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                content = ""
            lang = detect_language(str(code_file), content)
            if lang not in SUPPORTED_PARSE_LANGS:
                continue

            try:
                parsed= parse_code(lang, str(code_file))
                summary= create_llm_summary(parsed)
                summaries.append(summary)
            except Exception as e:
                print(f"Error parsing {code_file}: {e}")
                summaries.append(f"Error parsing {code_file.name}: {str(e)}")
    # Αποθήκευση summaries στον χρήστη
    save_code_summaries_user(username, assignment_id, summaries)
    
    return jsonify({
        "status": "ok",
        "assignment_id": assignment_id,
        "files_parsed": len(summaries)
    }), 200

from flask import Blueprint, jsonify, request
from app.utils.file_handler import (load_teacher_spec_user, load_code_summaries_user, save_quiz_text_user, convert_quiz_to_aiken)
from agent.prompt import build_prompt
from agent.generateQuiz import generate_quiz
import json
import math

quiz_bp= Blueprint("quiz_bp", __name__)

# Βοηθητική για καθαρισμό JSON από LLM
def clean_and_parse_json(llm_output):
    if isinstance(llm_output, (dict, list)): return llm_output
    if not isinstance(llm_output, str): return None
    cleaned= llm_output.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except:
        return None


@quiz_bp.route("/estimate-many", methods=["POST"])
def estimate_many_prompts():
    username= request.headers.get("X-Username")
    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    assignments = payload.get("assignments", [])
    if not isinstance(assignments, list):
        return jsonify({"error": "assignments must be a list"}), 400
    total_estimated_tokens = 0
    details= []

    for assignment_id in assignments:
        teacher_spec= load_teacher_spec_user(username, assignment_id)
        code_summaries= load_code_summaries_user(username, assignment_id)

        if not teacher_spec or not code_summaries:
            details.append({
                "assignment_id": assignment_id,
                "status": "skipped",
                "reason": "missing teacher specs or code summaries",
                "estimated_tokens": 0
            })
            continue

        prompt= build_prompt(teacher_spec, code_summaries)
        # Lightweight planning estimate (approx. 1 token per 4 chars), not exact billed usage.
        est_tokens= math.ceil(len(prompt)/ 4) if prompt else 0
        total_estimated_tokens += est_tokens
        details.append({
            "assignment_id": assignment_id,
            "status": "ok",
            "estimated_tokens": est_tokens
        })

    return jsonify({
        "status": "ok",
        # Sum across selected assignments to show expected input size before generation.
        "total_estimated_tokens": total_estimated_tokens,
        "assignments_requested": len(assignments),
        "details": details
    }), 200

@quiz_bp.route("/generate/<assignment_id>", methods=["POST"])
def generate_quiz_route(assignment_id):
    username= request.headers.get("X-Username")
    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Φόρτωση από φάκελο χρήστη
        teacher_spec= load_teacher_spec_user(username, assignment_id)
        code_summaries= load_code_summaries_user(username, assignment_id)
        if not teacher_spec:
            return jsonify({"error": "Missing teacher specs"}), 400
        if not code_summaries:
            return jsonify({"error": "Missing code summaries"}), 400

        prompt= build_prompt(teacher_spec, code_summaries)
        
        # Κλήση LLM
        raw_response= generate_quiz(prompt)
        quiz_data= clean_and_parse_json(raw_response)
        if not quiz_data:
            return jsonify({"error": "Invalid LLM response", "raw": str(raw_response)}), 500

        aiken_text= convert_quiz_to_aiken(quiz_data)
        # Αποθήκευση σε φάκελο χρήστη
        save_quiz_text_user(aiken_text, username, assignment_id)
        return jsonify({
            "status": "ok",
            "quiz_json": quiz_data,
            "aiken": aiken_text
        }), 200

    except Exception as e:
        print(f"server error: {e}")
        return jsonify({"error": str(e)}), 500

@quiz_bp.route("/aiken/<assignment_id>", methods=["GET"])
def get_aiken_quiz(assignment_id):
    username= request.headers.get("X-Username")
    if not username: return jsonify({"error": "Unauthorized"}), 401

    # Εύρεση αρχείου Aiken στον φάκελο χρήστη
    try:
        # αν το file_handler έχει save_quiz_text_user στο data/quizzes/...
        from pathlib import Path
        quiz_path= Path(f"data/quizzes/{username}/{assignment_id}.aiken.txt")
        
        if quiz_path.exists():
            with open(quiz_path, "r", encoding="utf-8") as f:
                content= f.read()
            return jsonify({"aiken": content}), 200
        else:
            return jsonify({"error": "Quiz not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

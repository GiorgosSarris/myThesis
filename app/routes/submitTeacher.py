# app/routes/submitTeacher.py

from flask import Blueprint, request, jsonify
from app.utils.file_handler import (
    save_teacher_spec_user,
    list_user_assignments
)

teacher_bp = Blueprint("teacher_bp", __name__)


@teacher_bp.route("/submit-many", methods=["POST"])
def submit_teacher_specs_many():
    username= request.headers.get("X-Username")
    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    data= request.json
    assignments= data.get("assignments", [])
    
    if not assignments:
        return jsonify({"error": "No assignments provided"}), 400

    spec_data= {
        "title": data.get("title"),
        "assignment": data.get("assignment"),
        "quiz_specs": data.get("quiz_specs")
    }
    count= 0
    errors= []
    
    for assign_id in assignments:
        try:
            save_teacher_spec_user(username, assign_id, spec_data)
            count+= 1
        except Exception as e:
            errors.append(f"{assign_id}: {str(e)}")

    return jsonify({
        "status": "ok", 
        "applied_count": count,
        "errors": errors if errors else None
    }), 200


@teacher_bp.route("/submit-all", methods=["POST"])
def submit_teacher_specs_all():
    username= request.headers.get("X-Username")
    if not username:
        return jsonify({"error": "Unauthorized"}), 401
    assignments= list_user_assignments(username)
    
    if not assignments:
        return jsonify({"error": "No assignments found"}), 404
    
    data= request.json
    spec_data= {
        "title": data.get("title"),
        "assignment": data.get("assignment"),
        "quiz_specs": data.get("quiz_specs")
    }
    count= 0
    errors= []
    
    for assign_id in assignments:
        try:
            save_teacher_spec_user(username, assign_id, spec_data)
            count+= 1
        except Exception as e:
            errors.append(f"{assign_id}: {str(e)}")
    
    return jsonify({
        "status": "ok",
        "applied_count": count,
        "total_assignments": len(assignments),
        "errors": errors if errors else None
    }), 200
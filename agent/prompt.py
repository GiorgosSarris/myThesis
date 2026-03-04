from typing import List, Dict

def build_prompt(teacher_spec: Dict[str, str], code_summaries: List[str],) ->str:
    prompt=(
        "generate a programming quiz based on:\n"
        "- The instructor's assignment description and quiz requirements.\n"
        "- The student's submitted code(analyzed below).\n"
    )
    #assignment description and teacher's requirements
    prompt+= f"Assignment Title: {teacher_spec.get('title', 'Untitled Task')}\n"
    prompt+= f"Assignment Description:\n{teacher_spec.get('assignment', 'No description provided.')}\n\n"
    prompt+= f"Quiz Focus:\n{teacher_spec.get('quiz_specs', 'No quiz focus provided.')}\n\n"

    #AST summaries
    if code_summaries:
        prompt+="Student's Code Analysis:\n"
        for i, summary in enumerate(code_summaries, start=1):
            prompt+= f"File {i} Summary:\n{summary.strip()}\n"
    else:
        prompt+="No code files were provided.\n"

    prompt+= (
        "\nIMPORTANT-Output Format:\n"
        "Return ONLY a valid JSON array with NO markdown code blocks, NO explanations.\n"
        "Each question object must have this EXACT structure:\n"
        "{\n"
        '  "question": "Η ερώτηση στα ελληνικά;",\n'
        '  "choices": ["Α. Πρώτη επιλογή", "Β. Δεύτερη επιλογή", "Γ. Τρίτη επιλογή", "Δ. Τέταρτη επιλογή"],\n'
        '  "answer": "Α"\n'
        "}\nor\n"
        "{\n"
        '  "question": "Η ερώτηση στα ελληνικά;",\n'
        '  "choices": ["Α. Σωστό", "Β. Λάθος"],\n'
        '  "answer": "Α"\n'
        "}\n\n"
        "Rules:\n"
        "-Test deep conceptual understanding of the assignment logic.\n"
        "-Produce one correct answer and three wrong answers in multiple-choice format.\n"
        "-Wrong answers must be realistic distractors based on common logical mistakes.\n"
        "-Distractors must be plausible and logically derived from the student's code.\n"
        "- The 'choices' array should contain ONLY the choice text WITHOUT letter prefixes (no Α., Β., etc).\n"
        "-Avoid syntax trivia and focus on algorithmic reasoning.\n"
        "-All questions and answers must be in clear,correct Greek language.\n"
        "-The 'answer' field must contain between 2 to 6 letters depending on the question(True/False, 4-5 or 6 answer-multiple choice). (Α, Β, Γ, Δ, Ε or Ζ).\n"
    )


    return prompt

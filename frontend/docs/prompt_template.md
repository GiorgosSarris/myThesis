Generate a programming quiz based on:
- The instructor's assignment description and quiz requirements.
- The student's submitted code (analyzed below).
Assignment Title: (value from Step 2 -> Title)
Assignment Description: (value from Step 2 -> Description)
Quiz Focus: (value from Step 2 -> Quiz Requirements)

Student's Code Analysis:
File 1 Summary: (parsed code summary from uploaded files)
File 2 ...

IMPORTANT - Output Format:
Return ONLY a valid JSON array with NO markdown code blocks, NO explanations.
Each question object must have this EXACT structure:
{
  "question": "Η ερώτηση στα ελληνικά;",
  "choices": ["Α. Πρώτη επιλογή", "Β. Δεύτερη επιλογή", "Γ. Τρίτη επιλογή", "Δ. Τέταρτη επιλογή"],
  "answer": "Α"
}
or
{
  "question": "Η ερώτηση στα ελληνικά;",
  "choices": ["Α. Σωστό", "Β. Λάθος"],
  "answer": "Α"
}
Rules:
-Test deep conceptual understanding of the assignment logic.
-Produce one correct answer and three wrong answers in multiple-choice format.
-Wrong answers must be realistic distractors based on common logical mistakes.
-Distractors must be plausible and logically derived from the student's code.
- The 'choices' array should contain ONLY the choice text WITHOUT letter prefixes (no Α., Β., etc).
-Avoid syntax trivia and focus on algorithmic reasoning.
-All questions and answers must be in clear,correct Greek language.
-The 'answer' field must contain between 2 to 6 letters depending on the question(True/False, 4-5 or 6 answer-multiple choice). (Α, Β, Γ, Δ, Ε or Ζ).

import streamlit as st
import requests
import os
from pathlib import Path

BASE_URL= "http://127.0.0.1:5000"
st.set_page_config(page_title="CognitoCode", layout="wide", initial_sidebar_state="collapsed")
PROJECT_ROOT= Path(__file__).parent.parent
FRONTEND_DOCS_DIR = PROJECT_ROOT / "frontend" / "docs"


# USER MANAGEMENT
def load_users():
    try:
        from config import USERS
        return USERS
    except:
        return {"admin": "admin123"}

def save_user(username, password):
    users= load_users()
    users[username] = password
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    with open(config_path, "w") as f:
        f.write('"""User authentication"""\nUSERS = {\n')
        for u, p in users.items():
            f.write(f'    "{u}": "{p}",\n')
        f.write('}\n')

def validate_user(username, password):
    return load_users().get(username)== password


# LOGIN
if 'username' not in st.session_state:
    st.markdown("<h1 style='text-align: center;'> CognitoCode</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>AI-Powered Quiz Generator</p>", unsafe_allow_html=True)
    st.markdown("---")
    tab1, tab2= st.tabs(["Login", "Register"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True, type="primary"):
                if validate_user(username, password):
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            new_user = st.text_input("Username", key="reg_user")
            new_pass = st.text_input("Password", type="password", key="reg_pass")
            new_pass2 = st.text_input("Confirm", type="password", key="reg_pass2")
            if st.button("Register", use_container_width=True, type="primary"):
                if not new_user or not new_pass:
                    st.error("Fill all fields")
                elif new_pass != new_pass2:
                    st.error("Passwords don't match")
                elif new_user in load_users():
                    st.error("Username exists")
                else:
                    save_user(new_user, new_pass)
                    st.success("Registration successful! Please login.")
    st.stop()


# HELPERS
username= st.session_state.username

def list_assignments():
    path = PROJECT_ROOT / "data" / "uploads" / username
    if not path.exists():
        return []
    return sorted([f.name for f in path.iterdir() if f.is_dir()])

def api_call(method, endpoint, **kwargs):
    # Add username header
    kwargs.setdefault('headers', {})['X-Username'] = username
    try:
        r = getattr(requests, method)(f"{BASE_URL}/{endpoint}", **kwargs)
        if r.status_code == 200:
            return r.json(), None
        else:
            return None, f"Error {r.status_code}: {r.text[:200]}"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to backend"
    except ValueError:
        return None, f"Invalid response: {r.text[:200]}"
    except Exception as e:
        return None, str(e)


def load_doc_file(filename, fallback):
    path = FRONTEND_DOCS_DIR / filename
    if not path.exists():
        return fallback
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return fallback

# HEADER
col1, col2= st.columns([4, 1])
with col1:
    st.title("CognitoCode")
with col2:
    st.caption(f" {username}")
    if st.button("Logout", use_container_width=True):
        del st.session_state.username
        st.rerun()
st.markdown("---")

docs_col1, docs_col2, docs_col3 = st.columns([1, 1, 4])
with docs_col1:
    if st.button("Show Prompt", use_container_width=True):
        st.session_state.show_prompt_help = not st.session_state.get("show_prompt_help", False)
with docs_col2:
    if st.button("Usage Guide", use_container_width=True):
        st.session_state.show_usage_help = not st.session_state.get("show_usage_help", False)

if st.session_state.get("show_prompt_help", False):
    prompt_doc= load_doc_file(
        "prompt_template.md",
        "Prompt template file not found: frontend/docs/prompt_template.md")
    st.subheader("Prompt Template (with dynamic placeholders)")
    st.code(prompt_doc, language="markdown")

if st.session_state.get("show_usage_help", False):
    usage_doc= load_doc_file(
        "usage_guide.md",
        "Usage guide file not found: frontend/docs/usage_guide.md")
    st.subheader("How To Use CognitoCode")
    st.markdown(usage_doc)

# MAIN WORKFLOW

# Step indicators
step_col1, step_col2, step_col3 = st.columns(3)
with step_col1:
    st.markdown("### 1. Upload Code")
with step_col2:
    st.markdown("### 2. Set Specs")
with step_col3:
    st.markdown("### 3. Generate Quiz")

st.markdown("---")


# 1: UPLOAD
st.header("Step 1: Upload Student Code")

col1, col2= st.columns([2, 1])

with col1:
    uploaded_file= st.file_uploader("Select ZIP file", type=["zip"])
    if uploaded_file:
        if st.button("Upload & Parse", type="primary", use_container_width=True):
            with st.spinner("Processing..."):
                result, error = api_call("post", "student/upload", files={"file": uploaded_file})
                
                if result:
                    st.success(f"Success! Assignment: `{result['assignment_id']}`")
                    st.info(f"Parsed {result['files_parsed']} files")
                    st.rerun()
                else:
                    st.error(f" {error}")
with col2:
    st.subheader("Your Uploads")
    assignments = list_assignments()
    
    if assignments:
        st.metric("Total", len(assignments))
        with st.expander("View All"):
            for a in assignments:
                st.text(f"• {a}")
    else:
        st.info("No uploads yet")
st.markdown("---")


# 2: SPECS
st.header("Step 2: Assignment Specifications")

assignments= list_assignments()

if not assignments:
    st.warning("Upload code first")
else:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        title = st.text_input(
            "Title",
            placeholder="Insert the assignment's title (e.g., OOP Project)",
            help="Use a short, clear title for the assignment."
        )
        description = st.text_area(
            "Description",
            height=120,
            placeholder="Add the full assignment statement/instructions for students. Describe the task, expected behavior, constraints, and deliverables.",
            help="This is the assignment brief the model will use as teaching context."
        )
        quiz_specs = st.text_area(
            "Quiz Requirements",
            height=110,
            placeholder="How many questions should the quiz have? Should it be multiple-choice or true/false? Do you want questions to focus on something specific (e.g., general concepts, recursion, edge cases, complexity)?",
            help="Define quiz format and focus areas so generated questions match your goals."
        )
    with col2:
        st.subheader("Target")
        apply_mode = st.radio("Apply to:", ["All", "Selected"], label_visibility="collapsed")
        
        if apply_mode == "Selected":
            selected = st.multiselect("Assignments:", assignments)
        else:
            selected = assignments
            st.info(f"{len(assignments)} assignments")
    
    if st.button("Apply Specifications", type="primary", use_container_width=True):
        if not selected:
            st.error("No assignments selected")
        elif not title or not description:
            st.warning("Fill title and description")
        else:
            payload = {
                "assignments": selected,
                "title": title,
                "assignment": description,
                "quiz_specs": quiz_specs
            }
            
            with st.spinner("Applying..."):
                endpoint = "teacher/submit-all" if apply_mode == "All" else "teacher/submit-many"
                result, error = api_call("post", endpoint, json=payload)
                
                if result:
                    st.success(f"Applied to {result['applied_count']} assignments")
                else:
                    st.error(f"{error}")
st.markdown("---")


# 3: GENERATE
st.header("Step 3: Generate Quiz")
assignments= list_assignments()

if not assignments:
    st.warning("Complete steps 1-2 first")
else:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        gen_mode = st.radio("Generate for:", ["All Assignments", "Selected Only"], label_visibility="collapsed")
        
        if gen_mode == "Selected Only":
            gen_selected = st.multiselect("Choose:", assignments, key="gen_sel")
        else:
            gen_selected = assignments
    targets = gen_selected if gen_mode == "Selected Only" else assignments
    with col2:
        st.metric("Will Generate", len(targets))
        if targets:
            signature = "|".join(sorted(targets))
            # Recalculate estimate only when selected assignment set changes.
            if st.session_state.get("gen_estimate_signature") != signature:
                result, error = api_call("post", "quiz/estimate-many", json={"assignments": targets})
                st.session_state.gen_estimate_signature = signature
                st.session_state.gen_estimate_result = result
                st.session_state.gen_estimate_error = error

            gen_estimate = st.session_state.get("gen_estimate_result")
            gen_estimate_error = st.session_state.get("gen_estimate_error")
            if gen_estimate and gen_estimate.get("status") == "ok":
                # Display estimate (approximate input tokens) before LLM call.
                st.metric("Est. Input Tokens", f"~{gen_estimate['total_estimated_tokens']:,}")
                st.caption("Real-time estimate based on selected assignments.")
            else:
                st.caption(f"Estimate unavailable: {gen_estimate_error or 'unknown error'}")
  
    if st.button("Generate Quiz", type="primary", use_container_width=True):
        if gen_mode == "Selected Only" and not gen_selected:
            st.error("Select assignments")
        else:
            progress= st.progress(0)
            status= st.empty()
            results= []
            for i, ass_id in enumerate(targets):
                status.text(f"Generating {i+1}/{len(targets)}: {ass_id}")
                result, error= api_call("post", f"quiz/generate/{ass_id}")
                
                if result:
                    results.append({"id": ass_id, "status": "ok", "questions": len(result.get("quiz_json", []))})
                else:
                    results.append({"id": ass_id, "status": "error", "error": error})
                progress.progress((i+1)/ len(targets))   
            progress.empty()
            status.empty()
            success= sum(1 for r in results if r["status"] == "ok")
            st.success(f"Generated {success}/{len(targets)} quizzes")
            
            with st.expander("Details"):
                for r in results:
                    if r["status"] == "ok":
                        st.write(f" {r['id']}: {r['questions']} questions")
                    else:
                        st.write(f" {r['id']}: {r['error']}")
st.markdown("---")


# 4: VIEW/DOWNLOAD
st.header("View & Download")
assignments= list_assignments()

if assignments:
    selected_view = st.selectbox("Select assignment:", assignments)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("View Aiken", use_container_width=True, type="primary"):
            result, error = api_call("get", f"quiz/aiken/{selected_view}")
            
            if result and "aiken" in result:
                st.code(result["aiken"], language="text")
                st.download_button(
                    "Download",
                    data=result["aiken"],
                    file_name=f"{selected_view}.txt",
                    mime="text/plain"
                )
            else:
                st.warning("Quiz not generated yet" if not error else error)
    
    with col2:
        if st.button("Delete Assignment", use_container_width=True):
            st.warning("Delete feature coming soon")
else:
    st.info("No assignments to view")
st.markdown("---")
st.caption("CognitoCode - AI-Powered Quiz Generator")

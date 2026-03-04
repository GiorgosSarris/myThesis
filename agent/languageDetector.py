import os
import re

EXTENSION_LANGUAGE_MAP={
    ".py":"python",
    ".c":"c",
    ".cpp":"cpp",
    ".hpp":"cpp",
    ".java":"java",
    ".js":"javascript",
    ".sql":"sql",
    ".vhd":"vhdl",
    ".asm":"mips", 
}

#check keywords to define the language if the extension is not found
LANGUAGE_KEYWORDS={ 
    "python": [r"def\s+", r"import\s+", r"class\s+"],
    "c": [r"#include\s+<", r"int\s+main\s*\("],
    "cpp": [r"#include\s+<", r"std::", r"int\s+main\s*\("],
    "java": [r"public\s+class", r"System\.out\.println"],
    "javascript": [r"function\s*\(", r"console\.log"],
    "sql": [r"SELECT\s+", r"INSERT\s+", r"CREATE\s+TABLE"],
    "vhdl": [r"entity\s+", r"architecture\s+", r"signal\s+"],
    "mips": [r"\badd\b", r"\bsub\b", r"\bj\b", r"\blw\b", r"\bsw\b"],
}

#detecting by file extension
def detect_extension(file_path: str)->str:
    _, ext=os.path.splitext(file_path)
    return EXTENSION_LANGUAGE_MAP.get(ext.lower(), "unknown")# return language or unknown

#detecting by content analysis
def detect_content(code_text:str)->str:
    for i, (language, patterns) in enumerate(LANGUAGE_KEYWORDS.items()):
        for pattern in patterns:
            if re.search(pattern, code_text, re.IGNORECASE):# case insensitive search
                return language     
    return "unknown"  
            

#main function using both methods
def detect_language(file_path: str, file_content: str)->str:
   #check by extension first
    candidate_lang=detect_extension(file_path)
    # if still unknown use content
    if candidate_lang=="unknown":
        candidate_lang=detect_content(file_content)

    return candidate_lang

from tree_sitter import Language, Parser
import os
import tree_sitter_python as tspython
import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter_java as tsjava
import tree_sitter_javascript as tsjs

#initialize languages
try:
    PY_LANGUAGE = Language(tspython.language())
    C_LANGUAGE = Language(tsc.language())
    CPP_LANGUAGE = Language(tscpp.language())
    JAVA_LANGUAGE = Language(tsjava.language())
    JS_LANGUAGE = Language(tsjs.language())
except Exception:
    PY_LANGUAGE = Language(tspython.language)
    C_LANGUAGE = Language(tsc.language)
    CPP_LANGUAGE = Language(tscpp.language)
    JAVA_LANGUAGE = Language(tsjava.language)
    JS_LANGUAGE = Language(tsjs.language)


def get_parser(lang_object):
    try:
        return Parser(lang_object)
    except TypeError:
        #fallback for older tree-sitter versions
        parser= Parser()
        parser.set_language(lang_object)
        return parser
    except Exception as e:
        print(f"Parser error: {e}")
        return None


def parse_code(language: str, file_path: str) -> dict:
    if language == "python":
        return parse_python(file_path)
    elif language == "c":
        return parse_c(file_path)
    elif language == "cpp":
        return parse_cpp(file_path)
    elif language == "java":
        return parse_java(file_path)
    elif language == "javascript":
        return parse_javascript(file_path)
    return {"error": f"Unsupported language: {language}"}


def parse_python(file_path: str) -> dict:
    parser = get_parser(PY_LANGUAGE)
    INTERESTING = {
        "module": "module",
        "function_definition": "function",
        "class_definition": "class",
        "decorated_definition": "decorator",
        "call": "call",
        "import_statement": "import",
        "import_from_statement": "import_from",
        "assignment": "assign",
        "augmented_assignment": "aug_assign",
        "for_statement": "for",
        "while_statement": "while",
        "if_statement": "if",
        "try_statement": "try",
        "except_clause": "except",
        "return_statement": "return",
        "comparison_operator": "compare",
        "binary_operator": "binop",
        "boolean_operator": "boolop",
        "list_comprehension": "list_comp",
        "dictionary_comprehension": "dict_comp"
    }
    return _generic_parse(parser, file_path, "python", INTERESTING)


def parse_c(file_path: str) -> dict:
    parser = get_parser(C_LANGUAGE)
    INTERESTING = {
        "translation_unit": "module",
        "function_definition": "function",
        "struct_specifier": "struct",
        "call_expression": "call",
        "declaration": "declaration",
        "for_statement": "for",
        "while_statement": "while",
        "if_statement": "if",
        "return_statement": "return"
    }
    return _generic_parse(parser, file_path, "c", INTERESTING)


def parse_cpp(file_path: str) -> dict:
    parser = get_parser(CPP_LANGUAGE)
    INTERESTING = {
        "translation_unit": "module",
        "function_definition": "function",
        "class_specifier": "class",
        "namespace_definition": "namespace",
        "call_expression": "call",
        "for_statement": "for",
        "if_statement": "if",
        "return_statement": "return"
    }
    return _generic_parse(parser, file_path, "cpp", INTERESTING)


def parse_java(file_path: str) -> dict:
    parser = get_parser(JAVA_LANGUAGE)
    INTERESTING = {
        "program": "module",
        "class_declaration": "class",
        "method_declaration": "function",
        "method_invocation": "call",
        "for_statement": "for",
        "if_statement": "if",
        "return_statement": "return"
    }
    return _generic_parse(parser, file_path, "java", INTERESTING)


def parse_javascript(file_path: str) -> dict:
    parser = get_parser(JS_LANGUAGE)
    INTERESTING = {
        "program": "module",
        "function_declaration": "function",
        "function_expression": "function",
        "arrow_function": "function",
        "class_declaration": "class",
        "method_definition": "function",
        "call_expression": "call",
        "variable_declarator": "declaration",
        "if_statement": "if",
        "for_statement": "for",
        "return_statement": "return"
    }
    return _generic_parse(parser, file_path, "javascript", INTERESTING)


def _generic_parse(parser, file_path, lang_name, interesting_types):
    if parser is None:
        return {"error": f"Parser failed for {lang_name}", "file": os.path.basename(file_path)}
    
    try:
        with open(file_path, "rb") as f:
            source_code= f.read()
        
        tree= parser.parse(source_code)
        if not tree.root_node:
            return {"language": lang_name, "file": os.path.basename(file_path), "ast": {}}
        
        def extract_name(node, source):
            # Extract name/identifier from node
            for field in ['name', 'declarator', 'function']:
                target= node.child_by_field_name(field)
                if target:
                    text= source[target.start_byte:target.end_byte].decode('utf-8', errors='ignore')
                    return text.split('.')[-1].split('(')[0].strip()
            # Fallback: look for identifier child
            for child in node.children:
                if child.type== "identifier":
                    text= source[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
                    return text.strip()
            return None
        
        def extract_details(node, source):
            # Get text
            text= source[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')
            # Clean whitespace
            text= ' '.join(text.split())
            # Truncate
            if len(text)> 80:
                text= text[:77] + "..."
            return text
        
        def parse_node(node, depth=0):
            node_type = node.type
            # Check if node is interesting
            if node_type in interesting_types:
                node_dict = {
                    "type": interesting_types[node_type],
                    "name": extract_name(node, source_code),
                    "details": extract_details(node, source_code) if depth > 0 else None,
                    "children": []
                }
                # if interesting, parse children with increased depth
                for child in node.children:
                    child_res = parse_node(child, depth + 1)
                    if child_res:
                        if isinstance(child_res, list):
                            node_dict["children"].extend(child_res)
                        else:
                            node_dict["children"].append(child_res)
                return node_dict
            # else, parse children at same depth
            collected= []
            for child in node.children:
                child_res= parse_node(child, depth)
                if child_res:
                    if isinstance(child_res, list):
                        collected.extend(child_res)
                    else:
                        collected.append(child_res)
            return collected if collected else None
        
        ast_result= parse_node(tree.root_node)
        return {
            "language": lang_name,
            "file": os.path.basename(file_path),
            "ast": ast_result if ast_result else {}
        }
    # parsing errors
    except Exception as e:
        return {
            "language": lang_name,
            "file": os.path.basename(file_path),
            "ast": {},
            "error": str(e)
        }


def create_llm_summary(parsed: dict, max_depth: int = 3) -> str:
    if "error" in parsed:
        return f"[{parsed.get('file', 'unknown')}] Error: {parsed['error']}"
    
    file_name= parsed.get('file', 'unknown')
    lines= [f"[{file_name}]"]
    def format_tree(node, depth=0, max_depth=max_depth):
        if not isinstance(node, dict) or depth> max_depth:
            return []
        
        node_type= node.get("type")
        name= node.get("name")
        details= node.get("details")
        # If module/program, process children directly
        if node_type in ["module", "program"]:
            result= []
            for child in node.get("children", []):
                result.extend(format_tree(child, depth, max_depth))
            return result
        
        # Format current node
        indent= "  "* depth
        if name:
            line= f"{indent}- {node_type} {name}"
        else:
            line= f"{indent}- {node_type}"
        
        # Add code details for important nodes
        if details and node_type in ["if", "for", "while", "compare", "call", "assign"]:
            line+= f": {details}"
        result= [line]
        
        # Recursively format children
        children= node.get("children", [])
        if children and depth< max_depth:
            for child in children[:15]:  #limit to 15 children per node
                result.extend(format_tree(child, depth + 1, max_depth))
        return result
    
    tree_lines= format_tree(parsed.get("ast"))
    if not tree_lines:
        return f"[{file_name}] (empty or unparseable)"
    
    lines.extend(tree_lines[:60])  #limit to 60 lines per file
    return "\n".join(lines)
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import ast


def list_directory_structure(path: str = ".", max_depth: int = 3) -> Dict:
    """
    List the directory structure of the project.

    Args:
        path: Root path to scan (default: current directory)
        max_depth: Maximum depth to traverse

    Returns:
        Dictionary representing the directory structure
    """
    def _scan_dir(current_path: Path, current_depth: int) -> Dict:
        if current_depth > max_depth:
            return {"type": "directory", "name": current_path.name, "children": {"...": {"type": "comment", "message": f"Depth limit reached"}}}

        result = {"type": "directory", "name": current_path.name, "children": {}}

        try:
            for item in sorted(current_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    result["children"][item.name] = _scan_dir(item, current_depth + 1)
                elif item.is_file():
                    result["children"][item.name] = {"type": "file", "name": item.name}
        except PermissionError:
            result["error"] = "Permission denied"

        return result

    root_path = Path(path).resolve()
    return _scan_dir(root_path, 0)


def read_code_file(file_path: str, start_line: int = None, end_line: int = None) -> Optional[str]:
    """
    Read the content of a code file.

    Args:
        file_path: Path to the file to read
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)

    Returns:
        String content of the file or specified lines
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if start_line is not None and end_line is not None:
            # Adjust for 0-based indexing
            start_idx = max(0, start_line - 1)
            end_idx = min(len(lines), end_line)
            return ''.join(lines[start_idx:end_idx])
        elif start_line is not None:
            # Just read around the specific line (10 lines of context)
            start_idx = max(0, start_line - 6)  # 5 before + current line
            end_idx = min(len(lines), start_line + 5)  # 5 after
            result_lines = []
            for i in range(start_idx, end_idx):
                line_num = i + 1
                marker = ">>> " if i == start_line - 1 else f"{line_num:3d}: "
                result_lines.append(f"{marker}{lines[i]}")
            return ''.join(result_lines)
        else:
            return ''.join(lines)
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"


def search_codebase(pattern: str, file_extensions: List[str] = None, search_content: bool = True) -> List[Dict]:
    """
    Search for files containing a specific pattern.

    Args:
        pattern: Text pattern to search for
        file_extensions: List of file extensions to search (e.g., ['.py', '.js'])
        search_content: Whether to search file contents or just filenames

    Returns:
        List of dictionaries with file paths and matched lines
    """
    if file_extensions is None:
        file_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json', '.txt', '.md']

    results = []

    for root, dirs, files in os.walk('.'):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    if search_content and pattern.lower() in content.lower():
                        # Find the lines containing the pattern
                        lines = content.split('\n')
                        matched_lines = []
                        for i, line in enumerate(lines):
                            if pattern.lower() in line.lower():
                                matched_lines.append({
                                    'line_number': i + 1,
                                    'content': line.strip()
                                })

                        results.append({
                            'file_path': file_path,
                            'matched_lines': matched_lines
                        })
                    elif not search_content and pattern.lower() in file.lower():
                        results.append({
                            'file_path': file_path,
                            'matched_lines': []
                        })
                except Exception:
                    continue  # Skip files that can't be read

    return results


def run_shell_command(command: str, timeout: int = 30) -> Dict[str, str]:
    """
    Safely run a shell command.

    Args:
        command: Command to execute
        timeout: Timeout in seconds

    Returns:
        Dictionary with stdout, stderr, and return code
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode,
            'command': command
        }
    except subprocess.TimeoutExpired:
        return {
            'stdout': '',
            'stderr': 'Command timed out',
            'return_code': -1,
            'command': command
        }
    except Exception as e:
        return {
            'stdout': '',
            'stderr': f'Error executing command: {str(e)}',
            'return_code': -1,
            'command': command
        }


def analyze_python_code(file_path: str) -> Dict:
    """
    Analyze Python code structure using AST.

    Args:
        file_path: Path to Python file to analyze

    Returns:
        Dictionary with code structure information
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'variables': []
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis['functions'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args]
                })
            elif isinstance(node, ast.ClassDef):
                analysis['classes'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    analysis['imports'].append({
                        'name': alias.name,
                        'alias': alias.asname
                    })
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        analysis['variables'].append({
                            'name': target.id,
                            'line': node.lineno
                        })

        return analysis
    except Exception as e:
        return {'error': f'Could not analyze {file_path}: {str(e)}'}

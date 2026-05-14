"""
Execution Sandbox — Safe multi-language runtime execution

Provides isolated environments for executing code in Python, JS/TS, Go, Rust,
Java, C/C++, Ruby, PHP, C#, and SQL. Uses Docker containerization with strict
resource limits, filesystem isolation, and network restrictions.
"""

import os
import json
import tempfile
import subprocess
import shutil
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum


class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    CPP = "cpp"
    CSHARP = "csharp"
    SQL = "sql"


@dataclass
class SandboxConfig:
    image: str
    timeout: int = 30
    memory_limit_mb: int = 512
    cpu_limit: float = 1.0
    network_enabled: bool = False
    allowed_imports: List[str] = None
    workdir: str = "/workspace"


LANGUAGE_CONFIGS = {
    Language.PYTHON: SandboxConfig(
        image="python:3.12-slim",
        timeout=30,
        memory_limit_mb=512,
        allowed_imports=["pytest", "unittest", "json", "math", "os", "sys", "typing", "collections", "datetime", "re", "itertools", "functools"],
    ),
    Language.JAVASCRIPT: SandboxConfig(
        image="node:20-slim",
        timeout=30,
        memory_limit_mb=512,
    ),
    Language.TYPESCRIPT: SandboxConfig(
        image="node:20-slim",
        timeout=30,
        memory_limit_mb=512,
    ),
    Language.GO: SandboxConfig(
        image="golang:1.22",
        timeout=45,
        memory_limit_mb=512,
    ),
    Language.RUST: SandboxConfig(
        image="rust:1.78-slim",
        timeout=60,
        memory_limit_mb=1024,
        cpu_limit=2.0,
    ),
    Language.JAVA: SandboxConfig(
        image="openjdk:21-slim",
        timeout=45,
        memory_limit_mb=1024,
    ),
    Language.CPP: SandboxConfig(
        image="gcc:14-bookworm",
        timeout=45,
        memory_limit_mb=512,
    ),
    Language.RUBY: SandboxConfig(
        image="ruby:3.3-slim",
        timeout=30,
        memory_limit_mb=512,
    ),
    Language.PHP: SandboxConfig(
        image="php:8.3-cli",
        timeout=30,
        memory_limit_mb=512,
    ),
    Language.CSHARP: SandboxConfig(
        image="mcr.microsoft.com/dotnet/sdk:8.0",
        timeout=60,
        memory_limit_mb=1024,
    ),
    Language.SQL: SandboxConfig(
        image="postgres:16-alpine",
        timeout=30,
        memory_limit_mb=512,
    ),
}


@dataclass
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    timed_out: bool = False
    memory_peak_mb: Optional[float] = None
    runtime_snapshot: Optional[Dict[str, Any]] = None


@dataclass
class SandboxFile:
    path: str
    content: str


class ExecutionSandbox:
    def __init__(self, use_docker: bool = True):
        self.use_docker = use_docker
        self._temp_dirs: List[str] = []

    def _detect_language(self, code: str, filename: str = None) -> Language:
        if filename:
            ext = Path(filename).suffix.lower()
            lang_map = {
                ".py": Language.PYTHON,
                ".js": Language.JAVASCRIPT,
                ".ts": Language.TYPESCRIPT,
                ".java": Language.JAVA,
                ".go": Language.GO,
                ".rs": Language.RUST,
                ".php": Language.PHP,
                ".rb": Language.RUBY,
                ".cpp": Language.CPP,
                ".cc": Language.CPP,
                ".cxx": Language.CPP,
                ".cs": Language.CSHARP,
                ".sql": Language.SQL,
            }
            if ext in lang_map:
                return lang_map[ext]
        code_lower = code.lower()
        patterns = [
            (["select ", "insert into", "create table", "alter table", "drop table"], Language.SQL),
            (["import ", "from ", "def ", "class ", "print("], Language.PYTHON),
            (["require(", "module.exports", "export default", "console.log(", "=>"], Language.JAVASCRIPT),
            (["package main", "import (", "func main"], Language.GO),
            (["fn main", "use std::", "let mut"], Language.RUST),
            (["public class", "public static void main", "System.out.println"], Language.JAVA),
            (["#include <", "int main(", "std::cout"], Language.CPP),
            (["def ", "puts ", "module ", "class ", "end"], Language.RUBY),
            (["<?php", "echo "], Language.PHP),
            (["using System", "namespace ", "Console.WriteLine"], Language.CSHARP),

        ]
        for pattern_list, lang in patterns:
            if any(p in code_lower for p in pattern_list):
                return lang
        return Language.PYTHON

    def _get_run_command(self, language: Language, file_path: str, test_command: str = None) -> List[str]:
        if test_command:
            return ["bash", "-c", test_command]
        commands = {
            Language.PYTHON: ["python", file_path],
            Language.JAVASCRIPT: ["node", file_path],
            Language.TYPESCRIPT: ["npx", "ts-node", file_path],
            Language.GO: ["go", "run", file_path],
            Language.RUST: ["cargo", "run"],
            Language.JAVA: ["java", file_path.replace(".java", "")],
            Language.CPP: ["sh", "-c", f"g++ -std=c++17 -o /tmp/out {file_path} && /tmp/out"],
            Language.RUBY: ["ruby", file_path],
            Language.PHP: ["php", file_path],
            Language.CSHARP: ["sh", "-c", f"dotnet run --project {Path(file_path).parent}"],
        }
        return commands.get(language, ["python", file_path])

    def _get_test_command(self, language: Language, file_path: str) -> str:
        test_commands = {
            Language.PYTHON: f"python -m pytest {file_path} -v --tb=short 2>&1 || python -m unittest {file_path} -v 2>&1",
            Language.JAVASCRIPT: f"npx jest {file_path} --verbose 2>&1 || npx mocha {file_path} 2>&1",
            Language.GO: f"go test -v ./... 2>&1",
            Language.RUST: "cargo test --verbose 2>&1",
            Language.JAVA: f"javac {file_path} && java org.junit.runner.JUnitCore {Path(file_path).stem} 2>&1",
            Language.RUBY: f"ruby -I. {file_path} 2>&1",
            Language.PHP: f"phpunit {file_path} 2>&1",
            Language.CSHARP: f"dotnet test --verbosity normal 2>&1",
        }
        return test_commands.get(language, f"python {file_path} 2>&1")

    def execute(self, code: str, language: Language = None, files: List[SandboxFile] = None,
                timeout: int = None, test_command: str = None) -> ExecutionResult:
        if language is None:
            language = self._detect_language(code)
        config = LANGUAGE_CONFIGS.get(language, SandboxConfig(image="python:3.12-slim"))
        timeout = timeout or config.timeout

        temp_dir = tempfile.mkdtemp(prefix="sandbox_")
        self._temp_dirs.append(temp_dir)

        try:
            main_file = self._write_files(temp_dir, code, language, files or [])
            result = self._run_in_sandbox(temp_dir, main_file, language, config, timeout, test_command)
            return result
        finally:
            self._cleanup_later(temp_dir)

    def execute_test(self, code: str, test_code: str, language: Language = None) -> ExecutionResult:
        if language is None:
            language = self._detect_language(code)

        files = [
            SandboxFile(path="test_main.py" if language == Language.PYTHON else "test_main.rs" if language == Language.RUST else "test_main.go" if language == Language.GO else "test_main.js" if language == Language.JAVASCRIPT else "TestMain.java" if language == Language.JAVA else "test_main.rb" if language == Language.RUBY else "test_main.php" if language == Language.PHP else "test_main.cs" if language == Language.CSHARP else "test_main.cpp" if language == Language.CPP else "test.sql" if language == Language.SQL else "test_main.py", content=test_code),
            SandboxFile(path="main.py" if language == Language.PYTHON else "main.rs" if language == Language.RUST else "main.go" if language == Language.GO else "main.js" if language == Language.JAVASCRIPT else "Main.java" if language == Language.JAVA else "main.rb" if language == Language.RUBY else "main.php" if language == Language.PHP else "Main.cs" if language == Language.CSHARP else "main.cpp" if language == Language.CPP else "schema.sql" if language == Language.SQL else "main.py", content=code),
        ]
        return self.execute(code, language, files=files, test_command=self._get_test_command(language, "test_main.py"))

    def _write_files(self, temp_dir: str, code: str, language: Language, extra_files: List[SandboxFile]) -> str:
        ext_map = {
            Language.PYTHON: "main.py",
            Language.JAVASCRIPT: "main.js",
            Language.TYPESCRIPT: "main.ts",
            Language.GO: "main.go",
            Language.RUST: "src/main.rs",
            Language.JAVA: "Main.java",
            Language.CPP: "main.cpp",
            Language.RUBY: "main.rb",
            Language.PHP: "main.php",
            Language.CSHARP: "main.cs",
            Language.SQL: "query.sql",
        }
        main_filename = ext_map.get(language, "main.py")
        main_path = os.path.join(temp_dir, main_filename)

        if language == Language.RUST:
            os.makedirs(os.path.join(temp_dir, "src"), exist_ok=True)
            main_path = os.path.join(temp_dir, "src", "main.rs")
            with open(os.path.join(temp_dir, "Cargo.toml"), "w") as f:
                f.write('[package]\nname = "sandbox"\nversion = "0.1.0"\nedition = "2021"\n')
        elif language == Language.CSHARP:
            os.makedirs(os.path.join(temp_dir, "project"), exist_ok=True)
            main_path = os.path.join(temp_dir, "project", "Program.cs")

        with open(main_path, "w") as f:
            f.write(code)

        for sf in extra_files:
            file_path = os.path.join(temp_dir, sf.path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(sf.content)

        return main_path

    def _run_in_sandbox(self, temp_dir: str, main_file: str, language: Language,
                        config: SandboxConfig, timeout: int, test_command: str) -> ExecutionResult:
        if not self.use_docker or not self._docker_available():
            return self._run_local(temp_dir, main_file, language, timeout, test_command)

        return self._run_docker(temp_dir, main_file, language, config, timeout, test_command)

    def _run_local(self, temp_dir: str, main_file: str, language: Language,
                   timeout: int, test_command: str) -> ExecutionResult:
        start = time.time()
        try:
            rel_path = os.path.relpath(main_file, temp_dir)
            cmd = self._get_run_command(language, rel_path, test_command)
            proc = subprocess.run(
                cmd,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            duration = int((time.time() - start) * 1000)
            return ExecutionResult(
                success=proc.returncode == 0,
                stdout=proc.stdout,
                stderr=proc.stderr,
                exit_code=proc.returncode,
                duration_ms=duration,
            )
        except subprocess.TimeoutExpired:
            duration = int((time.time() - start) * 1000)
            return ExecutionResult(
                success=False, stdout="", stderr="Execution timed out",
                exit_code=-1, duration_ms=duration, timed_out=True,
            )
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return ExecutionResult(
                success=False, stdout="", stderr=str(e),
                exit_code=-1, duration_ms=duration,
            )

    def _run_docker(self, temp_dir: str, main_file: str, language: Language,
                    config: SandboxConfig, timeout: int, test_command: str) -> ExecutionResult:
        start = time.time()
        container_name = f"sandbox-{uuid.uuid4().hex[:8]}"
        tag = config.image

        rel_path = os.path.relpath(main_file, temp_dir)
        cmd_parts = self._get_run_command(language, rel_path, test_command)

        docker_cmd = [
            "docker", "run", "--rm",
            "--name", container_name,
            "--memory", f"{config.memory_limit_mb}m",
            "--cpus", str(config.cpu_limit),
            "-v", f"{temp_dir}:/workspace",
            "-w", "/workspace",
        ]
        if not config.network_enabled:
            docker_cmd.extend(["--network", "none"])
        docker_cmd.append(tag)
        docker_cmd.extend(cmd_parts)

        try:
            proc = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 5,
            )
            duration = int((time.time() - start) * 1000)
            return ExecutionResult(
                success=proc.returncode == 0,
                stdout=proc.stdout,
                stderr=proc.stderr,
                exit_code=proc.returncode,
                duration_ms=duration,
            )
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "kill", container_name], capture_output=True)
            duration = int((time.time() - start) * 1000)
            return ExecutionResult(
                success=False, stdout="", stderr="Docker execution timed out",
                exit_code=-1, duration_ms=duration, timed_out=True,
            )
        except FileNotFoundError:
            return self._run_local(temp_dir, main_file, language, timeout, test_command)
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return ExecutionResult(
                success=False, stdout="", stderr=str(e),
                exit_code=-1, duration_ms=duration,
            )

    def _docker_available(self) -> bool:
        try:
            subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _cleanup_later(self, temp_dir: str):
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

    def cleanup_all(self):
        for td in self._temp_dirs:
            self._cleanup_later(td)
        self._temp_dirs.clear()

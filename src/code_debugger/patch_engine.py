"""
Patch Engine — Structured diff generation, application, and rollback

Generates unified diffs from original → fixed code, applies patches to files,
supports rollback, and integrates with git for automatic commits and PRs.
"""

import difflib
import os
import subprocess
import tempfile
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FilePatch:
    file_path: str
    original_content: str
    patched_content: str
    diff: str = ""
    status: str = "pending"

    def __post_init__(self):
        if not self.diff:
            self.diff = self._generate_diff()

    def _generate_diff(self) -> str:
        original_lines = self.original_content.splitlines(keepends=True)
        patched_lines = self.patched_content.splitlines(keepends=True)
        diff = difflib.unified_diff(
            original_lines,
            patched_lines,
            fromfile=f"a/{self.file_path}",
            tofile=f"b/{self.file_path}",
        )
        return "".join(diff)


@dataclass
class PatchResult:
    success: bool
    applied_patches: List[FilePatch] = field(default_factory=list)
    failed_patches: List[Tuple[FilePatch, str]] = field(default_factory=list)
    commit_sha: Optional[str] = None
    pr_url: Optional[str] = None
    message: str = ""


@dataclass
class PatchSet:
    patches: List[FilePatch]
    summary: str = ""
    confidence_score: float = 0.0
    fixes_root_cause: bool = False


class PatchEngine:
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)

    def create_patch(self, file_path: str, original: str, fixed: str) -> FilePatch:
        abs_path = os.path.join(self.repo_path, file_path) if not os.path.isabs(file_path) else file_path
        return FilePatch(
            file_path=file_path,
            original_content=original,
            patched_content=fixed,
        )

    def apply_patch(self, patch: FilePatch, dry_run: bool = False) -> Tuple[bool, str]:
        abs_path = self._resolve_path(patch.file_path)

        if not os.path.exists(abs_path) and not dry_run:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        if not dry_run:
            try:
                with open(abs_path, "w") as f:
                    f.write(patch.patched_content)
                patch.status = "applied"
                return True, ""
            except Exception as e:
                patch.status = "failed"
                return False, str(e)

        return True, ""

    def apply_patch_set(self, patch_set: PatchSet, dry_run: bool = False) -> PatchResult:
        result = PatchResult(success=True)

        for patch in patch_set.patches:
            ok, err = self.apply_patch(patch, dry_run)
            if ok:
                result.applied_patches.append(patch)
            else:
                result.failed_patches.append((patch, err))
                result.success = False

        return result

    def rollback(self, patch: FilePatch) -> bool:
        abs_path = self._resolve_path(patch.file_path)
        try:
            with open(abs_path, "w") as f:
                f.write(patch.original_content)
            patch.status = "rolled_back"
            return True
        except Exception:
            return False

    def rollback_all(self, patches: List[FilePatch]) -> List[Tuple[FilePatch, bool]]:
        results = []
        for patch in reversed(patches):
            if patch.status == "applied":
                ok = self.rollback(patch)
                results.append((patch, ok))
        return results

    def create_diff_preview(self, patches: List[FilePatch]) -> str:
        parts = []
        for patch in patches:
            if patch.diff:
                parts.append(patch.diff)
        return "\n".join(parts)

    def git_commit(self, patches: List[FilePatch], message: str = None) -> Optional[str]:
        if not self._is_git_repo():
            return None

        try:
            if not message:
                files_summary = ", ".join(p.file_path for p in patches)
                message = f"fix: automated patch for {files_summary}"

            for patch in patches:
                rel_path = os.path.relpath(
                    self._resolve_path(patch.file_path), self.repo_path
                )
                subprocess.run(
                    ["git", "add", rel_path],
                    cwd=self.repo_path, capture_output=True
                )

            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path, capture_output=True, text=True
            )

            if result.returncode == 0:
                sha_result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=self.repo_path, capture_output=True, text=True
                )
                return sha_result.stdout.strip()
            return None
        except Exception:
            return None

    def git_create_branch_and_push(self, branch_name: str, patches: List[FilePatch],
                                    commit_message: str = None) -> Optional[str]:
        if not self._is_git_repo():
            return None
        try:
            subprocess.run(["git", "checkout", "-b", branch_name],
                           cwd=self.repo_path, capture_output=True)
            sha = self.git_commit(patches, commit_message)
            if sha:
                push_result = subprocess.run(
                    ["git", "push", "-u", "origin", branch_name],
                    cwd=self.repo_path, capture_output=True, text=True
                )
                if push_result.returncode == 0:
                    return sha
            return None
        except Exception:
            return None

    def _resolve_path(self, file_path: str) -> str:
        if os.path.isabs(file_path):
            return file_path
        return os.path.join(self.repo_path, file_path)

    def _is_git_repo(self) -> bool:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path, capture_output=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def diff_text(original: str, fixed: str, filename: str = "file") -> str:
        original_lines = original.splitlines(keepends=True)
        fixed_lines = fixed.splitlines(keepends=True)
        diff = difflib.unified_diff(
            original_lines, fixed_lines,
            fromfile=f"a/{filename}", tofile=f"b/{filename}",
        )
        return "".join(diff)

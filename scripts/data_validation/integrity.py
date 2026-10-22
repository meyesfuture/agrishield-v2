"""
File integrity and cryptographic checksum validation module.
Verifies all files against STARTER_SOURCE_DROP_MANIFEST.json and PROVENANCE_MANIFEST.json.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from .config import WORKSPACE_ROOT, STARTER_DROP_MANIFEST, PROVENANCE_MANIFEST, PHASE5_DIR


def compute_sha256(file_path: Path) -> str:
    """Compute standard SHA-256 hexadecimal digest for a given file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_starter_drop_manifest() -> Dict[str, Any]:
    """
    Verify all 49 files registered in STARTER_SOURCE_DROP_MANIFEST.json.
    Returns validation status, total files, matches, mismatches, and missing files.
    """
    if not STARTER_DROP_MANIFEST.exists():
        return {
            "status": "FAILED",
            "error": f"Manifest file not found: {STARTER_DROP_MANIFEST}",
            "total_files": 0,
            "passed": 0,
            "failed": 0,
            "missing": 0,
            "mismatches": [],
        }

    with open(STARTER_DROP_MANIFEST, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    files_list = manifest_data.get("files", [])
    total_files = len(files_list)
    passed = 0
    mismatches = []
    missing = []

    for entry in files_list:
        rel_path = entry.get("relative_path")
        expected_sha = entry.get("sha256")
        expected_size = entry.get("size_bytes")

        target_file = WORKSPACE_ROOT / rel_path

        if not target_file.exists():
            missing.append(rel_path)
            continue

        actual_size = target_file.stat().st_size
        actual_sha = compute_sha256(target_file)

        if actual_sha == expected_sha and actual_size == expected_size:
            passed += 1
        else:
            mismatches.append({
                "file": rel_path,
                "expected_sha": expected_sha,
                "actual_sha": actual_sha,
                "expected_size": expected_size,
                "actual_size": actual_size,
            })

    status = "PASSED" if (passed == total_files and not mismatches and not missing) else "FAILED"

    return {
        "status": status,
        "manifest_path": str(STARTER_DROP_MANIFEST.relative_to(WORKSPACE_ROOT)),
        "total_files": total_files,
        "passed": passed,
        "failed": len(mismatches),
        "missing": len(missing),
        "missing_files": missing,
        "mismatches": mismatches,
    }


def verify_provenance_manifest() -> Dict[str, Any]:
    """
    Verify the 44 acquisition files registered in PROVENANCE_MANIFEST.json.
    Returns verification status and any discrepancies.
    """
    if not PROVENANCE_MANIFEST.exists():
        return {
            "status": "FAILED",
            "error": f"Provenance manifest not found: {PROVENANCE_MANIFEST}",
            "total_files": 0,
            "passed": 0,
            "failed": 0,
            "missing": 0,
            "mismatches": [],
        }

    with open(PROVENANCE_MANIFEST, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    files_list = manifest_data.get("files", [])
    total_files = len(files_list)
    passed = 0
    mismatches = []
    missing = []

    for entry in files_list:
        rel_path = entry.get("relative_path")
        expected_sha = entry.get("sha256")
        expected_bytes = entry.get("bytes")

        # In PROVENANCE_MANIFEST, paths are relative to phase5_acquisition/
        # Normalize backslashes to forward slashes for cross-platform compatibility
        clean_rel_path = rel_path.replace("\\", "/")
        target_file = PHASE5_DIR / clean_rel_path

        if not target_file.exists():
            missing.append(clean_rel_path)
            continue

        actual_size = target_file.stat().st_size
        actual_sha = compute_sha256(target_file)

        if actual_sha == expected_sha and actual_size == expected_bytes:
            passed += 1
        else:
            mismatches.append({
                "file": clean_rel_path,
                "expected_sha": expected_sha,
                "actual_sha": actual_sha,
                "expected_size": expected_bytes,
                "actual_size": actual_size,
            })

    status = "PASSED" if (passed == total_files and not mismatches and not missing) else "FAILED"

    return {
        "status": status,
        "manifest_path": str(PROVENANCE_MANIFEST.relative_to(WORKSPACE_ROOT)),
        "total_files": total_files,
        "passed": passed,
        "failed": len(mismatches),
        "missing": len(missing),
        "missing_files": missing,
        "mismatches": mismatches,
    }

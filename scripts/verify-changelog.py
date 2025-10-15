#!/usr/bin/env python3
"""Verify changelog entries exist for all version updates.

This script ensures that all knowledge base version numbers have
corresponding entries in the CHANGELOG.md file.
"""

import re
import sys
from pathlib import Path


def extract_versions_from_changelog(changelog_path: Path) -> set[str]:
	"""Extract all version numbers from CHANGELOG.md.

	Args:
		changelog_path: Path to the CHANGELOG.md file

	Returns:
		Set of version numbers found in changelog
	"""
	content = changelog_path.read_text(encoding="utf-8")
	# Match versions like: ## [1.2.3] - 2025-10-14
	pattern = r"##\s*\[(\d+\.\d+\.\d+)\]"
	return set(re.findall(pattern, content))


def extract_versions_from_kb(kb_dir: Path) -> set[str]:
	"""Extract current versions from all knowledge base files.

	Args:
		kb_dir: Path to the knowledge base directory

	Returns:
		Set of version numbers found in KB files
	"""
	versions: set[str] = set()

	for file_path in kb_dir.rglob("*.md"):
		content = file_path.read_text(encoding="utf-8")
		match = re.search(r"version:\s*(\d+\.\d+\.\d+)", content)
		if match:
			versions.add(match.group(1))

	return versions


def main() -> int:
	"""Verify all KB versions have changelog entries.

	Returns:
		Exit code: 0 for success, 1 for missing entries
	"""
	kb_dir = Path("docs/knowledge-base")
	changelog_path = kb_dir / "CHANGELOG.md"

	if not changelog_path.exists():
		print("❌ CHANGELOG.md not found")
		return 1

	kb_versions = extract_versions_from_kb(kb_dir)
	changelog_versions = extract_versions_from_changelog(changelog_path)

	missing_versions = kb_versions - changelog_versions

	if missing_versions:
		print("❌ Changelog verification failed:\n")
		print("  Missing changelog entries for versions:")
		for version in sorted(missing_versions):
			print(f"    • {version}")
		return 1

	print("✅ All knowledge base versions have changelog entries")
	return 0


if __name__ == "__main__":
	sys.exit(main())

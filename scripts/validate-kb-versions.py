#!/usr/bin/env python3
"""Validate knowledge base version numbers and metadata.

This script ensures all knowledge base files have proper versioning
and required metadata fields in their frontmatter.
"""

import re
import sys
from pathlib import Path
from typing import Any

import yaml


def extract_frontmatter(file_path: Path) -> dict[str, Any]:
	"""Extract YAML frontmatter from markdown file.

	Args:
		file_path: Path to the markdown file

	Returns:
		Dictionary containing the frontmatter metadata

	Raises:
		ValueError: If no frontmatter is found in the file
	"""
	content = file_path.read_text(encoding="utf-8")
	match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)

	if not match:
		raise ValueError(f"No frontmatter found in {file_path}")

	return yaml.safe_load(match.group(1))  # type: ignore[no-any-return]


def validate_version_format(version: str) -> bool:
	"""Validate semantic version format.

	Args:
		version: Version string to validate

	Returns:
		True if version matches semantic versioning format (X.Y.Z)
	"""
	pattern = r"^\d+\.\d+\.\d+$"
	return bool(re.match(pattern, version))


def check_version_increment(old_version: str, new_version: str) -> tuple[bool, str]:
	"""Verify version was incremented correctly.

	Args:
		old_version: Previous version string
		new_version: New version string

	Returns:
		Tuple of (is_valid, message) indicating if increment is valid
	"""
	old_parts = [int(x) for x in old_version.split(".")]
	new_parts = [int(x) for x in new_version.split(".")]

	# Check MAJOR increment
	if new_parts[0] > old_parts[0]:
		if new_parts[1] == 0 and new_parts[2] == 0:
			return True, "MAJOR version increment"
		return False, "MAJOR increment should reset MINOR and PATCH to 0"

	# Check MINOR increment
	if new_parts[1] > old_parts[1]:
		if new_parts[2] == 0:
			return True, "MINOR version increment"
		return False, "MINOR increment should reset PATCH to 0"

	# Check PATCH increment
	if new_parts[2] > old_parts[2]:
		return True, "PATCH version increment"

	return False, "No version increment detected"


def main() -> int:
	"""Run knowledge base version validation.

	Returns:
		Exit code: 0 for success, 1 for validation failures
	"""
	kb_dir = Path("docs/knowledge-base")
	errors: list[str] = []
	version_history: dict[Path, str] = {}  # Track versions for increment validation

	for file_path in kb_dir.rglob("*.md"):
		try:
			metadata = extract_frontmatter(file_path)

			# Validate version format
			version = metadata.get("version")
			if not version:
				errors.append(f"{file_path}: Missing version in frontmatter")
				continue

			if not validate_version_format(str(version)):
				errors.append(f"{file_path}: Invalid version format '{version}' (expected X.Y.Z)")

			# Check version increment if we've seen this file before
			# (This is useful when running validation across git history or multiple runs)
			if file_path in version_history:
				old_version = version_history[file_path]
				is_valid, message = check_version_increment(old_version, str(version))
				if not is_valid:
					errors.append(
						f"{file_path}: Version increment issue: {message} "
						f"(previous: {old_version}, current: {version})"
					)

			# Store current version for future comparisons
			version_history[file_path] = str(version)

			# Validate required fields
			required_fields = ["last_updated", "status"]
			for field in required_fields:
				if field not in metadata:
					errors.append(f"{file_path}: Missing required field '{field}'")

		except (ValueError, yaml.YAMLError, KeyError) as e:
			errors.append(f"{file_path}: Validation error - {str(e)}")

	if errors:
		print("❌ Knowledge Base Validation Failed:\n")
		for error in errors:
			print(f"  • {error}")
		return 1

	print("✅ All knowledge base files validated successfully")
	return 0


if __name__ == "__main__":
	sys.exit(main())

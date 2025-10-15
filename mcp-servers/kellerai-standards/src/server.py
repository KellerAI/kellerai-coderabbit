#!/usr/bin/env python3
"""
KellerAI Custom MCP Server for CodeRabbit Integration
Serves organizational standards, ADRs, and team preferences

This MCP server provides tools for:
1. Retrieving coding standards by category
2. Searching Architecture Decision Records (ADRs)
3. Getting team code review preferences
4. Checking pattern approval status
"""

import os
import json
import yaml
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    from mcp import stdio_server
except ImportError:
    print("Error: MCP SDK not installed. Run: pip install mcp")
    exit(1)


# Configuration
REPO_ROOT = Path(os.environ.get('KELLERAI_REPO_ROOT', os.getcwd()))
STANDARDS_FILE = REPO_ROOT / 'docs' / 'standards' / 'coding-standards.yaml'
ADR_DIR = REPO_ROOT / 'docs' / 'architecture' / 'decisions'
PATTERNS_FILE = REPO_ROOT / 'docs' / 'standards' / 'approved-patterns.yaml'
PREFERENCES_FILE = REPO_ROOT / 'docs' / 'standards' / 'team-preferences.yaml'

# Initialize MCP server
server = Server("kellerai-standards")


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools for KellerAI standards"""
    return [
        Tool(
            name="get_coding_standards",
            description="Retrieve KellerAI coding standards by category (architecture, security, performance, testing, documentation, or 'all')",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["architecture", "security", "performance", 
                                "testing", "documentation", "all"],
                        "description": "Category of standards to retrieve",
                        "default": "all"
                    }
                }
            }
        ),
        Tool(
            name="search_adr",
            description="Search Architecture Decision Records (ADRs) by keyword or topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (e.g., 'database', 'authentication', 'api design')"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["accepted", "proposed", "deprecated", "superseded", "all"],
                        "description": "Filter by ADR status",
                        "default": "all"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_team_preferences",
            description="Get team code review preferences, naming conventions, and style guidelines",
            inputSchema={
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "typescript", "all"],
                        "description": "Programming language-specific preferences",
                        "default": "all"
                    }
                }
            }
        ),
        Tool(
            name="check_pattern_approval",
            description="Check if a code pattern is approved, discouraged, or prohibited at KellerAI",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Code pattern to check (e.g., 'singleton', 'global state', 'dependency injection')"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context (e.g., 'async programming', 'error handling')",
                        "default": ""
                    }
                },
                "required": ["pattern"]
            }
        ),
        Tool(
            name="validate_api_design",
            description="Validate API endpoint design against KellerAI REST API standards",
            inputSchema={
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "string",
                        "description": "API endpoint path (e.g., '/api/users/{id}')"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                        "description": "HTTP method"
                    },
                    "description": {
                        "type": "string",
                        "description": "Brief description of endpoint purpose"
                    }
                },
                "required": ["endpoint", "method"]
            }
        )
    ]


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle MCP tool calls"""
    
    try:
        if name == "get_coding_standards":
            result = await get_coding_standards(
                category=arguments.get("category", "all")
            )
        
        elif name == "search_adr":
            result = await search_architecture_decisions(
                query=arguments["query"],
                status=arguments.get("status", "all"),
                limit=arguments.get("limit", 5)
            )
        
        elif name == "get_team_preferences":
            result = await get_team_preferences(
                language=arguments.get("language", "all")
            )
        
        elif name == "check_pattern_approval":
            result = await check_pattern_approval(
                pattern=arguments["pattern"],
                context=arguments.get("context", "")
            )
        
        elif name == "validate_api_design":
            result = await validate_api_design(
                endpoint=arguments["endpoint"],
                method=arguments["method"],
                description=arguments.get("description", "")
            )
        
        else:
            result = f"Unknown tool: {name}"
        
        return [TextContent(type="text", text=result)]
    
    except Exception as e:
        error_msg = f"Error executing tool '{name}': {str(e)}"
        return [TextContent(type="text", text=error_msg)]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_coding_standards(category: str = "all") -> str:
    """Retrieve coding standards from YAML file"""
    try:
        if not STANDARDS_FILE.exists():
            return f"""
# KellerAI Coding Standards

⚠️ Standards file not found at: {STANDARDS_FILE}

Please create the standards file with organizational coding standards.
See documentation for template and examples.
"""
        
        with open(STANDARDS_FILE) as f:
            standards = yaml.safe_load(f)
        
        if category == "all":
            output = "# KellerAI Coding Standards - Complete Reference\n\n"
            output += yaml.dump(standards, default_flow_style=False, sort_keys=False)
        else:
            output = f"# KellerAI Coding Standards - {category.title()}\n\n"
            if category in standards:
                output += yaml.dump({category: standards[category]}, 
                                  default_flow_style=False, sort_keys=False)
            else:
                output += f"Category '{category}' not found in standards.\n"
                output += f"Available categories: {', '.join(standards.keys())}"
        
        return output
    
    except yaml.YAMLError as e:
        return f"Error parsing standards YAML: {str(e)}"
    except Exception as e:
        return f"Error loading standards: {str(e)}"


async def search_architecture_decisions(
    query: str, 
    status: str = "all", 
    limit: int = 5
) -> str:
    """Search ADRs for relevant decisions"""
    try:
        if not ADR_DIR.exists():
            return f"""
# Architecture Decision Records

⚠️ ADR directory not found at: {ADR_DIR}

Please create the ADR directory and add architecture decision records.
See documentation for ADR template and examples.
"""
        
        results = []
        query_lower = query.lower()
        
        # Search through all markdown files in ADR directory
        for adr_file in sorted(ADR_DIR.glob("*.md")):
            content = adr_file.read_text()
            
            # Extract ADR metadata
            metadata = extract_adr_metadata(content)
            
            # Filter by status if specified
            if status != "all" and metadata.get("status", "").lower() != status.lower():
                continue
            
            # Check if query matches filename or content
            if (query_lower in adr_file.name.lower() or 
                query_lower in content.lower()):
                
                results.append({
                    "file": adr_file.name,
                    "metadata": metadata,
                    "content": content[:1000]  # First 1000 chars
                })
            
            # Stop if we've reached the limit
            if len(results) >= limit:
                break
        
        if results:
            output = f"# Architecture Decision Records - Search Results for '{query}'\n\n"
            output += f"Found {len(results)} matching ADR(s)\n\n"
            
            for i, adr in enumerate(results, 1):
                output += f"## {i}. {adr['file']}\n\n"
                
                # Add metadata
                meta = adr['metadata']
                if meta:
                    output += f"**Status:** {meta.get('status', 'Unknown')}\n"
                    output += f"**Date:** {meta.get('date', 'Unknown')}\n"
                    if 'deciders' in meta:
                        output += f"**Deciders:** {meta['deciders']}\n"
                    output += "\n"
                
                # Add excerpt
                output += f"{adr['content']}\n\n"
                output += "---\n\n"
            
            return output
        else:
            return f"""
# Architecture Decision Records - No Results

No ADRs found matching '{query}' with status '{status}'.

Suggestions:
- Try broader search terms
- Check ADR status filter
- Verify ADRs exist in: {ADR_DIR}
"""
    
    except Exception as e:
        return f"Error searching ADRs: {str(e)}"


async def get_team_preferences(language: str = "all") -> str:
    """Get team preferences from YAML file"""
    try:
        if not PREFERENCES_FILE.exists():
            # Return default preferences
            return get_default_preferences(language)
        
        with open(PREFERENCES_FILE) as f:
            prefs = yaml.safe_load(f)
        
        if language == "all":
            output = "# KellerAI Team Preferences - All Languages\n\n"
            output += yaml.dump(prefs, default_flow_style=False, sort_keys=False)
        else:
            output = f"# KellerAI Team Preferences - {language.title()}\n\n"
            if language in prefs:
                output += yaml.dump({language: prefs[language]}, 
                                  default_flow_style=False, sort_keys=False)
            else:
                output += f"No specific preferences for '{language}'.\n"
                output += "Using general preferences.\n\n"
                output += yaml.dump(prefs.get("general", {}), 
                                  default_flow_style=False)
        
        return output
    
    except Exception as e:
        return f"Error loading preferences: {str(e)}\n\n" + get_default_preferences(language)


async def check_pattern_approval(pattern: str, context: str = "") -> str:
    """Check if a pattern is approved, discouraged, or prohibited"""
    try:
        if not PATTERNS_FILE.exists():
            return get_default_pattern_status(pattern, context)
        
        with open(PATTERNS_FILE) as f:
            patterns = yaml.safe_load(f)
        
        pattern_lower = pattern.lower()
        
        # Search through pattern categories
        for category in ["approved", "discouraged", "prohibited"]:
            if category in patterns:
                for item in patterns[category]:
                    if isinstance(item, str):
                        item_name = item
                        item_desc = ""
                    elif isinstance(item, dict):
                        item_name = list(item.keys())[0]
                        item_desc = item[item_name]
                    else:
                        continue
                    
                    if pattern_lower in item_name.lower():
                        return format_pattern_status(
                            pattern, category, item_name, item_desc, context
                        )
        
        # Pattern not found in explicit list
        return f"""
# Pattern Status: {pattern}

ℹ️ Pattern '{pattern}' not explicitly listed in KellerAI standards.

**Recommendation:** Use best judgment and seek code review.

**Context:** {context if context else "General usage"}

**Next Steps:**
1. Discuss with team lead if uncertain
2. Consider adding to approved patterns if widely beneficial
3. Document decision for future reference
"""
    
    except Exception as e:
        return f"Error checking pattern: {str(e)}\n\n" + get_default_pattern_status(pattern, context)


async def validate_api_design(endpoint: str, method: str, description: str = "") -> str:
    """Validate API endpoint design against standards"""
    issues = []
    recommendations = []
    
    # Check versioning
    if not endpoint.startswith("/api/v"):
        issues.append("❌ Missing API versioning. Endpoints should start with `/api/v1/`, `/api/v2/`, etc.")
    
    # Check resource naming
    if "//" in endpoint:
        issues.append("❌ Double slashes in endpoint path")
    
    # Check for trailing slash
    if endpoint.endswith("/") and endpoint != "/":
        issues.append("⚠️ Trailing slash. Remove for consistency.")
    
    # Check HTTP method usage
    method_guidance = {
        "GET": "Should be idempotent and safe. No side effects.",
        "POST": "Use for creating resources or non-idempotent operations.",
        "PUT": "Use for full resource replacement. Include all fields.",
        "PATCH": "Use for partial updates. Include only changed fields.",
        "DELETE": "Should be idempotent. Deleting twice = same result."
    }
    
    if method in method_guidance:
        recommendations.append(f"📘 {method} - {method_guidance[method]}")
    
    # Check for query parameters in path (common mistake)
    if "?" in endpoint:
        issues.append("❌ Query parameters in path. Use proper query string syntax.")
    
    # Build response
    output = f"# API Design Validation: {method} {endpoint}\n\n"
    
    if description:
        output += f"**Description:** {description}\n\n"
    
    if not issues and not recommendations:
        output += "✅ **Status:** Passes KellerAI API design standards\n\n"
    else:
        if issues:
            output += "## Issues Found\n\n"
            for issue in issues:
                output += f"{issue}\n"
            output += "\n"
        
        if recommendations:
            output += "## Recommendations\n\n"
            for rec in recommendations:
                output += f"{rec}\n"
            output += "\n"
    
    # Add general API standards
    output += """
## KellerAI API Standards

### Endpoint Structure
- ✅ Format: `/api/v{version}/{resource}/{id}/{sub-resource}`
- ✅ Use plural nouns for resources: `/users`, `/orders`
- ✅ Use kebab-case for multi-word resources: `/user-profiles`

### HTTP Methods
- **GET**: Retrieve resource(s)
- **POST**: Create new resource
- **PUT**: Replace entire resource
- **PATCH**: Partial update
- **DELETE**: Remove resource

### Response Codes
- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid input
- **401 Unauthorized**: Missing/invalid auth
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server error

### Required Headers
- `Content-Type: application/json`
- `Authorization: Bearer <token>`
- `X-Request-ID: <uuid>` (for tracking)

### Pagination
- Use query parameters: `?page=1&limit=20`
- Return metadata: `total`, `page`, `limit`, `hasMore`

### Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "field": "email"
  }
}
```
"""
    
    return output


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def extract_adr_metadata(content: str) -> Dict[str, str]:
    """Extract metadata from ADR markdown content"""
    metadata = {}
    lines = content.split('\n')
    
    for line in lines[:20]:  # Check first 20 lines
        line = line.strip()
        if line.startswith("**Status:**"):
            metadata["status"] = line.split("**Status:**")[1].strip()
        elif line.startswith("**Date:**"):
            metadata["date"] = line.split("**Date:**")[1].strip()
        elif line.startswith("**Deciders:**"):
            metadata["deciders"] = line.split("**Deciders:**")[1].strip()
    
    return metadata


def format_pattern_status(
    pattern: str, 
    category: str, 
    item_name: str, 
    description: str, 
    context: str
) -> str:
    """Format pattern approval status"""
    emoji_map = {
        "approved": "✅",
        "discouraged": "⚠️",
        "prohibited": "🚫"
    }
    
    status_map = {
        "approved": "APPROVED",
        "discouraged": "DISCOURAGED",
        "prohibited": "PROHIBITED"
    }
    
    emoji = emoji_map.get(category, "ℹ️")
    status = status_map.get(category, "UNKNOWN")
    
    output = f"# Pattern Status: {pattern}\n\n"
    output += f"{emoji} **Status:** {status}\n\n"
    output += f"**Pattern:** {item_name}\n\n"
    
    if description:
        output += f"**Guidance:** {description}\n\n"
    
    if context:
        output += f"**Context:** {context}\n\n"
    
    if category == "approved":
        output += "This pattern is approved for use at KellerAI. Follow best practices.\n"
    elif category == "discouraged":
        output += "This pattern is discouraged. Consider alternatives when possible.\n"
    elif category == "prohibited":
        output += "This pattern is prohibited for security/safety reasons. Do not use.\n"
    
    return output


def get_default_preferences(language: str) -> str:
    """Return default team preferences"""
    defaults = {
        "python": {
            "naming": {
                "functions": "snake_case",
                "classes": "PascalCase",
                "constants": "UPPER_SNAKE_CASE",
                "private": "_leading_underscore"
            },
            "async": "Required for I/O operations",
            "type_hints": "Required for public APIs",
            "docstrings": "Google style, required for all public functions"
        },
        "javascript": {
            "naming": {
                "functions": "camelCase",
                "classes": "PascalCase",
                "constants": "UPPER_SNAKE_CASE"
            },
            "async": "Use async/await, avoid callbacks",
            "modules": "ES6 modules (import/export)",
            "formatting": "Prettier with 2-space indents"
        }
    }
    
    if language == "all":
        return yaml.dump(defaults, default_flow_style=False)
    elif language in defaults:
        return yaml.dump({language: defaults[language]}, default_flow_style=False)
    else:
        return f"No default preferences for {language}"


def get_default_pattern_status(pattern: str, context: str) -> str:
    """Return default pattern status when patterns file doesn't exist"""
    # Common approved patterns
    approved = ["dependency injection", "async/await", "type hints", "dataclasses", 
                "context managers", "generators", "list comprehensions", "f-strings"]
    
    # Common discouraged patterns
    discouraged = ["global state", "mutable defaults", "bare except", 
                  "string concatenation in loops"]
    
    # Common prohibited patterns
    prohibited = ["eval", "exec", "pickle untrusted data", "sql injection", 
                 "hardcoded credentials"]
    
    pattern_lower = pattern.lower()
    
    for p in approved:
        if p in pattern_lower:
            return format_pattern_status(pattern, "approved", p, "", context)
    
    for p in discouraged:
        if p in pattern_lower:
            return format_pattern_status(pattern, "discouraged", p, "", context)
    
    for p in prohibited:
        if p in pattern_lower:
            return format_pattern_status(pattern, "prohibited", p, "", context)
    
    return f"Pattern '{pattern}' not explicitly listed. Use best judgment."


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

async def main():
    """Run the KellerAI Standards MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

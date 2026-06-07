"""MCP Tool definitions for TUKUB AI"""

from typing import Dict, Any, List

MCP_TOOLS = [
    {
        "name": "nmap_scan",
        "description": "Network port scanning and service detection",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Target IP or domain"},
                "ports": {"type": "string", "description": "Port range"},
                "scan_type": {"type": "string", "enum": ["syn", "tcp", "udp"]}
            },
            "required": ["target"]
        }
    },
    {
        "name": "nuclei_scan",
        "description": "Vulnerability scanning",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Target URL"},
                "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"]}
            },
            "required": ["target"]
        }
    },
    {
        "name": "ffuf_fuzz",
        "description": "Web fuzzing",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target URL with FUZZ"},
                "wordlist": {"type": "string", "description": "Wordlist path"}
            },
            "required": ["url", "wordlist"]
        }
    }
]


def get_mcp_tools() -> List[Dict[str, Any]]:
    """Get all MCP tool definitions"""
    return MCP_TOOLS
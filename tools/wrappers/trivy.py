"""Trivy wrapper for vulnerability scanning"""

import subprocess
import json
from typing import Dict, Any, Optional


class TrivyWrapper:
    """Wrapper for Trivy vulnerability scanner"""
    
    @staticmethod
    def scan(target: str, scan_type: str = "image", severity: str = "HIGH") -> Dict[str, Any]:
        """Scan for vulnerabilities"""
        
        cmd = ["trivy", scan_type, target, "--severity", severity, "--format", "json"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        data = {}
        if result.stdout:
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass
        
        return {
            "success": result.returncode == 0,
            "vulnerabilities": data.get("Results", []),
            "raw": result.stdout
        }
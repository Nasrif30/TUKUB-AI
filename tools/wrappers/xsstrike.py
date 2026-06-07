"""XSStrike wrapper for XSS detection"""

import subprocess
from typing import Dict, Any


class XSStrikeWrapper:
    """Wrapper for XSStrike XSS scanner"""
    
    @staticmethod
    def scan(url: str, data: str = None) -> Dict[str, Any]:
        """Scan for XSS vulnerabilities"""
        
        cmd = ["python3", "xsstrike.py", "-u", url]
        
        if data:
            cmd.extend(["--data", data])
        
        cmd.extend(["--json"])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
"""Falco wrapper for runtime security"""

import subprocess
from typing import Dict, Any


class FalcoWrapper:
    """Wrapper for Falco"""
    
    @staticmethod
    def check_rules(rules_file: str) -> Dict[str, Any]:
        """Check Falco rules"""
        
        cmd = ["falco", "-r", rules_file, "-t"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
"""Pwntools wrapper for exploit development"""

import subprocess
from typing import Dict, Any


class PwntoolsWrapper:
    """Wrapper for Pwntools"""
    
    @staticmethod
    def run_script(script_path: str) -> Dict[str, Any]:
        """Run Pwntools exploit script"""
        
        cmd = ["python3", script_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
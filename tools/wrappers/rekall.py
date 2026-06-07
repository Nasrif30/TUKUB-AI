"""Rekall wrapper for memory forensics"""

import subprocess
from typing import Dict, Any


class RekallWrapper:
    """Wrapper for Rekall memory forensics"""
    
    @staticmethod
    def analyze(memory_file: str, profile: str = "Win10x64") -> Dict[str, Any]:
        """Analyze memory dump with Rekall"""
        
        cmd = ["rekall", "-f", memory_file, "--profile", profile, "pslist"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
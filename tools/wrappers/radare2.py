"""Radare2 wrapper for binary analysis"""

import subprocess
from typing import Dict, Any


class Radare2Wrapper:
    """Wrapper for Radare2"""
    
    @staticmethod
    def analyze(binary_path: str) -> Dict[str, Any]:
        """Analyze binary with Radare2"""
        
        cmd = ["r2", "-c", "aaa; afl; q", binary_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
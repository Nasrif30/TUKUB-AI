"""Volatility wrapper for memory forensics"""

import subprocess
from typing import Dict, Any, Optional


class VolatilityWrapper:
    """Wrapper for Volatility 3 memory forensics"""
    
    @staticmethod
    def analyze(memory_file: str, plugin: str = "windows.pslist") -> Dict[str, Any]:
        """Analyze memory dump with Volatility"""
        
        cmd = ["volatility3", "-f", memory_file, plugin]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
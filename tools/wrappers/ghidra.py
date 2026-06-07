"""Ghidra wrapper for reverse engineering"""

import subprocess
from typing import Dict, Any
from pathlib import Path


class GhidraWrapper:
    """Wrapper for Ghidra headless"""
    
    @staticmethod
    def analyze(binary_path: str, project_name: str = "analysis") -> Dict[str, Any]:
        """Analyze binary with Ghidra headless"""
        
        cmd = [
            "ghidraHeadless",
            Path(binary_path).parent,
            project_name,
            "-import",
            binary_path,
            "-analyze",
            "-postScript",
            "AnalysisScript"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
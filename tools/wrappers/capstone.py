"""Capstone wrapper for disassembly"""

import subprocess
from typing import Dict, Any


class CapstoneWrapper:
    """Wrapper for Capstone disassembly framework"""
    
    @staticmethod
    def disassemble(binary_path: str, arch: str = "x86") -> Dict[str, Any]:
        """Disassemble binary"""
        
        cmd = ["cstool", f"-d {arch}", binary_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
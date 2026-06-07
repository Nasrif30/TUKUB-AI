"""Shellter wrapper for shellcode injection"""

import subprocess
from typing import Dict, Any


class ShellterWrapper:
    """Wrapper for Shellter"""
    
    @staticmethod
    def inject(exe_path: str, payload: str) -> Dict[str, Any]:
        """Inject shellcode into executable"""
        
        cmd = ["shellter", "-A", "-f", exe_path, "-p", payload]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
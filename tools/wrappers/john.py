"""John the Ripper wrapper"""

import subprocess
from typing import Dict, Any


class JohnWrapper:
    """Wrapper for John the Ripper"""
    
    @staticmethod
    def crack(hash_file: str, format: str = "raw-md5") -> Dict[str, Any]:
        """Crack hashes with John"""
        
        cmd = ["john", f"--format={format}", "--show", hash_file]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
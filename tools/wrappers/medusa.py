"""Medusa wrapper for parallel brute force"""

import subprocess
from typing import Dict, Any, Optional


class MedusaWrapper:
    """Wrapper for Medusa"""
    
    @staticmethod
    def brute(target: str, service: str, userlist: str, passlist: str, threads: int = 4) -> Dict[str, Any]:
        """Brute force with Medusa"""
        
        cmd = ["medusa", "-h", target, "-M", service, "-U", userlist, "-P", passlist, "-t", str(threads)]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
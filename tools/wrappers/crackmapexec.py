"""CrackMapExec wrapper for AD enumeration"""

import subprocess
from typing import Dict, Any, Optional


class CrackMapExecWrapper:
    """Wrapper for CrackMapExec"""
    
    @staticmethod
    def enumerate(target: str, protocol: str = "smb", username: Optional[str] = None, 
                   password: Optional[str] = None) -> Dict[str, Any]:
        """Enumerate target"""
        
        cmd = ["crackmapexec", protocol, target]
        
        if username and password:
            cmd.extend(["-u", username, "-p", password])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
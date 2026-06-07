"""Hydra wrapper for brute force attacks"""

import subprocess
from typing import Dict, Any, Optional


class HydraWrapper:
    """Wrapper for Hydra"""
    
    @staticmethod
    def brute(target: str, service: str, userlist: str, passlist: str, port: Optional[int] = None) -> Dict[str, Any]:
        """Brute force login"""
        
        cmd = ["hydra", "-L", userlist, "-P", passlist, f"{service}://{target}"]
        
        if port:
            cmd.extend(["-s", str(port)])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
"""BloodHound wrapper for AD attack path mapping"""

import subprocess
from typing import Dict, Any, Optional


class BloodHoundWrapper:
    """Wrapper for BloodHound collector"""
    
    @staticmethod
    def collect(domain: str, username: str, password: str, dc: Optional[str] = None) -> Dict[str, Any]:
        """Collect AD data for BloodHound"""
        
        cmd = ["bloodhound-python", "-u", username, "-p", password, "-d", domain, "-ns", dc or ""]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
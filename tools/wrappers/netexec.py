"""NetExec wrapper for network exploitation"""

import subprocess
import json
from typing import Dict, Any, Optional


class NetexecWrapper:
    """Wrapper for NetExec (formerly CrackMapExec)"""
    
    @staticmethod
    def enumerate(target: str, protocol: str = "smb", username: Optional[str] = None, 
                   password: Optional[str] = None) -> Dict[str, Any]:
        """Enumerate target using NetExec"""
        
        cmd = ["netexec", protocol, target]
        
        if username and password:
            cmd.extend(["-u", username, "-p", password])
        
        cmd.extend(["--json"])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        data = []
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        
        return {
            "success": result.returncode == 0,
            "data": data,
            "raw": result.stdout
        }
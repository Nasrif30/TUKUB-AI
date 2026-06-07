"""ScoutSuite wrapper for cloud security"""

import subprocess
from typing import Dict, Any


class ScoutSuiteWrapper:
    """Wrapper for ScoutSuite"""
    
    @staticmethod
    def audit(provider: str = "aws", profile: str = "default") -> Dict[str, Any]:
        """Run cloud security audit"""
        
        cmd = ["scout", "--provider", provider, "--profile", profile]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
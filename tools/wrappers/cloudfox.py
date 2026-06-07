"""CloudFox wrapper for cloud pentesting"""

import subprocess
from typing import Dict, Any


class CloudFoxWrapper:
    """Wrapper for CloudFox"""
    
    @staticmethod
    def enumerate(provider: str = "aws", command: str = "all") -> Dict[str, Any]:
        """Enumerate cloud resources"""
        
        cmd = ["cloudfox", provider, command]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
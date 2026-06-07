"""Docker Bench Security wrapper"""

import subprocess
from typing import Dict, Any


class DockerBenchWrapper:
    """Wrapper for Docker Bench Security"""
    
    @staticmethod
    def audit() -> Dict[str, Any]:
        """Run Docker security audit"""
        
        cmd = ["docker-bench-security"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
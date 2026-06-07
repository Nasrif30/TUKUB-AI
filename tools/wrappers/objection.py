"""Objection wrapper for mobile runtime exploration"""

import subprocess
from typing import Dict, Any


class ObjectionWrapper:
    """Wrapper for Objection"""
    
    @staticmethod
    def explore(package_name: str, device: str = "emulator") -> Dict[str, Any]:
        """Explore Android/iOS app"""
        
        cmd = ["objection", "--device", device, "--package", package_name, "explore", "--quiet"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
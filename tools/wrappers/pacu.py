"""Pacu wrapper for AWS exploitation"""

import subprocess
from typing import Dict, Any, Optional


class PacuWrapper:
    """Wrapper for Pacu AWS exploitation framework"""
    
    @staticmethod
    def run_module(module_name: str, session_name: str = "default") -> Dict[str, Any]:
        """Run Pacu module"""
        
        cmd = ["pacu", "--session", session_name, "--module", module_name]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
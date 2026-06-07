"""Veil wrapper for payload generation"""

import subprocess
from typing import Dict, Any


class VeilWrapper:
    """Wrapper for Veil Framework"""
    
    @staticmethod
    def generate_payload(payload_type: str = "python/meterpreter/rev_tcp") -> Dict[str, Any]:
        """Generate payload with Veil"""
        
        cmd = ["veil", "--type", payload_type, "--output"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
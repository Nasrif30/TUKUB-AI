"""Bettercap wrapper for MITM attacks"""

import subprocess
from typing import Dict, Any


class BettercapWrapper:
    """Wrapper for Bettercap"""
    
    @staticmethod
    def run_caplet(caplet_file: str) -> Dict[str, Any]:
        """Run Bettercap caplet"""
        
        cmd = ["bettercap", "-eval", f"caplet.load({caplet_file})"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
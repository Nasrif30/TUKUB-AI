"""GQRX wrapper for SDR analysis"""

import subprocess
from typing import Dict, Any


class GQRXWrapper:
    """Wrapper for GQRX SDR receiver"""
    
    @staticmethod
    def scan(frequency: str, duration: int = 10) -> Dict[str, Any]:
        """Scan frequency"""
        
        cmd = ["gqrx", "-r", str(duration), "-f", frequency]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 30)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
"""Aircrack-ng wrapper for WiFi auditing"""

import subprocess
from typing import Dict, Any


class AircrackWrapper:
    """Wrapper for Aircrack-ng"""
    
    @staticmethod
    def crack(handshake_file: str, wordlist: str) -> Dict[str, Any]:
        """Crack WPA/WPA2 handshake"""
        
        cmd = ["aircrack-ng", "-w", wordlist, handshake_file]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
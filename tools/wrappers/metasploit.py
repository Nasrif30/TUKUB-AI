"""Metasploit wrapper for exploitation"""

import subprocess
from typing import Dict, Any


class MetasploitWrapper:
    """Wrapper for Metasploit Framework"""
    
    @staticmethod
    def run_console(commands: list) -> Dict[str, Any]:
        """Run Metasploit commands"""
        
        cmd = ["msfconsole", "-q", "-x", "; ".join(commands) + "; exit"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
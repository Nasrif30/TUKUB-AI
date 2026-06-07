"""Frida wrapper for dynamic instrumentation"""

import subprocess
from typing import Dict, Any, Optional


class FridaWrapper:
    """Wrapper for Frida"""
    
    @staticmethod
    def trace_process(process_name: str, script_path: Optional[str] = None) -> Dict[str, Any]:
        """Trace process with Frida"""
        
        cmd = ["frida", "-n", process_name]
        
        if script_path:
            cmd.extend(["-l", script_path])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
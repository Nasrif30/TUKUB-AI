"""Masscan wrapper for fast port scanning"""

import subprocess
import json
from typing import Dict, Any, Optional


class MasscanWrapper:
    """Wrapper for Masscan"""
    
    @staticmethod
    def scan(target: str, ports: str = "1-1000", rate: int = 1000) -> Dict[str, Any]:
        """Fast port scan with Masscan"""
        
        cmd = ["masscan", target, "-p", ports, "--rate", str(rate), "-oJ", "-"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        data = []
        if result.stdout:
            try:
                parsed = json.loads(result.stdout)
                data = parsed.get("ports", [])
            except:
                pass
        
        return {
            "success": result.returncode == 0,
            "ports": data,
            "count": len(data),
            "raw": result.stdout
        }
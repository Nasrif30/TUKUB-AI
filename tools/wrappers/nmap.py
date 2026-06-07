"""Nmap wrapper for network scanning"""

import subprocess
import json
from typing import Dict, Any, Optional


class NmapWrapper:
    """Wrapper for Nmap security scanner"""
    
    @staticmethod
    def scan(target: str, ports: Optional[str] = None, scan_type: str = "syn") -> Dict[str, Any]:
        """Perform Nmap scan on target"""
        
        cmd = ["nmap"]
        
        if scan_type == "syn":
            cmd.append("-sS")
        elif scan_type == "tcp":
            cmd.append("-sT")
        elif scan_type == "udp":
            cmd.append("-sU")
        
        if ports:
            cmd.extend(["-p", ports])
        
        cmd.extend(["-oJ", "-", target])  # JSON output
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and result.stdout:
            try:
                data = json.loads(result.stdout)
                return {"success": True, "data": data, "raw": result.stdout}
            except json.JSONDecodeError:
                return {"success": True, "data": result.stdout, "raw": result.stdout}
        
        return {"success": False, "error": result.stderr}
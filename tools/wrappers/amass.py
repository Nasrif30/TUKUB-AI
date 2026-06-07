"""Amass wrapper for subdomain enumeration"""

import subprocess
import json
from typing import Dict, Any


class AmassWrapper:
    """Wrapper for Amass subdomain enumeration"""
    
    @staticmethod
    def enumerate(domain: str, passive: bool = True) -> Dict[str, Any]:
        """Enumerate subdomains"""
        
        cmd = ["amass", "enum", "-d", domain]
        
        if passive:
            cmd.append("-passive")
        
        cmd.extend(["-o", "-", "-json"])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        subdomains = []
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        subdomains.append(data.get("name", ""))
                    except:
                        pass
        
        return {
            "success": result.returncode == 0,
            "subdomains": subdomains,
            "count": len(subdomains),
            "raw": result.stdout
        }
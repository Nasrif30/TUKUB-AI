"""Subfinder wrapper for fast subdomain discovery"""

import subprocess
import json
from typing import Dict, Any


class SubfinderWrapper:
    """Wrapper for Subfinder"""
    
    @staticmethod
    def find(domain: str) -> Dict[str, Any]:
        """Find subdomains"""
        
        cmd = ["subfinder", "-d", domain, "-silent", "-o", "-"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        subdomains = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
        
        return {
            "success": result.returncode == 0,
            "subdomains": subdomains,
            "count": len(subdomains),
            "raw": result.stdout
        }
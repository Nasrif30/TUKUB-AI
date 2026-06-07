"""Kube-Hunter wrapper for Kubernetes security"""

import subprocess
from typing import Dict, Any


class KubeHunterWrapper:
    """Wrapper for Kube-Hunter"""
    
    @staticmethod
    def hunt(target: str = None) -> Dict[str, Any]:
        """Hunt for Kubernetes vulnerabilities"""
        
        cmd = ["kube-hunter"]
        
        if target:
            cmd.extend(["--remote", target])
        
        cmd.extend(["--log", "json"])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
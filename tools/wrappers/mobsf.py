"""MobSF wrapper for mobile security"""

import subprocess
from typing import Dict, Any


class MobSFWrapper:
    """Wrapper for Mobile Security Framework"""
    
    @staticmethod
    def scan(apk_path: str) -> Dict[str, Any]:
        """Scan APK with MobSF"""
        
        cmd = ["mobsf", "-f", apk_path, "-o", "json"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
"""Autopsy wrapper for disk forensics"""

import subprocess
from typing import Dict, Any


class AutopsyWrapper:
    """Wrapper for Autopsy"""
    
    @staticmethod
    def analyze(disk_image: str, case_dir: str) -> Dict[str, Any]:
        """Run Autopsy analysis"""
        
        cmd = ["autopsy", "--basedir", case_dir, disk_image]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
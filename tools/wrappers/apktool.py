"""Apktool wrapper for APK decompilation"""

import subprocess
from typing import Dict, Any
from pathlib import Path


class ApktoolWrapper:
    """Wrapper for Apktool"""
    
    @staticmethod
    def decompile(apk_path: str, output_dir: str = None) -> Dict[str, Any]:
        """Decompile APK file"""
        
        output = output_dir or Path(apk_path).stem + "_decompiled"
        cmd = ["apktool", "d", apk_path, "-o", output, "-f"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "output_dir": output,
            "output": result.stdout,
            "error": result.stderr
        }
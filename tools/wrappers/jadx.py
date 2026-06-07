"""JADX wrapper for Java decompilation"""

import subprocess
from typing import Dict, Any


class JADXWrapper:
    """Wrapper for JADX"""
    
    @staticmethod
    def decompile(apk_path: str, output_dir: str = None) -> Dict[str, Any]:
        """Decompile APK to Java source"""
        
        cmd = ["jadx", "-d", output_dir or "jadx_output", apk_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
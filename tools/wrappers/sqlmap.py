"""SQLMap wrapper for SQL injection"""

import subprocess
import json
from typing import Dict, Any, Optional


class SqlmapWrapper:
    """Wrapper for SQLMap"""
    
    @staticmethod
    def exploit(url: str, data: Optional[str] = None, level: int = 1) -> Dict[str, Any]:
        """Run SQLMap exploitation"""
        
        cmd = ["sqlmap", "-u", url, "--batch", "--level", str(level)]
        
        if data:
            cmd.extend(["--data", data])
        
        cmd.extend(["--output-format", "json"])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
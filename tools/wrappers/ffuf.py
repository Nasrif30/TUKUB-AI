"""FFUF wrapper for web fuzzing"""

import subprocess
import json
from typing import Dict, Any, Optional


class FfufWrapper:
    """Wrapper for FFUF web fuzzer"""
    
    @staticmethod
    def fuzz(url: str, wordlist: str, extensions: Optional[str] = None) -> Dict[str, Any]:
        """Run FFUF fuzzing"""
        
        cmd = ["ffuf", "-u", url, "-w", wordlist, "-o", "-", "-of", "json"]
        
        if extensions:
            cmd.extend(["-e", extensions])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                return {"success": True, "results": data, "raw": result.stdout}
            except json.JSONDecodeError:
                return {"success": True, "data": result.stdout, "raw": result.stdout}
        
        return {"success": False, "error": result.stderr}
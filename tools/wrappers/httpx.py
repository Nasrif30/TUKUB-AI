"""HTTPx wrapper for HTTP probing"""

import subprocess
import json
from typing import Dict, Any, List


class HTTPxWrapper:
    """Wrapper for HTTPx"""
    
    @staticmethod
    def probe(targets: List[str]) -> Dict[str, Any]:
        """Probe HTTP endpoints"""
        
        cmd = ["httpx", "-silent", "-json", "-o", "-"]
        
        result = subprocess.run(cmd, input="\n".join(targets), capture_output=True, text=True, timeout=300)
        
        results = []
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        results.append(json.loads(line))
                    except:
                        pass
        
        return {
            "success": result.returncode == 0,
            "results": results,
            "count": len(results),
            "raw": result.stdout
        }
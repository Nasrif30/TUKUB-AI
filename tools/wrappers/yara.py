"""YARA wrapper for malware detection"""

import subprocess
from typing import Dict, Any, List


class YARAWapper:
    """Wrapper for YARA"""
    
    @staticmethod
    def scan(file_path: str, rules_path: str) -> Dict[str, Any]:
        """Scan file with YARA rules"""
        
        cmd = ["yara", rules_path, file_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        matches = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        
        return {
            "success": True,
            "matches": matches,
            "count": len(matches),
            "raw": result.stdout
        }
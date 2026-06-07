"""OWASP ZAP wrapper for web scanning"""

import subprocess
from typing import Dict, Any, Optional


class ZAPWrapper:
    """Wrapper for OWASP ZAP"""
    
    @staticmethod
    def scan(target: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Run ZAP scan"""
        
        cmd = ["zap-cli", "--zap-path", "zap.sh", "quick-scan", "--self-contained", "--start-options", "-config", target]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
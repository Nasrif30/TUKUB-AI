"""Prowler wrapper for cloud security auditing"""

import subprocess
from typing import Dict, Any, Optional


class ProwlerWrapper:
    """Wrapper for Prowler cloud security tool"""
    
    @staticmethod
    def audit(provider: str = "aws", profile: Optional[str] = None) -> Dict[str, Any]:
        """Run cloud security audit"""
        
        cmd = ["prowler", provider]
        
        if profile:
            cmd.extend(["--profile", profile])
        
        cmd.extend(["-M", "json"])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        
        findings = []
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        import json
                        findings.append(json.loads(line))
                    except:
                        pass
        
        return {
            "success": result.returncode == 0,
            "findings": findings,
            "raw": result.stdout
        }
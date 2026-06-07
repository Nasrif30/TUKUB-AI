"""Nuclei wrapper for vulnerability scanning"""

import subprocess
import json
from typing import Dict, Any, Optional, List


class NucleiWrapper:
    """Wrapper for Nuclei vulnerability scanner"""
    
    @staticmethod
    def scan(target: str, severity: str = "high", templates: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run Nuclei scan on target"""
        
        cmd = ["nuclei", "-u", target, "-json"]
        
        severity_map = {"critical": "critical", "high": "high", "medium": "medium", "low": "low"}
        if severity in severity_map:
            cmd.extend(["-s", severity_map[severity]])
        
        if templates:
            for template in templates:
                cmd.extend(["-t", template])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        findings = []
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        findings.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        
        return {
            "success": result.returncode == 0,
            "findings": findings,
            "count": len(findings),
            "raw": result.stdout
        }
"""Hashcat wrapper for password cracking"""

import subprocess
from typing import Dict, Any, Optional


class HashcatWrapper:
    """Wrapper for Hashcat"""
    
    @staticmethod
    def crack(hash_file: str, hash_type: int, wordlist: str, rules: Optional[str] = None) -> Dict[str, Any]:
        """Crack password hashes"""
        
        cmd = ["hashcat", "-m", str(hash_type), "-a", "0", hash_file, wordlist, "--outfile", "-"]
        
        if rules:
            cmd.extend(["-r", rules])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        cracked = []
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if ':' in line and not line.startswith('#'):
                    cracked.append(line)
        
        return {
            "success": result.returncode == 0,
            "cracked": cracked,
            "count": len(cracked),
            "raw": result.stdout
        }
"""Dynamic skill management - Zero context waste"""

from typing import Dict, List, Optional


class SkillManager:
    """Dynamic skill loading based on context - Zero context waste"""
    
    SKILLS = {
        "web": {
            "triggers": ["web", "http", "api", "sqli", "xss", "ssti", "ssrf", "xxe", "idor", "graphql"],
            "tools": ["nuclei", "ffuf", "zap", "sqlmap", "xsstrike", "dalfox", "katana", "kiterunner"],
            "techniques": ["SQL Injection", "XSS", "SSRF", "SSTI", "XXE", "IDOR", "GraphQL Attacks"],
            "description": "Web application security testing"
        },
        "ad": {
            "triggers": ["ad", "domain", "windows", "ldap", "kerberos", "ntlm", "smb", "active directory"],
            "tools": ["netexec", "impacket", "bloodhound", "rubeus", "mimikatz", "crackmapexec"],
            "techniques": ["Kerberoasting", "ADCS Abuse", "NTLM Relay", "Pass-the-Hash", "DCSync"],
            "description": "Active Directory security assessment"
        },
        "cloud": {
            "triggers": ["aws", "azure", "gcp", "cloud", "s3", "lambda", "ec2", "cloudtrail", "iam"],
            "tools": ["prowler", "trivy", "pacu", "scoutsuite", "cloudfox", "steampipe"],
            "techniques": ["IAM Escalation", "Metadata API Abuse", "Storage Bucket Exploits"],
            "description": "Cloud security auditing"
        },
        "mobile": {
            "triggers": ["android", "ios", "apk", "ipa", "frida", "mobile", "root", "jailbreak"],
            "tools": ["mobsf", "frida", "objection", "apktool", "jadx"],
            "techniques": ["Static Analysis", "Dynamic Instrumentation", "SSL Bypass"],
            "description": "Mobile application security"
        },
        "osint": {
            "triggers": ["recon", "osint", "subdomain", "enum", "dns", "whois", "passive", "discovery"],
            "tools": ["amass", "subfinder", "httpx", "nmap", "masscan", "shodan", "censys"],
            "techniques": ["Passive Enumeration", "Active Discovery", "Fingerprinting"],
            "description": "OSINT and reconnaissance"
        },
        "exploit": {
            "triggers": ["exploit", "shellcode", "edr", "bypass", "rop", "buffer overflow", "exploitation"],
            "tools": ["ghidra", "pwntools", "metasploit", "veil", "shellter"],
            "techniques": ["EDR Evasion", "Shellcode Generation", "ROP Chains"],
            "description": "Exploit development"
        },
        "forensics": {
            "triggers": ["memory", "forensics", "dfir", "volatility", "dump", "malware", "incident"],
            "tools": ["volatility3", "autopsy", "yara", "rekall", "strings"],
            "techniques": ["Memory Analysis", "Rootkit Detection", "Timeline Analysis"],
            "description": "Digital forensics and incident response"
        },
        "wireless": {
            "triggers": ["wifi", "wireless", "wpa", "ble", "bluetooth", "zigbee", "rfid", "nfc"],
            "tools": ["aircrack-ng", "bettercap", "wifite", "gqrx"],
            "techniques": ["WPA Handshake Capture", "PMKID Attack", "Evil Twin", "BLE GATT"],
            "description": "Wireless security testing"
        },
        "container": {
            "triggers": ["docker", "kubernetes", "k8s", "container", "pod", "cri", "orchestration"],
            "tools": ["docker-bench", "kube-hunter", "falco", "trivy"],
            "techniques": ["Container Escape", "K8s Misconfigurations", "Privilege Escalation"],
            "description": "Container and Kubernetes security"
        },
        "password": {
            "triggers": ["password", "hash", "crack", "brute", "ntlm", "hashcat", "john", "cracking"],
            "tools": ["hashcat", "john", "hydra", "medusa"],
            "techniques": ["Dictionary Attack", "Brute Force", "Rule-based Cracking", "Rainbow Tables"],
            "description": "Password attack and cracking"
        },
        "binary": {
            "triggers": ["binary", "reverse", "engineering", "disassembly", "decompile", "radare", "ghidra"],
            "tools": ["ghidra", "radare2", "binaryninja", "capstone", "unicorn"],
            "techniques": ["Static Analysis", "Dynamic Analysis", "Binary Patching"],
            "description": "Binary reverse engineering"
        }
    }
    
    def __init__(self):
        self.loaded_skills: List[str] = []
    
    def detect_skills(self, context: str) -> List[str]:
        """Detect which skills are needed based on context"""
        detected = []
        context_lower = context.lower()
        
        for skill_name, skill_data in self.SKILLS.items():
            for trigger in skill_data["triggers"]:
                if trigger in context_lower:
                    detected.append(skill_name)
                    break
        
        return detected
    
    def load_skill(self, skill_name: str) -> Dict:
        """Load a skill and return its data"""
        if skill_name not in self.SKILLS:
            return {"error": f"Skill '{skill_name}' not found"}
        
        if skill_name in self.loaded_skills:
            return {"loaded": True, "skill": skill_name, "message": "Already loaded"}
        
        skill = self.SKILLS[skill_name]
        self.loaded_skills.append(skill_name)
        
        return {
            "loaded": True,
            "skill": skill_name,
            "tools": skill["tools"],
            "techniques": skill["techniques"],
            "description": skill["description"]
        }
    
    def get_loaded_skills(self) -> List[str]:
        return self.loaded_skills
    
    def list_all_skills(self) -> Dict:
        return self.SKILLS
    
    def get_skill_context(self) -> str:
        """Get context string for loaded skills"""
        if not self.loaded_skills:
            return ""
        
        context = "\n[LOADED SKILLS]\n"
        for skill_name in self.loaded_skills:
            skill = self.SKILLS[skill_name]
            context += f"- {skill_name.upper()}: {skill['description']}\n"
            context += f"  Tools: {', '.join(skill['tools'][:5])}\n"
        
        return context
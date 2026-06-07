"""Tool registry for security tools"""

import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path

from rich.console import Console

console = Console()


class ToolRegistry:
    """Central registry for all security tools"""
    
    def __init__(self):
        self.tools: Dict[str, Dict] = {}
        self._register_all_tools()
    
    def _register_all_tools(self):
        """Register all 50+ security tools"""
        
        # Reconnaissance tools
        self.tools["nmap"] = {"executable": "nmap", "category": "recon", "description": "Network discovery and port scanning"}
        self.tools["amass"] = {"executable": "amass", "category": "recon", "description": "Subdomain enumeration"}
        self.tools["subfinder"] = {"executable": "subfinder", "category": "recon", "description": "Fast subdomain discovery"}
        self.tools["httpx"] = {"executable": "httpx", "category": "recon", "description": "HTTP probing"}
        self.tools["masscan"] = {"executable": "masscan", "category": "recon", "description": "Massive port scanning"}
        self.tools["shodan"] = {"executable": "shodan", "category": "recon", "description": "Shodan API search"}
        
        # Web security tools
        self.tools["nuclei"] = {"executable": "nuclei", "category": "web", "description": "Vulnerability scanner"}
        self.tools["ffuf"] = {"executable": "ffuf", "category": "web", "description": "Web fuzzing"}
        self.tools["sqlmap"] = {"executable": "sqlmap", "category": "web", "description": "SQL injection"}
        self.tools["xsstrike"] = {"executable": "xsstrike", "category": "web", "description": "XSS detection"}
        self.tools["zap"] = {"executable": "zap-cli", "category": "web", "description": "OWASP ZAP scanner"}
        self.tools["dalfox"] = {"executable": "dalfox", "category": "web", "description": "XSS scanner"}
        self.tools["katana"] = {"executable": "katana", "category": "web", "description": "Web crawler"}
        self.tools["kiterunner"] = {"executable": "kiterunner", "category": "web", "description": "API content discovery"}
        
        # Active Directory tools
        self.tools["netexec"] = {"executable": "netexec", "category": "ad", "description": "Network exploitation"}
        self.tools["impacket"] = {"executable": "impacket", "category": "ad", "description": "Protocol implementations"}
        self.tools["bloodhound"] = {"executable": "bloodhound-python", "category": "ad", "description": "AD attack path mapping"}
        self.tools["crackmapexec"] = {"executable": "crackmapexec", "category": "ad", "description": "AD enumeration"}
        self.tools["rubeus"] = {"executable": "rubeus", "category": "ad", "description": "Kerberos attacks"}
        self.tools["mimikatz"] = {"executable": "mimikatz", "category": "ad", "description": "Credential extraction"}
        
        # Cloud security tools
        self.tools["prowler"] = {"executable": "prowler", "category": "cloud", "description": "Cloud security audit"}
        self.tools["trivy"] = {"executable": "trivy", "category": "cloud", "description": "Vulnerability scanning"}
        self.tools["pacu"] = {"executable": "pacu", "category": "cloud", "description": "AWS exploitation"}
        self.tools["scoutsuite"] = {"executable": "scout", "category": "cloud", "description": "Cloud audits"}
        self.tools["cloudfox"] = {"executable": "cloudfox", "category": "cloud", "description": "Cloud pentesting"}
        
        # Mobile security tools
        self.tools["mobsf"] = {"executable": "mobsf", "category": "mobile", "description": "Mobile security framework"}
        self.tools["frida"] = {"executable": "frida", "category": "mobile", "description": "Dynamic instrumentation"}
        self.tools["objection"] = {"executable": "objection", "category": "mobile", "description": "Runtime exploration"}
        self.tools["apktool"] = {"executable": "apktool", "category": "mobile", "description": "APK decompilation"}
        self.tools["jadx"] = {"executable": "jadx", "category": "mobile", "description": "Java decompiler"}
        
        # Binary analysis tools
        self.tools["ghidra"] = {"executable": "ghidra", "category": "binary", "description": "Reverse engineering"}
        self.tools["radare2"] = {"executable": "r2", "category": "binary", "description": "Binary analysis"}
        self.tools["pwntools"] = {"executable": "pwn", "category": "binary", "description": "Exploit framework"}
        self.tools["capstone"] = {"executable": "cstool", "category": "binary", "description": "Disassembly"}
        
        # Forensics tools
        self.tools["volatility"] = {"executable": "volatility3", "category": "forensics", "description": "Memory forensics"}
        self.tools["yara"] = {"executable": "yara", "category": "forensics", "description": "Malware detection"}
        self.tools["rekall"] = {"executable": "rekall", "category": "forensics", "description": "Memory analysis"}
        
        # Wireless tools
        self.tools["aircrack"] = {"executable": "aircrack-ng", "category": "wireless", "description": "WiFi auditing"}
        self.tools["bettercap"] = {"executable": "bettercap", "category": "wireless", "description": "MITM framework"}
        self.tools["wifite"] = {"executable": "wifite", "category": "wireless", "description": "Automated WiFi attacks"}
        
        # Password tools
        self.tools["hashcat"] = {"executable": "hashcat", "category": "password", "description": "Password cracking"}
        self.tools["john"] = {"executable": "john", "category": "password", "description": "John the Ripper"}
        self.tools["hydra"] = {"executable": "hydra", "category": "password", "description": "Network login brute force"}
        self.tools["medusa"] = {"executable": "medusa", "category": "password", "description": "Parallel brute force"}
        
        # Container tools
        self.tools["docker_bench"] = {"executable": "docker-bench-security", "category": "container", "description": "Docker security"}
        self.tools["kube_hunter"] = {"executable": "kube-hunter", "category": "container", "description": "K8s hunting"}
        self.tools["falco"] = {"executable": "falco", "category": "container", "description": "Runtime security"}
        
        # Exploit tools
        self.tools["metasploit"] = {"executable": "msfconsole", "category": "exploit", "description": "Exploit framework"}
        self.tools["veil"] = {"executable": "veil", "category": "exploit", "description": "Payload generation"}
    
    def check_available(self, tool_name: str) -> bool:
        """Check if a tool executable is available in PATH."""
        import shutil
        info = self.tools.get(tool_name)
        if not info:
            return False
        return shutil.which(info["executable"]) is not None

    def execute(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given arguments.

        Argument building rules (key -> CLI token):
        - bool True  -> --key (flag)
        - str/int starting with '-' -> passed as-is (already a flag)
        - '_target' or '_' prefixed keys -> positional argument (value only)
        - otherwise -> --key value pair
        """
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found", "available": list(self.tools.keys())}

        tool = self.tools[tool_name]
        executable = tool["executable"]
        cmd = [executable]

        for key, value in args.items():
            if value is None:
                continue
            str_value = str(value)
            if isinstance(value, bool):
                if value:
                    cmd.append(f"--{key}")
            elif key.startswith("_"):          # positional: _target, _1, etc.
                cmd.append(str_value)
            elif str_value.startswith("-"):    # already a raw flag/value
                cmd.append(str_value)
            else:
                cmd.append(f"--{key}")
                cmd.append(str_value)

        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                encoding="utf-8",
                errors="replace",
            )
            # Consider success if return code is 0 OR stdout has content and no fatal error
            success = result.returncode == 0 or (
                bool(result.stdout.strip()) and result.returncode < 2
            )
            return {
                "tool": tool_name,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": success,
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Tool '{tool_name}' timed out after 300 seconds", "success": False}
        except FileNotFoundError:
            return {
                "error": f"Tool '{tool_name}' (executable: '{executable}') not found in PATH. "
                         "Please install it first.",
                "success": False,
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def list_available(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())

    def list_installed(self) -> List[str]:
        """Return only tools whose executable is actually present in PATH."""
        return [name for name in self.tools if self.check_available(name)]
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        return self.tools.get(tool_name)
    
    def list_by_category(self, category: str) -> List[Dict]:
        return [{"name": k, **v} for k, v in self.tools.items() if v.get("category") == category]
    
    def get_tool_help(self, tool_name: str) -> str:
        """Get help for a specific tool"""
        info = self.tools.get(tool_name)
        if not info:
            return f"Tool '{tool_name}' not found"
        
        return f"""
Tool: {tool_name}
Category: {info.get('category')}
Description: {info.get('description')}
Executable: {info.get('executable')}

Usage examples:
  {tool_name} --help
"""
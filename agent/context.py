"""Session context management"""

import time
from typing import Dict, Any, List, Optional


class SessionContext:
    """Manages session state and findings"""
    
    def __init__(self):
        self.objective: str = ""
        self.target: str = ""
        self.findings: List[Dict] = []
        self.action_history: List[str] = []
        self.start_time: float = 0
        self.authorization_ref: Optional[str] = None
    
    def set_objective(self, objective: str, target: str, authorization: str = None):
        self.objective = objective
        self.target = target
        self.authorization_ref = authorization
        self.start_time = time.time()
    
    def get_state(self) -> Dict:
        return {
            "objective": self.objective,
            "target": self.target,
            "findings": self.findings,
            "action_history": self.action_history,
            "elapsed_time": time.time() - self.start_time,
            "authorization": self.authorization_ref,
            "total_findings": len(self.findings)
        }
    
    def update(self, tool: str, result: Dict):
        """Update context with tool execution result"""
        success = result.get("success", False)
        self.action_history.append(f"{tool}: {'success' if success else 'failed'}")
        
        if success and result.get("stdout"):
            finding = {
                "tool": tool,
                "output": result["stdout"][:2000],
                "timestamp": time.time(),
                "summary": self._extract_summary(result["stdout"])
            }
            self.findings.append(finding)
    
    def _extract_summary(self, output: str) -> str:
        """Extract a short summary from tool output"""
        lines = output.strip().split('\n')
        if lines:
            first_line = lines[0]
            if len(first_line) > 150:
                return first_line[:150] + "..."
            return first_line
        return "No output"
    
    def add_finding(self, finding: Dict):
        """Add a finding manually"""
        self.findings.append(finding)
    
    def generate_report(self, partial: bool = False) -> Dict:
        return {
            "objective": self.objective,
            "target": self.target,
            "authorization": self.authorization_ref,
            "total_findings": len(self.findings),
            "actions_taken": len(self.action_history),
            "actions": self.action_history,
            "findings": self.findings,
            "elapsed_time": round(time.time() - self.start_time, 2),
            "partial_report": partial
        }
    
    def clear(self):
        """Clear all context data"""
        self.objective = ""
        self.target = ""
        self.findings = []
        self.action_history = []
        self.authorization_ref = None
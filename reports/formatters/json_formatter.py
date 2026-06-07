"""JSON report formatter"""

import json
from typing import Dict, Any
from datetime import datetime


class JSONFormatter:
    """Format report as JSON"""
    
    extension = "json"
    
    def format(self, data: Dict[str, Any]) -> str:
        """Convert data to JSON"""
        
        report = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "version": "1.0",
                "tool": "TUKUB AI"
            },
            "assessment": {
                "objective": data.get('objective'),
                "target": data.get('target'),
                "authorization": data.get('authorization')
            },
            "summary": {
                "total_findings": data.get('total_findings', 0),
                "actions_taken": data.get('actions_taken', 0),
                "elapsed_time": data.get('elapsed_time', 0)
            },
            "findings": data.get('findings', []),
            "actions": data.get('actions', [])
        }
        
        return json.dumps(report, indent=2)
"""Report generation module"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from reports.formatters.markdown import MarkdownFormatter
from reports.formatters.json_formatter import JSONFormatter
from reports.formatters.html import HTMLFormatter


class ReportGenerator:
    """Generate reports in multiple formats"""
    
    FORMATTERS = {
        "markdown": MarkdownFormatter,
        "json": JSONFormatter,
        "html": HTMLFormatter
    }
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path.home() / ".tukub" / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, data: Dict[str, Any], format_type: str = "markdown") -> str:
        """Generate report in specified format"""
        
        formatter_class = self.FORMATTERS.get(format_type)
        if not formatter_class:
            raise ValueError(f"Unknown format: {format_type}")
        
        formatter = formatter_class()
        content = formatter.format(data)
        
        filename = f"tukub_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{formatter.extension}"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return str(filepath)
    
    def generate_markdown(self, data: Dict[str, Any]) -> str:
        """Generate markdown report"""
        return self.generate(data, "markdown")
    
    def generate_json(self, data: Dict[str, Any]) -> str:
        """Generate JSON report"""
        return self.generate(data, "json")
    
    def generate_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML report"""
        return self.generate(data, "html")
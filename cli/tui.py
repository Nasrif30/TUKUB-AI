"""Terminal User Interface for TUKUB AI"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.columns import Columns

console = Console()


class TukubTUI:
    """Terminal UI for TUKUB AI"""
    
    def __init__(self):
        self.running = True
        self.current_target = None
        self.current_objective = None
        self.findings = []
    
    def run(self):
        """Run the TUI"""
        self._show_header()
        
        while self.running:
            try:
                cmd = Prompt.ask("\n[bold cyan]TUKUB>[/bold cyan]")
                self._handle_command(cmd)
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        console.print("\n[yellow]Exiting TUKUB AI...[/yellow]")
    
    def _show_header(self):
        """Show TUI header"""
        header = Panel(
            "[bold cyan]TUKUB AI Interactive Terminal[/bold cyan]\n"
            "[yellow]Type 'help' for commands, 'exit' to quit[/yellow]\n"
            "[red]AUTHORIZED USE ONLY[/red]",
            border_style="cyan"
        )
        console.print(header)
    
    def _handle_command(self, cmd: str):
        """Handle user commands"""
        cmd_lower = cmd.lower().strip()
        
        if cmd_lower == "exit" or cmd_lower == "quit":
            self.running = False
        
        elif cmd_lower == "help":
            self._show_help()
        
        elif cmd_lower.startswith("set target"):
            self.current_target = cmd.replace("set target", "").strip()
            console.print(f"[green]Target set: {self.current_target}[/green]")
        
        elif cmd_lower.startswith("set objective"):
            self.current_objective = cmd.replace("set objective", "").strip()
            console.print(f"[green]Objective set: {self.current_objective}[/green]")
        
        elif cmd_lower == "status":
            self._show_status()
        
        elif cmd_lower == "clear":
            console.clear()
            self._show_header()
        
        elif cmd_lower == "findings":
            self._show_findings()
        
        else:
            console.print("[yellow]Unknown command. Type 'help' for available commands.[/yellow]")
    
    def _show_help(self):
        """Show help menu"""
        help_text = """
[bold cyan]Available Commands:[/bold cyan]

  [yellow]set target <ip/domain>[/yellow]     - Set target for assessment
  [yellow]set objective <text>[/yellow]       - Set testing objective
  [yellow]status[/yellow]                     - Show current status
  [yellow]findings[/yellow]                   - Show current findings
  [yellow]run[/yellow]                        - Start assessment
  [yellow]clear[/yellow]                      - Clear screen
  [yellow]help[/yellow]                       - Show this help
  [yellow]exit[/yellow]                       - Quit TUI

[bold red]REMEMBER: Only test systems you own or have permission to test[/bold red]
"""
        console.print(Panel(help_text, title="Help", border_style="cyan"))
    
    def _show_status(self):
        """Show current status"""
        status_table = Table(title="Current Status")
        status_table.add_column("Setting", style="cyan")
        status_table.add_column("Value", style="yellow")
        
        status_table.add_row("Target", self.current_target or "Not set")
        status_table.add_row("Objective", self.current_objective or "Not set")
        status_table.add_row("Findings", str(len(self.findings)))
        
        console.print(status_table)
    
    def _show_findings(self):
        """Show current findings"""
        if not self.findings:
            console.print("[yellow]No findings yet. Run an assessment first.[/yellow]")
            return
        
        findings_table = Table(title="Findings")
        findings_table.add_column("#", style="cyan")
        findings_table.add_column("Finding", style="white")
        
        for i, finding in enumerate(self.findings[-10:], 1):
            findings_table.add_row(str(i), str(finding)[:100])
        
        console.print(findings_table)
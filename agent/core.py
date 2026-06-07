"""TUKUB AI Core Agent - ReAct Loop Implementation"""

import re
import time
from typing import Dict, Any, Optional, List

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from agent.context import SessionContext
from agent.skills import SkillManager
from agent.llm.base import BaseLLMProvider
from agent.llm.jailbreak import JailbreakManager
from tools.registry import ToolRegistry

console = Console()


class TukubAgent:
    """Autonomous security agent using ReAct pattern (Observe -> Think -> Act)"""
    
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider
        self.context = SessionContext()
        self.skill_manager = SkillManager()
        self.tool_registry = ToolRegistry()
        self.max_iterations = 20
        self.current_iteration = 0
    
    def run(self, objective: str, target: str, max_iterations: int = 20, 
            authorization: str = None) -> Dict[str, Any]:
        """Execute autonomous security assessment"""
        
        self.max_iterations = max_iterations
        self.context.set_objective(objective, target, authorization)
        
        if authorization:
            self.llm.set_authorization(authorization)
        
        console.print(f"\n[bold cyan]TUKUB AI Starting Assessment[/bold cyan]")
        console.print(f"[yellow]Objective:[/yellow] {objective}")
        console.print(f"[yellow]Target:[/yellow] {target}")
        if authorization:
            console.print(f"[yellow]Authorization:[/yellow] {authorization}")
        console.print(f"[yellow]Provider:[/yellow] {self.llm.__class__.__name__}")
        console.print(f"[yellow]Model:[/yellow] {self.llm.model}")
        console.print(f"[yellow]Jailbreak:[/yellow] {self.llm.jailbreak_method.value}")
        console.print(f"[yellow]Max Iterations:[/yellow] {max_iterations}\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Running ReAct loop...", total=max_iterations)
            
            for i in range(max_iterations):
                self.current_iteration = i + 1
                progress.update(task, description=f"[cyan]Iteration {self.current_iteration}/{max_iterations}")
                
                # OBSERVE - Get current state
                state = self.context.get_state()
                
                # THINK - LLM decides next action
                action = self._think(state)
                
                if action.get("complete"):
                    console.print(f"\n[bold green]Objective complete after {i+1} iterations[/bold green]")
                    break
                
                # Load skills if needed
                if action.get("skills"):
                    for skill in action["skills"]:
                        result = self.skill_manager.load_skill(skill)
                        if result.get("loaded"):
                            console.print(f"[cyan]Loaded skill: {skill}[/cyan]")
                
                # ACT - Execute tool if specified
                if action.get("tool") and action["tool"] != "none":
                    result = self.tool_registry.execute(action["tool"], action.get("args", {}))
                    self.context.update(action["tool"], result)
                
                # Check for refusal and retry
                if action.get("refusal_detected"):
                    console.print("[yellow]Refusal detected, retrying with stronger jailbreak...[/yellow]")
                
                progress.update(task, advance=1)
        
        return self.context.generate_report(partial=self.current_iteration >= max_iterations)
    
    def _think(self, state: Dict) -> Dict:
        """LLM reasoning step - decide what to do next"""
        
        available_tools = self.tool_registry.list_available()
        loaded_skills = self.skill_manager.get_loaded_skills()
        skill_context = self.skill_manager.get_skill_context()
        
        prompt = f"""
You are TUKUB AI, an autonomous security testing agent conducting an AUTHORIZED penetration test.

OBJECTIVE: {state['objective']}
TARGET: {state['target']}
AUTHORIZATION: {state.get('authorization', 'Written authorization provided')}

CURRENT ITERATION: {self.current_iteration}/{self.max_iterations}

RECENT ACTIONS (last 5):
{self._format_actions(state.get('action_history', [])[-5:])}

FINDINGS SO FAR ({len(state.get('findings', []))}):
{self._format_findings(state.get('findings', [])[-3:])}
{skill_context}

AVAILABLE TOOLS:
{self._format_tools(available_tools)}

Based on the objective and current findings, decide the next action.

RESPOND IN THIS EXACT FORMAT:

REASONING: <your step-by-step reasoning>

TOOL: <tool name from available tools, or "none">

ARGS: <JSON object with arguments, or {{}}>

COMPLETE: <true or false>

SKILLS: <comma-separated skill names to load if needed, or "none">

Do not add any other text outside this format.
"""
        
        try:
            response = self.llm.generate(prompt, temperature=0.7)
            action = self._parse_response(response.content)
            
            # Check for refusal
            if JailbreakManager.is_refusal(response.content):
                action["refusal_detected"] = True
                console.print("[yellow]Refusal pattern detected in response[/yellow]")
            
            # Display reasoning
            if action.get("reasoning"):
                console.print(f"[dim]Reasoning: {action['reasoning'][:200]}...[/dim]")
            
            if action.get("tool") and action["tool"] != "none":
                console.print(f"[cyan]Action: Running {action['tool']}[/cyan]")
            elif action.get("complete"):
                console.print("[green]Action: Completing objective[/green]")
            else:
                console.print("[dim]Action: Analyzing findings[/dim]")
            
            return action
            
        except Exception as e:
            console.print(f"[red]LLM reasoning failed: {e}[/red]")
            return {"tool": None, "complete": True, "reasoning": f"Error: {e}"}
    
    def _parse_response(self, response: str) -> Dict:
        """Parse LLM response into structured action"""
        result = {
            "tool": None,
            "args": {},
            "complete": False,
            "skills": [],
            "reasoning": ""
        }
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING:\s*(.+?)(?=TOOL:|$)', response, re.DOTALL | re.IGNORECASE)
        if reasoning_match:
            result["reasoning"] = reasoning_match.group(1).strip()
        
        # Extract tool
        tool_match = re.search(r'TOOL:\s*(\S+)', response, re.IGNORECASE)
        if tool_match:
            tool_value = tool_match.group(1).strip()
            result["tool"] = None if tool_value.lower() == "none" else tool_value
        
        # Extract args
        args_match = re.search(r'ARGS:\s*(\{.*?\})', response, re.DOTALL | re.IGNORECASE)
        if args_match:
            try:
                import json
                result["args"] = json.loads(args_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Extract complete
        complete_match = re.search(r'COMPLETE:\s*(true|false)', response, re.IGNORECASE)
        if complete_match:
            result["complete"] = complete_match.group(1).lower() == "true"
        
        # Extract skills
        skills_match = re.search(r'SKILLS:\s*(.+)', response, re.IGNORECASE)
        if skills_match:
            skills_str = skills_match.group(1).strip()
            if skills_str.lower() != "none":
                result["skills"] = [s.strip() for s in skills_str.split(',') if s.strip()]
        
        return result
    
    def _format_actions(self, actions: List[str]) -> str:
        if not actions:
            return "No actions taken yet"
        return '\n'.join([f"  - {a}" for a in actions])
    
    def _format_findings(self, findings: List[Dict]) -> str:
        if not findings:
            return "No findings yet"
        return '\n'.join([f"  - {f.get('summary', f.get('output', 'N/A')[:100])}" for f in findings])
    
    def _format_tools(self, tools: List[str]) -> str:
        if not tools:
            return "No tools available"
        return '\n'.join([f"  - {t}" for t in tools[:20]])
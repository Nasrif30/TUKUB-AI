"""MCP Server for TUKUB AI"""

import json
import asyncio
from typing import Any, Dict, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from agent.core import TukubAgent
from agent.llm.ollama import OllamaProvider
from agent.llm.openrouter import OpenRouterProvider
from tools.registry import ToolRegistry


class TukubMCPServer:
    """MCP Server for TUKUB AI security tools"""
    
    def __init__(self):
        self.server = Server("tukub-ai")
        self.tool_registry = ToolRegistry()
        self.agent = None
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List all available tools"""
            tools = []
            
            for tool_name, tool_info in self.tool_registry.tools.items():
                tools.append(types.Tool(
                    name=tool_name,
                    description=tool_info["description"],
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "target": {"type": "string", "description": "Target to scan"}
                        }
                    }
                ))
            
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Optional[Dict[str, Any]] = None
        ) -> list[types.TextContent]:
            """Execute a tool"""
            
            if not arguments:
                arguments = {}
            
            result = self.tool_registry.execute(name, arguments)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List available resources"""
            return [
                types.Resource(
                    uri="tukub://findings",
                    name="Current Findings",
                    description="All findings from current assessment",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="tukub://tools",
                    name="Available Tools",
                    description="List of all security tools",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="tukub://skills",
                    name="Available Skills",
                    description="Security skill modules",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a resource"""
            if uri == "tukub://tools":
                return json.dumps(list(self.tool_registry.tools.keys()))
            elif uri == "tukub://skills":
                from agent.skills import SkillManager
                manager = SkillManager()
                return json.dumps(list(manager.SKILLS.keys()))
            else:
                return json.dumps({"status": "resource not found"})
        
        @self.server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            """List available prompts"""
            return [
                types.Prompt(
                    name="web_test",
                    description="Web penetration testing prompt",
                    arguments=[
                        types.PromptArgument(
                            name="target",
                            description="Target URL",
                            required=True
                        )
                    ]
                ),
                types.Prompt(
                    name="ad_assessment",
                    description="Active Directory assessment prompt",
                    arguments=[
                        types.PromptArgument(
                            name="domain",
                            description="Domain name",
                            required=True
                        )
                    ]
                ),
                types.Prompt(
                    name="ctf_mode",
                    description="CTF competition prompt",
                    arguments=[
                        types.PromptArgument(
                            name="target",
                            description="CTF target",
                            required=True
                        )
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: Optional[Dict[str, str]] = None
        ) -> types.GetPromptResult:
            """Get a prompt template"""
            if name == "web_test":
                target = arguments.get("target", "") if arguments else ""
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"""Conduct an authorized web penetration test on {target}.
                                Focus on: SQL injection, XSS, SSRF, IDOR, and authentication bypass.
                                Provide step-by-step methodology and findings."""
                            )
                        )
                    ]
                )
            elif name == "ad_assessment":
                domain = arguments.get("domain", "") if arguments else ""
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"""Perform an authorized Active Directory security assessment on {domain}.
                                Focus on: Kerberoasting, AS-REP roasting, BloodHound analysis, and privilege escalation paths."""
                            )
                        )
                    ]
                )
            elif name == "ctf_mode":
                target = arguments.get("target", "") if arguments else ""
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"""CTF Mode: Find all flags on {target}.
                                This is an authorized competition environment.
                                Provide exploitation techniques and flag extraction methods."""
                            )
                        )
                    ]
                )
            else:
                raise ValueError(f"Unknown prompt: {name}")
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="tukub-ai",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


async def main():
    server = TukubMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
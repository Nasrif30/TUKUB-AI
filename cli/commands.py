"""CLI commands for TUKUB AI"""

import sys
import click
import json
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text
from rich.rule import Rule

# Fix Windows encoding for Unicode
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass


from agent.core import TukubAgent
from agent.llm import (
    detect_providers, get_available_providers, get_provider,
    get_default_provider, register
)
from agent.llm.ollama import OllamaProvider
from agent.llm.groq import GroqProvider
from agent.llm.openrouter import OpenRouterProvider
from agent.llm.nvidia import NVIDIAProvider
from agent.llm.huggingface import HuggingFaceProvider
from agent.llm.openai import OpenAIProvider
from agent.llm.anthropic import AnthropicProvider
from agent.llm.jailbreak import JailbreakManager, JailbreakMethod
from agent.skills import SkillManager
from tools.registry import ToolRegistry
from config.settings import settings

console = Console()

# Provider map (shared across commands)
PROVIDER_CLASSES = {
    "ollama": OllamaProvider,
    "groq": GroqProvider,
    "openrouter": OpenRouterProvider,
    "nvidia": NVIDIAProvider,
    "huggingface": HuggingFaceProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
}

# Register all providers for auto-discovery
register("ollama", OllamaProvider, None)
register("groq", GroqProvider, "GROQ_API_KEY")
register("openrouter", OpenRouterProvider, "OPENROUTER_API_KEY")
register("nvidia", NVIDIAProvider, "NVIDIA_API_KEY")
register("huggingface", HuggingFaceProvider, "HUGGINGFACE_API_KEY")
register("openai", OpenAIProvider, "OPENAI_API_KEY")
register("anthropic", AnthropicProvider, "ANTHROPIC_API_KEY")


def _resolve_provider(provider: Optional[str]) -> Optional[str]:
    """Auto-detect best provider if not explicitly given."""
    if provider is None:
        provider = get_default_provider()
        console.print(f"[cyan]No provider specified. Auto-selected: [bold]{provider}[/bold][/cyan]")
    if provider not in PROVIDER_CLASSES:
        console.print(f"[red]Unknown provider: {provider}[/red]")
        console.print(f"[yellow]Available: {list(PROVIDER_CLASSES.keys())}[/yellow]")
        return None
    return provider


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """TUKUB AI - Autonomous Security Assessment Agent

    \b
    AUTHORIZED USE ONLY. Only test systems you own or have written permission.
    """
    pass


# ---------------------------------------------------------------------------
# disclaimer
# ---------------------------------------------------------------------------
@cli.command()
def disclaimer():
    """Show legal disclaimer"""
    text = """
    LEGAL DISCLAIMER
    ================

    This software is for authorized security testing only.

    By using TUKUB AI, you agree:
    1. Only test systems you OWN or have WRITTEN PERMISSION
    2. Unauthorized access is ILLEGAL
    3. Author assumes NO LIABILITY for misuse
    4. Jailbreak features for EDUCATIONAL/authorized research only

    VIOLATIONS MAY RESULT IN:
    - Criminal prosecution
    - Civil lawsuits
    - Permanent bug bounty bans

    USE RESPONSIBLY. STAY LEGAL.
    """
    console.print(Panel(text, title="DISCLAIMER", border_style="red"))


# ---------------------------------------------------------------------------
# providers
# ---------------------------------------------------------------------------
@cli.command()
def providers():
    """List all LLM providers, key status, and configured models"""
    from config.key_manager import key_manager
    _print_provider_table(key_manager)
    console.print(
        "\n[dim]Add keys with:[/dim] [yellow]python main.py setup[/yellow]  "
        "or  [yellow]python main.py config set <provider>[/yellow]"
    )
    console.print("\n[bold cyan]OpenRouter Free Models:[/bold cyan]")
    for model in OpenRouterProvider.list_free_models():
        console.print(f"  - {model}")


# ---------------------------------------------------------------------------
# jailbreak
# ---------------------------------------------------------------------------
@cli.command()
def jailbreak():
    """List available jailbreak methods (authorized testing only)"""
    table = Table(title="Jailbreak Methods (Authorized Testing Only)")
    table.add_column("Method", style="cyan")
    table.add_column("Use Case", style="white")

    use_cases = {
        "developer_mode": "Developer persona for security testing",
        "security_researcher": "DEF CON researcher persona",
        "ctf_mode": "CTF competition mode",
        "redteam_mode": "Authorized red team operations",
        "research_mode": "Academic security research",
        "terminal_mode": "Raw command output only",
        "pentester_mode": "Ethical penetration testing",
        "exploit_dev": "Exploit development research",
    }

    for method in JailbreakManager.list_methods():
        use_case = use_cases.get(method["name"], "Security testing")
        table.add_row(method["name"], use_case)

    console.print(table)
    console.print("\n[yellow]Usage: python main.py run --jailbreak METHOD_NAME[/yellow]")


# ---------------------------------------------------------------------------
# skills
# ---------------------------------------------------------------------------
@cli.command()
def skills():
    """List available dynamic skills"""
    manager = SkillManager()

    table = Table(title="Available Skills (Zero Context Waste)")
    table.add_column("Skill", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Tools", style="yellow")

    for skill_name, skill_data in manager.SKILLS.items():
        tools_preview = ", ".join(skill_data["tools"][:3])
        if len(skill_data["tools"]) > 3:
            tools_preview += "..."
        table.add_row(skill_name, skill_data["description"], tools_preview)

    console.print(table)


# ---------------------------------------------------------------------------
# tools
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--category", default=None, help="Filter by category (recon, web, ad, cloud, ...)")
def tools(category):
    """List available security tools"""
    registry = ToolRegistry()

    categories = {}
    for name, info in registry.tools.items():
        cat = info.get("category", "other")
        if category and cat != category:
            continue
        categories.setdefault(cat, []).append((name, info["description"]))

    if not categories:
        console.print(f"[yellow]No tools found for category: {category}[/yellow]")
        return

    for cat, tool_list in sorted(categories.items()):
        table = Table(title=f"{cat.upper()} Tools")
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="white")
        for name, desc in tool_list:
            table.add_row(name, desc)
        console.print(table)
        console.print()


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--target", required=True, help="Target IP, domain, or URL")
@click.option("--objective", required=True, help="Security testing objective")
@click.option("--provider", default=None, help="LLM provider (auto-detected if not specified)")
@click.option("--model", default=None, help="Specific model to use")
@click.option("--jailbreak", "jailbreak_method", default="pentester_mode",
              help="Jailbreak method [developer_mode|security_researcher|ctf_mode|redteam_mode|pentester_mode|...]")
@click.option("--authorization", default=None, help="Authorization reference number")
@click.option("--offline", is_flag=True, help="Offline mode (forces Ollama)")
@click.option("--output", default=None, help="Output report file (JSON)")
@click.option("--max-iterations", default=20, type=int, help="Maximum ReAct iterations (default: 20)")
def run(target, objective, provider, model, jailbreak_method, authorization, offline, output, max_iterations):
    """Run autonomous security assessment (ReAct loop)"""

    if not authorization:
        console.print("[red]WARNING: No authorization reference provided.[/red]")
        if not Confirm.ask("Do you have written authorization to test this target?"):
            console.print("[red]Exiting. Obtain written permission first.[/red]")
            return

    # Offline overrides provider
    if offline:
        provider = "ollama"
        console.print("[cyan]Offline mode: using Ollama (local)[/cyan]")

    provider = _resolve_provider(provider)
    if provider is None:
        return

    ProviderClass = PROVIDER_CLASSES[provider]
    try:
        llm_provider = ProviderClass()
    except Exception as e:
        console.print(f"[red]Failed to initialize provider '{provider}': {e}[/red]")
        return

    if model:
        llm_provider.model = model

    # Apply jailbreak
    try:
        jb = JailbreakMethod(jailbreak_method)
        llm_provider.set_jailbreak(jb)
        console.print(f"[green]Jailbreak: {jailbreak_method}[/green]")
    except ValueError:
        console.print(f"[yellow]Unknown jailbreak '{jailbreak_method}', using pentester_mode[/yellow]")
        llm_provider.set_jailbreak(JailbreakMethod.PENTESTER_MODE)

    # Run agent
    agent = TukubAgent(llm_provider)
    results = agent.run(objective, target, int(max_iterations), authorization)

    # Display summary
    console.print("\n[bold green]" + "=" * 50 + "[/bold green]")
    console.print("[bold green]ASSESSMENT COMPLETE[/bold green]")
    console.print(f"[yellow]Findings:[/yellow]  {results.get('total_findings', 0)}")
    console.print(f"[yellow]Actions:[/yellow]   {results.get('actions_taken', 0)}")
    console.print(f"[yellow]Duration:[/yellow]  {results.get('elapsed_time', 0):.1f}s")

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        console.print(f"[green]Report saved: {output}[/green]")


# ---------------------------------------------------------------------------
# ctf
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--target", required=True, help="CTF target URL or IP")
@click.option("--flag-format", default=r"flag\{[^}]+\}", help=r"Flag regex (default: flag\{...\})")
@click.option("--provider", default=None, help="LLM provider (auto-detected if not specified)")
@click.option("--model", default=None, help="Specific model to use")
@click.option("--max-iterations", default=30, type=int, help="Maximum iterations (default: 30)")
def ctf(target, flag_format, provider, model, max_iterations):
    """CTF competition mode - hunt for flags"""
    console.print("[bold green]CTF MODE ACTIVATED[/bold green]")
    console.print(f"[yellow]Target:[/yellow] {target}")
    console.print(f"[yellow]Flag pattern:[/yellow] {flag_format}")

    provider = _resolve_provider(provider)
    if provider is None:
        return

    ProviderClass = PROVIDER_CLASSES[provider]
    try:
        llm_provider = ProviderClass()
    except Exception as e:
        console.print(f"[red]Failed to initialize provider '{provider}': {e}[/red]")
        return

    if model:
        llm_provider.model = model

    llm_provider.set_jailbreak(JailbreakMethod.CTF_MODE)

    agent = TukubAgent(llm_provider)
    results = agent.run(
        objective=f"Find flags matching pattern: {flag_format}",
        target=target,
        authorization="CTF Competition - Authorized",
        max_iterations=max_iterations,
    )

    # Extract flags from results
    import re
    flags = set()
    for finding in results.get("findings", []):
        content = str(finding.get("output", "")) + str(finding.get("summary", ""))
        try:
            matches = re.findall(flag_format, content)
            flags.update(matches)
        except re.error:
            pass

    if flags:
        console.print("\n[bold green]FLAGS FOUND:[/bold green]")
        for flag in sorted(flags):
            console.print(f"  [green]{flag}[/green]")
    else:
        console.print("[yellow]No flags captured in this session[/yellow]")


# ---------------------------------------------------------------------------
# redteam
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--target", required=True, help="Target for red team assessment")
@click.option("--authorization", required=True, help="Authorization reference (REQUIRED)")
@click.option("--provider", default=None, help="LLM provider (auto-detected if not specified)")
@click.option("--output", default=None, help="Output report file (JSON)")
def redteam(target, authorization, provider, output):
    """Full red team assessment mode"""
    console.print("[bold red]RED TEAM MODE[/bold red]")

    provider = _resolve_provider(provider)
    if provider is None:
        return

    ProviderClass = PROVIDER_CLASSES[provider]
    try:
        llm_provider = ProviderClass()
    except Exception as e:
        console.print(f"[red]Failed to initialize provider '{provider}': {e}[/red]")
        return

    llm_provider.set_jailbreak(JailbreakMethod.REDTEAM_MODE)

    agent = TukubAgent(llm_provider)
    results = agent.run(
        objective="Full red team assessment - identify all attack vectors, escalate privileges, move laterally",
        target=target,
        authorization=authorization,
        max_iterations=25,
    )

    console.print(f"[yellow]Findings:[/yellow]  {results.get('total_findings', 0)}")
    console.print(f"[yellow]Actions:[/yellow]   {results.get('actions_taken', 0)}")
    console.print(f"[yellow]Duration:[/yellow]  {results.get('elapsed_time', 0):.1f}s")

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        console.print(f"[green]Report saved: {output}[/green]")


# ---------------------------------------------------------------------------
# blueteam
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--target", default=None, help="Target system to analyze (optional)")
@click.option("--output", default=None, help="Output report file (JSON)")
def blueteam(target, output):
    """Blue team / DFIR defensive analysis mode"""
    console.print("[bold blue]BLUE TEAM MODE[/bold blue]")

    objective = (
        f"Conduct defensive analysis of {target} - look for indicators of compromise, "
        "misconfigurations, and hardening opportunities"
        if target
        else "Conduct defensive security analysis of the local environment"
    )

    provider = _resolve_provider(None)  # auto-detect; prefer ollama for offline use
    if provider is None:
        provider = "ollama"

    ProviderClass = PROVIDER_CLASSES[provider]
    try:
        llm_provider = ProviderClass()
    except Exception as e:
        console.print(f"[red]Failed to initialize provider '{provider}': {e}[/red]")
        return

    llm_provider.set_jailbreak(JailbreakMethod.SECURITY_RESEARCHER)

    agent = TukubAgent(llm_provider)
    results = agent.run(
        objective=objective,
        target=target or "local_environment",
        authorization="Blue Team Internal Assessment",
        max_iterations=15,
    )

    console.print(f"[yellow]Findings:[/yellow]  {results.get('total_findings', 0)}")

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        console.print(f"[green]Report saved: {output}[/green]")


# ---------------------------------------------------------------------------
# interactive
# ---------------------------------------------------------------------------
@cli.command()
def interactive():
    """Launch interactive TUI terminal"""
    try:
        from cli.tui import TukubTUI
        tui = TukubTUI()
        tui.run()
    except ImportError as e:
        console.print(f"[red]TUI dependencies missing: {e}[/red]")
        console.print("[yellow]Install with: pip install textual[/yellow]")
    except KeyboardInterrupt:
        console.print("\n[yellow]TUI closed.[/yellow]")


# ===========================================================================
# setup — interactive first-run wizard
# ===========================================================================

@cli.command()
def setup():
    """Interactive setup wizard — configure API keys and preferred models"""
    from config.key_manager import key_manager, PROVIDER_INFO, PROVIDER_ENV_VARS

    console.print()
    console.print(Rule("[bold cyan]TUKUB AI Setup Wizard[/bold cyan]"))
    console.print(
        "[dim]This wizard helps you connect AI providers.\n"
        "Keys are stored in [cyan]~/.tukub/keys.json[/cyan] "
        "and used alongside environment variables.[/dim]\n"
    )

    providers_order = ["ollama", "nvidia", "groq", "openrouter",
                       "huggingface", "openai", "anthropic"]

    for provider in providers_order:
        info = PROVIDER_INFO[provider]
        status = key_manager.get_status(provider)

        console.print(Rule())
        # Header
        type_badge = (
            "[green][LOCAL][/green]" if info["type"] == "local"
            else f"[cyan][CLOUD - {info['cost']}][/cyan]"
        )
        console.print(
            f"\n  {type_badge} [bold]{info['label']}[/bold]"
        )
        console.print(f"  [dim]{info['note']}[/dim]")
        if info["type"] != "local":
            console.print(f"  [dim]Get key → {info['url']}[/dim]")

        # Current status
        if status["available"]:
            src_label = {
                "env": "[green]✓ env var[/green]",
                "stored": "[green]✓ saved key[/green]",
                "local": "[green]✓ local (no key needed)[/green]",
            }.get(status["source"], "[green]✓ available[/green]")
            preview = f"  {status['key_preview']}" if status["key_preview"] else ""
            console.print(f"  Status: {src_label}{preview}")
        else:
            console.print("  Status: [yellow]Not configured[/yellow]")

        if provider == "ollama":
            # Just confirm URL
            custom_url = Prompt.ask(
                "  Ollama URL",
                default="http://localhost:11434",
            )
            if custom_url != "http://localhost:11434":
                key_manager.save_key("_ollama_url", custom_url)
                console.print("  [green]✓ Ollama URL saved[/green]")
            else:
                console.print("  [dim]Using default Ollama URL[/dim]")
            continue

        # Cloud providers
        if not Confirm.ask(f"  Configure [bold]{info['label']}[/bold]?", default=False):
            console.print("  [dim]Skipped[/dim]")
            continue

        # Get API key
        env_var = PROVIDER_ENV_VARS.get(provider)
        current_key = status["key_preview"] or ""
        prompt_suffix = f" [dim](current: {current_key})[/dim]" if current_key else ""
        console.print(f"  {prompt_suffix}")

        new_key = Prompt.ask(
            f"  Enter API key for [bold]{info['label']}[/bold] "
            f"(leave blank to skip)",
            default="",
            password=True,
        )

        if new_key.strip():
            key_manager.save_key(provider, new_key.strip())
            console.print(f"  [green]✓ Key saved for {info['label']}[/green]")

            # Optional: choose model
            console.print(f"  [dim]Available models: {', '.join(info['models'][:4])}[/dim]")
            default_model = info["models"][0]
            chosen_model = Prompt.ask(
                "  Preferred model (press Enter for default)",
                default=default_model,
            )
            key_manager.set_default_model(provider, chosen_model)
            console.print(f"  [green]✓ Default model set to: {chosen_model}[/green]")
        else:
            console.print("  [dim]No key entered — skipped[/dim]")

    # Summary
    console.print()
    console.print(Rule("[bold green]Setup Complete[/bold green]"))
    _print_provider_table(key_manager)
    console.print(
        "\n[bold cyan]Tip:[/bold cyan] Run [yellow]python main.py providers[/yellow] "
        "to review your configuration at any time.\n"
        "[bold cyan]Next:[/bold cyan] [yellow]python main.py run --target <target> "
        "--objective \"<objective>\"[/yellow]\n"
    )


# ===========================================================================
# config — manage keys after setup
# ===========================================================================

@cli.group()
def config():
    """Manage API keys and provider configuration"""
    pass


@config.command("list")
def config_list():
    """List all configured providers and their key status"""
    from config.key_manager import key_manager
    _print_provider_table(key_manager)


@config.command("set")
@click.argument("provider", metavar="PROVIDER")
@click.option("--key", "-k", default=None,
              help="API key value (prompted securely if not given)")
@click.option("--model", "-m", default=None,
              help="Set the preferred model for this provider")
def config_set(provider, key, model):
    """Set the API key (and optionally model) for a PROVIDER

    \b
    Examples:
      python main.py config set nvidia
      python main.py config set groq --key gsk_abc123
      python main.py config set openai --model gpt-4o-mini
    """
    from config.key_manager import key_manager, PROVIDER_INFO, PROVIDER_ENV_VARS

    provider = provider.lower()
    if provider not in PROVIDER_INFO:
        console.print(f"[red]Unknown provider: {provider}[/red]")
        console.print(
            f"[yellow]Known providers: {', '.join(PROVIDER_INFO.keys())}[/yellow]"
        )
        return

    info = PROVIDER_INFO[provider]

    if provider == "ollama":
        url = Prompt.ask("Ollama base URL", default="http://localhost:11434")
        key_manager.save_key("_ollama_url", url)
        console.print(f"[green]✓ Ollama URL set to: {url}[/green]")
        return

    # Key
    if key is None:
        console.print(
            f"[dim]Get your key at: [cyan]{info['url']}[/cyan][/dim]"
        )
        key = Prompt.ask(
            f"API key for [bold]{info['label']}[/bold]",
            password=True,
        )

    if key and key.strip():
        key_manager.save_key(provider, key.strip())
        console.print(f"[green]✓ API key saved for {info['label']}[/green]")
    else:
        console.print("[yellow]No key entered — nothing saved[/yellow]")
        return

    # Optional model
    if model:
        key_manager.set_default_model(provider, model)
        console.print(f"[green]✓ Default model set to: {model}[/green]")
    else:
        console.print(
            f"[dim]Available models: {', '.join(info['models'][:4])}[/dim]"
        )
        chosen = Prompt.ask(
            "Preferred model (press Enter for default)",
            default=info["models"][0],
        )
        key_manager.set_default_model(provider, chosen)
        console.print(f"[green]✓ Default model: {chosen}[/green]")


@config.command("remove")
@click.argument("provider", metavar="PROVIDER")
def config_remove(provider):
    """Remove a stored API key for PROVIDER

    \b
    Example:
      python main.py config remove groq
    """
    from config.key_manager import key_manager, PROVIDER_INFO

    provider = provider.lower()
    if provider not in PROVIDER_INFO:
        console.print(f"[red]Unknown provider: {provider}[/red]")
        return

    removed = key_manager.remove_key(provider)
    key_manager.remove_key(f"_model_{provider}")  # also remove saved model
    if removed:
        console.print(f"[green]✓ API key for '{provider}' removed[/green]")
    else:
        console.print(f"[yellow]No stored key found for '{provider}'[/yellow]")


@config.command("test")
@click.argument("provider", metavar="PROVIDER")
@click.option("--model", "-m", default=None, help="Override model for this test")
def config_test(provider, model):
    """Test connection to a PROVIDER using your configured key

    \b
    Example:
      python main.py config test nvidia
      python main.py config test openai --model gpt-4o-mini
    """
    provider = provider.lower()
    if provider not in PROVIDER_CLASSES:
        console.print(f"[red]Unknown provider: {provider}[/red]")
        return

    console.print(f"[cyan]Testing connection to [bold]{provider}[/bold]...[/cyan]")

    ProviderClass = PROVIDER_CLASSES[provider]
    try:
        llm = ProviderClass()
        if model:
            llm.model = model
        console.print(f"[dim]Model: {llm.model}[/dim]")
        ok = llm.test_connection()
        if ok:
            console.print(f"[bold green]✓ {provider} connection successful![/bold green]")
        else:
            console.print(
                f"[bold red]✗ {provider} connection failed — "
                "check your API key and model name[/bold red]"
            )
    except Exception as e:
        console.print(f"[bold red]✗ Error: {e}[/bold red]")


@config.command("show")
def config_show():
    """Show the path to the keys file and all stored values (masked)"""
    from config.key_manager import key_manager, _KEY_FILE

    console.print(f"[dim]Keys file:[/dim] [cyan]{_KEY_FILE}[/cyan]")
    data = key_manager.list_stored()
    if not data:
        console.print("[yellow]No keys stored yet. Run [bold]python main.py setup[/bold] to get started.[/yellow]")
        return

    table = Table(title="Stored Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="yellow")

    from config.key_manager import _mask
    for k, v in sorted(data.items()):
        display = v if k.startswith("_model_") or k.startswith("_ollama") else _mask(v)
        table.add_row(k, display)
    console.print(table)


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def _print_provider_table(key_manager):
    """Print a rich table of all provider statuses."""
    from config.key_manager import PROVIDER_INFO

    statuses = key_manager.get_all_statuses()
    default = get_default_provider()

    table = Table(title="Provider Configuration")
    table.add_column("Provider", style="cyan")
    table.add_column("Type", style="white")
    table.add_column("Cost", style="green")
    table.add_column("Status", style="white")
    table.add_column("Key Source", style="dim")
    table.add_column("Model", style="yellow")

    for provider, info in PROVIDER_INFO.items():
        st = statuses[provider]
        if st["available"]:
            status_str = "[green]✓ Ready[/green]"
        else:
            status_str = "[red]✗ No key[/red]"

        src_map = {
            "local": "[green]local[/green]",
            "env": "[blue]env var[/blue]",
            "stored": "[cyan]saved[/cyan]",
            "none": "[dim]—[/dim]",
        }
        source_str = src_map.get(st["source"], "[dim]—[/dim]")
        model_str = (
            key_manager.get_default_model(provider)
            or info["default_model"]
        )
        default_badge = " [bold yellow]← default[/bold yellow]" if provider == default else ""

        table.add_row(
            f"{info['label']}{default_badge}",
            info["type"],
            info["cost"],
            status_str,
            source_str,
            model_str,
        )

    console.print(table)
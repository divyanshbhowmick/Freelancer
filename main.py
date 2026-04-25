#!/usr/bin/env python3
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

load_dotenv()

console = Console()

QUICK_STARTS = [
    ("1", "Write an Upwork proposal for a Cloud Cost job post"),
    ("2", "Write a LinkedIn post (K8s audit format)"),
    ("3", "Write a cold DM for a Series B startup on LinkedIn"),
    ("4", "Show my Week 1 tasks and mark what I've done"),
    ("5", "Calculate my projected income this month"),
    ("6", "Write a follow-up DM for a connection I made 4 days ago"),
    ("7", "Give me a discovery call script for a cloud cost prospect"),
    ("8", "Draft a SOW for a 3-week Elasticsearch optimization project"),
]

HELP_TEXT = """
[bold]Commands:[/bold]
  [cyan]/reset[/cyan]   — Start a new conversation (clears history)
  [cyan]/tasks[/cyan]   — Show all weekly tasks
  [cyan]/quit[/cyan]    — Exit

[bold]Quick starts:[/bold]  Type a number 1–8 to use a preset prompt
"""


def print_banner():
    text = Text()
    text.append("Freelance Domination Bot", style="bold white")
    text.append("\n₹2L/month from global clients — Java · DevOps · Elasticsearch", style="dim")
    console.print(Panel(text, border_style="bright_blue", padding=(0, 2)))


def print_quick_starts():
    lines = ["[dim]Quick starts:[/dim]"]
    for key, label in QUICK_STARTS:
        lines.append(f"  [cyan]{key}[/cyan]  {label}")
    console.print("\n".join(lines))
    console.print()


def show_all_tasks():
    from tracker import get_progress, WEEKLY_PLAN
    progress = get_progress()
    for week_key, data in progress.items():
        done = data["done"]
        total = data["total"]
        bar = "█" * done + "░" * (total - done)
        console.print(f"\n[bold]{data['label']}[/bold]  [{done}/{total}] {bar}")
        for task in data["completed_tasks"]:
            console.print(f"  [green]✓[/green] {task}")
        for task in data["pending_tasks"]:
            console.print(f"  [dim]○[/dim] {task}")


def resolve_input(raw: str) -> str:
    stripped = raw.strip()
    for key, label in QUICK_STARTS:
        if stripped == key:
            return label
    return stripped


def main():
    print_banner()
    print_quick_starts()

    try:
        from agent import FreelanceStrategyBot
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print(
            "Run:  [cyan]cp .env.example .env[/cyan]  then add your ANTHROPIC_API_KEY"
        )
        sys.exit(1)

    bot = FreelanceStrategyBot()
    console.print("[dim]Type your question, a number (1–8), /reset, /tasks, or /quit[/dim]\n")

    while True:
        try:
            raw = Prompt.ask("[bold blue]You[/bold blue]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not raw.strip():
            continue

        cmd = raw.strip().lower()

        if cmd in ("/quit", "/exit", "quit", "exit"):
            console.print("[dim]Goodbye.[/dim]")
            break

        if cmd == "/reset":
            bot.reset()
            console.print("[dim]Conversation reset.[/dim]\n")
            continue

        if cmd == "/tasks":
            show_all_tasks()
            console.print()
            continue

        if cmd in ("/help", "help"):
            console.print(HELP_TEXT)
            continue

        user_input = resolve_input(raw)

        console.print("\n[bold green]Bot[/bold green]  ", end="")
        try:
            bot.chat(user_input)
        except anthropic.APIStatusError as e:
            console.print(f"\n[bold red]API error {e.status_code}:[/bold red] {e.message}")
        except anthropic.APIConnectionError:
            console.print("\n[bold red]Connection error.[/bold red] Check your internet and try again.")
        except Exception as e:
            console.print(f"\n[bold red]Unexpected error:[/bold red] {e}")
        console.print()


if __name__ == "__main__":
    import anthropic  # noqa: F401 — validate import before bot init
    main()

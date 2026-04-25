#!/usr/bin/env python3
import sys
import anyio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()

QUICK_STARTS = [
    ("1", "Write an Upwork proposal for a Cloud Cost job post"),
    ("2", "Write a LinkedIn post (K8s audit format)"),
    ("3", "Write a cold DM for a Series B startup on LinkedIn"),
    ("4", "What are my Week 1 tasks and which should I do first?"),
    ("5", "Calculate my projected income: 2 retainers at ₹60k + one ₹70k project"),
    ("6", "Write a follow-up DM for a connection I made 4 days ago"),
    ("7", "Give me a discovery call script for a cloud cost prospect"),
    ("8", "Draft a SOW for a 3-week Elasticsearch optimization project"),
]

HELP_TEXT = """
[bold]Commands:[/bold]
  [cyan]/save [name][/cyan]  — Save last response to outputs/ folder
  [cyan]/tasks[/cyan]        — Show 30-day tracker (all weeks)
  [cyan]/done week1 0 2[/cyan] — Mark tasks 0 and 2 in week1 as done
  [cyan]/reset[/cyan]        — Start a fresh conversation
  [cyan]/quit[/cyan]         — Exit

[bold]Quick starts:[/bold] type a number 1–8
"""


def print_banner() -> None:
    t = Text()
    t.append("Freelance Domination Bot", style="bold white")
    t.append("\n₹2L/month from global clients  ·  Java · DevOps · Elasticsearch", style="dim")
    console.print(Panel(t, border_style="bright_blue", padding=(0, 2)))


def print_quick_starts() -> None:
    lines = ["[dim]Quick starts:[/dim]"]
    for key, label in QUICK_STARTS:
        lines.append(f"  [cyan]{key}[/cyan]  {label}")
    console.print("\n".join(lines))
    console.print()


def show_tasks() -> None:
    from tracker import get_progress
    progress = get_progress()
    for wk, data in progress.items():
        done, total = data["done"], data["total"]
        bar = "█" * done + "░" * (total - done)
        console.print(f"\n[bold]{data['label']}[/bold]  [{done}/{total}] {bar}")
        for task in data["completed_tasks"]:
            console.print(f"  [green]✓[/green] {task}")
        for task in data["pending_tasks"]:
            console.print(f"  [dim]○[/dim] {task}")
    console.print()


def handle_done(parts: list[str]) -> None:
    from tracker import update_progress
    if len(parts) < 3:
        console.print("[yellow]Usage: /done week1 0 2 3[/yellow]")
        return
    week = parts[1]
    try:
        indices = [int(x) for x in parts[2:]]
    except ValueError:
        console.print("[yellow]Task indices must be numbers.[/yellow]")
        return
    result = update_progress(week, indices)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
    else:
        console.print(f"[green]Marked done in {week}:[/green]")
        for t in result["newly_completed"]:
            console.print(f"  ✓ {t}")


def resolve_input(raw: str) -> str:
    stripped = raw.strip()
    for key, label in QUICK_STARTS:
        if stripped == key:
            return label
    return stripped


async def main() -> None:
    print_banner()
    print_quick_starts()

    from agent import FreelanceStrategyBot
    bot = FreelanceStrategyBot()

    console.print("[dim]Starting session…[/dim]")
    try:
        await bot.start()
    except Exception as e:
        console.print(f"[bold red]Failed to start:[/bold red] {e}")
        console.print(
            "\nMake sure [cyan]claude[/cyan] CLI is installed and you're logged in:\n"
            "  npm install -g @anthropic-ai/claude-code\n"
            "  claude login"
        )
        sys.exit(1)

    console.print("[dim]Ready. Type a question, a number (1–8), or /help[/dim]\n")

    try:
        while True:
            try:
                raw = Prompt.ask("[bold blue]You[/bold blue]")
            except (EOFError, KeyboardInterrupt):
                console.print("\n[dim]Goodbye.[/dim]")
                break

            if not raw.strip():
                continue

            cmd = raw.strip()
            lower = cmd.lower()

            if lower in ("/quit", "/exit", "quit", "exit"):
                console.print("[dim]Goodbye.[/dim]")
                break

            if lower == "/help":
                console.print(HELP_TEXT)
                continue

            if lower == "/tasks":
                show_tasks()
                continue

            if lower.startswith("/done"):
                handle_done(lower.split())
                continue

            if lower.startswith("/save"):
                parts = cmd.split(maxsplit=1)
                name = parts[1] if len(parts) > 1 else "response"
                path = bot.save_last(name)
                if path:
                    console.print(f"[green]Saved →[/green] {path}")
                else:
                    console.print("[yellow]Nothing to save yet — ask the bot something first.[/yellow]")
                continue

            if lower == "/reset":
                await bot.reset()
                console.print("[dim]Conversation reset.[/dim]\n")
                continue

            user_input = resolve_input(raw)
            console.print("\n[bold green]Bot[/bold green]  ", end="")
            try:
                await bot.chat(user_input)
            except Exception as e:
                console.print(f"\n[bold red]Error:[/bold red] {e}")
            console.print()
    finally:
        await bot.stop()


if __name__ == "__main__":
    anyio.run(main)

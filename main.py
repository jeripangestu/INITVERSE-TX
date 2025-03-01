import asyncio
from utils import run_all
from utils import data
from rich.console import Console
from rich.progress import Progress
from rich.text import Text

console = Console()

private_keys = data.get("private_keys", [])

async def countdown(seconds):
    """Menampilkan countdown dengan progress bar."""
    with Progress() as progress:
        task = progress.add_task("[cyan]Menunggu untuk restart...", total=seconds)
        for _ in range(seconds):
            await asyncio.sleep(1)
            progress.update(task, advance=1)

async def main():
    while True:
        console.print("[bold green]🔥 Memulai proses trading...[/bold green]")
        await run_all(private_keys)
        
        console.print("\n[bold yellow]⏳ Semua proses selesai. Menunggu 1 jam sebelum menjalankan ulang...[/bold yellow]")
        await countdown(3600)  # Countdown 1 jam sebelum restart

asyncio.run(main())

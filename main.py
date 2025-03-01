import asyncio
from utils import run_all, data
from rich.console import Console
from rich.progress import Progress
from rich.text import Text

console = Console()
private_keys = data.get("private_keys", [])

def show_banner():
    """Menampilkan banner berwarna di terminal."""
    banner = """[bold blue]____                            [/bold blue]
   [bold blue]/ __ \____ __________ ______[/bold blue]    
  [bold blue]/ / / / __ `/ ___/ __ `/ ___/[/bold blue]    
 [bold blue]/ /_/ / /_/ (__  ) /_/ / /[/bold blue]        
[bold blue]/_____/_\__,_/____/\__,_/_/[/bold blue]          
    
    [bold green]____                       [/bold green][bold yellow]__[/bold yellow]    
   [bold green]/ __ \\___  ____ ___  __  __/ /_[/bold green] [bold yellow]______  ____ _[/bold yellow]    
  [bold green]/ /_/ / _ \\/ __ `__ \\/ / / / / /[/bold green] [bold yellow]/ __ \\/ __ `/[/bold yellow]    
 [bold green]/ ____/  __/ / / / / / /_/ / / /[/bold green] [bold yellow]/ / / / /_/ /[/bold yellow]     
[bold green]/_/    \\___/_/ /_/ /_/\\__,_/_/[/bold green] [bold yellow]/ / /_/\\__, /[/bold yellow]      
                                         [bold yellow]/____/[/bold yellow]        
    
====================================================    
     [bold magenta]Automation[/bold magenta]         : [bold cyan]Auto Install Node and Bot[/bold cyan]    
     [bold magenta]Telegram Channel[/bold magenta]   : [bold cyan]@dasarpemulung[/bold cyan]    
     [bold magenta]Telegram Group[/bold magenta]     : [bold cyan]@parapemulung[/bold cyan]    
     [bold magenta]Credit[/bold magenta]             : [bold cyan]@jeripangestu, @Anywiz[/bold cyan]  
====================================================    
    """
    console.print(banner)

async def countdown(seconds):
    """Menampilkan countdown dengan progress bar."""
    with Progress() as progress:
        task = progress.add_task("[cyan]⏳ Menunggu untuk restart...", total=seconds)
        for _ in range(seconds):
            await asyncio.sleep(1)
            progress.update(task, advance=1)

async def main():
    show_banner()  # Tampilkan banner saat mulai
    while True:
        console.print("\n[bold green]🔥 Memulai proses trading...[/bold green]")
        await run_all(private_keys)
        console.print("\n[bold yellow]⏳ Semua proses selesai. Menunggu 1 jam sebelum menjalankan ulang...[/bold yellow]")
        await countdown(3600)  # Countdown 1 jam sebelum restart

asyncio.run(main())

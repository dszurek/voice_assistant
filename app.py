import os.path
import sys
import time
from rich.console import Console

# Add the parent directory (ecocar) to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the WakewordService from the wake_word_service folder
from wakeword_service.wws import WakeWordService
# Initialize the rich console
console = Console()

def on_listening():
    console.print("[cyan]Listening...[/cyan]")

def main():
    # Initialize the wake word service
    wakeword_service = WakeWordService(on_listening_callback=on_listening)
    
    # Wait for the user to press Enter to start the wake word service
    input("Press Enter to start the wake word service...\n")
    on_listening()
    wakeword_service.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        console.print("[red]WakewordService stopped.[/red]")
        wakeword_service.stop()

if __name__ == "__main__":
    main()
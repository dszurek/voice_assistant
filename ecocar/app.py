import os.path
import sys
import time
import logging
from rich.console import Console

# Add the parent directory (ecocar) to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the WakewordService from the wake_word_service folder
from ecocar.wakeword_service.wws import WakeWordService
# Initialize the rich console
console = Console()

def main():
    # Initialize the wake word service
    wakeword_service = WakeWordService()
    
    # Wait for the user to press Enter to start the wake word service
    input("Press Enter to start the wake word service...\n")
    console.print("[cyan]Listening for wake word...[/cyan]")
    wakeword_service.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        console.print("[red]WakewordService stopped.[/red]")
        wakeword_service.stop()

if __name__ == "__main__":
    main()
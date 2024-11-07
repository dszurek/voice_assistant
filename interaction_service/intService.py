import logging
from rich.console import Console
import re


class InteractionService:
    def __init__(self):
        self.headlights_on = False
        self.cruise_control_on = False
        self.music_request = {"name": "None", "author": "None"}
        self.destination = "None"
        self.console = Console()

    #checks whether the user's request requires the interaction service
    def is_request(self, request: str) -> bool:
        return any(
            keyword in request.lower()
            for keyword in [
                "play",
                "set navigation",
                "set destination",
                "turn on",
                "turn off"
            ]
        )

    # handles user's request
    def handle_request(self, request: str):
        if "play" in request.lower():
            return self.play_music(request)
        
        elif "set navigation" in request.lower() or "set destination" in request.lower():
            return self.set_navigation(request)
        
        elif "headlights" in request.lower():
            return self.set_headlights(request)
        
        elif "cruise control" in request.lower():
            return self.set_cruise_control(request)
        
        else:
            return "Sorry, I didn't understand that request."
        
    def set_headlights(self, request: str):
        if "turn on" in request.lower():
            self.headlights_on = True
            return "Turning on headlights"
        elif "turn off" in request.lower():
            self.headlights_on = False
            return "Turning off headlights"
        else:
            return "Sorry, I didn't understand that request."        

    def set_cruise_control(self, request: str):
        if "turn on" in request.lower():
            self.cruise_control_on = True
            return "Turning on cruise control"
        elif "turn off" in request.lower():
            self.cruise_control_on = False
            return "Turning off cruise control"
        else:
            return "Sorry, I didn't understand that request."

    def play_music(self, request: str):
        # Extract the song name and artist from the request
        match = re.search(r"play (.+?) by (.+)", request.lower())
        if match:
            song_name = match.group(1).strip()
            author = match.group(2).strip()
        else:
            song_name = request.lower().replace("play", "").strip()
            author = "Unknown"

        self.music_request = {"name": song_name, "author": author}

        # Here: personal solution (API's, custom functions, etc.)

        logging.info(f"Playing song: {song_name} by {author}")
        return f"Playing {song_name}"

    def set_navigation(self, request: str):
        # Extract the destination from the request
        destination = request.lower().replace("set navigation to", "").strip()
        self.destination = destination

        # Here: personal solution (API's, custom functions, etc.)

        logging.info(f"Setting navigation to: {destination}")
        return f"Setting navigation to {destination}"
    
    def varState(self):
        self.console.print(f"""Headlights: {self.headlights_on}
Cruise Control: {self.cruise_control_on}
Music: name: {self.music_request['name']} author: {self.music_request['author']}
Destination: {self.destination}""")


if __name__ == "__main__":
    interaction_service = InteractionService()
    sample_request = "Play dream by Fleetwood Mac"
    response = interaction_service.handle_request(sample_request)
    print(response)

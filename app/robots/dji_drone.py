class DJIDrone:
    """
    A DJI enterprise level drone that can fly to certain coordinates.
    """
    
    def fly_to(self, x: float, y: float, z: float) -> None:
        print(f"[ACTION] DJI Drone flying to coordinates x:{x}, y:{y}, z:{z}...")
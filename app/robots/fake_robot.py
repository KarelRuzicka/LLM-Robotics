from pydantic_ai import ModelRetry


class FakeRobot:
    """
    A fake robot for testing.
    """
    
    def crouch(self) -> None:
        print("[ACTION] Fake robot crouching...")

    def stand(self) -> None:
        print("[ACTION] Fake robot standing...")
        
    def wave_right_arm(self) -> None:
        print("[ACTION] Fake robot waving right arm...")
    
    def wave_left_arm(self) -> None:
        print("[ACTION] Fake robot fails to wave its arm.")
        raise ModelRetry("Arm waving mechanism is currently malfunctioning.")
    
    def step_right(self, duration_sec: float) -> None:
        print(f"[ACTION] Fake robot stepping right for {duration_sec} seconds...")
from pydantic_ai import BinaryContent, ModelRetry
import requests


class TestRobot:
    """
    A robot with basic functionalities.
    """
    
    def crouch(self) -> None:
        print("[ACTION] Test robot crouching...")

    def stand(self) -> None:
        print("[ACTION] Test robot standing...")
        
    def wave_right_arm(self) -> None:
        print("[ACTION] Test robot waving right arm...")
    
    def wave_left_arm(self) -> None:
        print("[ACTION] Test robot fails to wave its arm.")
        raise ModelRetry("Arm waving mechanism is currently malfunctioning.")
    
    def step_forward(self, steps: int) -> None:
        print(f"[ACTION] Test robot stepping forward for {steps} steps...")
    
    def step_backward(self, steps: int) -> None:
        print(f"[ACTION] Test robot stepping backward for {steps} steps...")
    
    def turn_left(self, degrees: float) -> None:
        print(f"[ACTION] Test robot turning left by {degrees} degrees...")
    
    def turn_right(self, degrees: float) -> None:
        print(f"[ACTION] Test robot turning right by {degrees} degrees...")
        
    def front_camera_snapshot(self) -> BinaryContent:
        print("[ACTION] Test robot taking front camera snapshot...")
        
        image_url = "https://room108.com/wp-content/uploads/2024/05/Set-18-2-1024x683.jpg"
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error if the download fails
        image_bytes = response.content
    
        return BinaryContent(data=image_bytes, media_type='image/jpeg')

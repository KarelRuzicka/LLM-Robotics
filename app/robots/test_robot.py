from pydantic_ai import BinaryContent, ModelRetry, FunctionToolset
import requests


toolset = FunctionToolset()

toolset.metadata = {}
toolset.metadata["robot_description"] = "A robot called TestBot with basic functionalities."


@toolset.tool   
def crouch() -> None:
    """Crouch down to a lower height."""
    print("[ACTION] Test robot crouching...")

@toolset.tool
def stand() -> None:
    """Stand up to default height."""
    print("[ACTION] Test robot standing...")
    
@toolset.tool
def wave_right_arm() -> None:
    """Wave the right arm."""
    print("[ACTION] Test robot waving right arm...")

@toolset.tool
def wave_left_arm() -> None:
    """Wave the left arm."""
    print("[ACTION] Test robot fails to wave its arm.")
    raise ModelRetry("Arm waving mechanism is currently malfunctioning.")

@toolset.tool
def step_forward(steps: int) -> None:
    """Take a number of steps forward."""
    print(f"[ACTION] Test robot stepping forward for {steps} steps...")

@toolset.tool
def step_backward(steps: int) -> None:
    """Take a number of steps backward."""
    print(f"[ACTION] Test robot stepping backward for {steps} steps...")

@toolset.tool
def turn_left(degrees: float) -> None:
    """Turn the robot to the left by a certain number of degrees."""
    print(f"[ACTION] Test robot turning left by {degrees} degrees...")

@toolset.tool
def turn_right(degrees: float) -> None:
    """Turn the robot to the right by a certain number of degrees."""
    print(f"[ACTION] Test robot turning right by {degrees} degrees...")
    
@toolset.tool
def front_camera_snapshot() -> BinaryContent:
    """Take a snapshot using the front camera."""
    
    print("[ACTION] Test robot taking front camera snapshot...")
    
    image_url = "https://room108.com/wp-content/uploads/2024/05/Set-18-2-1024x683.jpg"
    response = requests.get(image_url)
    response.raise_for_status()  # Raise an error if the download fails
    image_bytes = response.content

    return BinaryContent(data=image_bytes, media_type='image/jpeg')

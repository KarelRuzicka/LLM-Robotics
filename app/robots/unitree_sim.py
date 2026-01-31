import time
from typing import Optional

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.idl.std_msgs.msg.dds_ import String_


class UnitreeSimRobot:
    """
    Simulated Unitree G1 robot. Supports basic movement commands.
    """

    def __init__(
        self,
        domain_id: int = 1,
        topic: str = "rt/run_command/cmd",
        default_height: float = 0.8,
        rate_hz: float = 100.0,
    ) -> None:
        # Initialize DDS factory and publisher
        ChannelFactoryInitialize(domain_id)
        self._publisher = ChannelPublisher(topic, String_)
        self._publisher.Init()

        self._default_height = float(default_height)
        self._period = 1.0 / rate_hz if rate_hz > 0 else 0.01

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _send_command(
        self,
        x_vel: float = 0.0,
        y_vel: float = 0.0,
        yaw_vel: float = 0.0,
        height: Optional[float] = None,
    ) -> None:
        if height is None:
            height = self._default_height

        commands_list = [
            float(x_vel),
            -float(y_vel),
            -float(yaw_vel),
            float(height),
        ]
        msg = String_(data=str(commands_list))
        self._publisher.Write(msg)

    def _move_for_duration(
        self,
        duration_sec: float,
        x_vel: float = 0.0,
        y_vel: float = 0.0,
        yaw_vel: float = 0.0,
        height: Optional[float] = None,
    ) -> None:
        """Send a constant velocity command for a given duration, then stop."""
        end_time = time.time() + float(duration_sec)
        while time.time() < end_time:
            self._send_command(x_vel=x_vel, y_vel=y_vel, yaw_vel=yaw_vel, height=height)
            time.sleep(self._period)

        # Send a final stop command (zero velocities, keep height)
        self.stop(height=height)

    # ------------------------------------------------------------------
    # Public high-level commands
    # ------------------------------------------------------------------

    def stop(self, height: Optional[float] = None) -> None:
        """Send a zero-velocity command (robot stops moving)."""
        print(f"UnitreeSimRobot.stop(height={height})")
        self._send_command(0.0, 0.0, 0.0, height)

    def go_forward(self, duration_sec: float, speed: float = 1, height: Optional[float] = None) -> None:
        """Move forward at constant speed for ``duration_sec`` seconds."""
        print(f"UnitreeSimRobot.go_forward(duration_sec={duration_sec}, speed={speed}, height={height})")
        self._move_for_duration(duration_sec, x_vel=abs(speed), y_vel=0.0, yaw_vel=0.0, height=height)

    def go_backward(self, duration_sec: float, speed: float = 1, height: Optional[float] = None) -> None:
        """Move backward at constant speed for ``duration_sec`` seconds."""
        print(f"UnitreeSimRobot.go_backward(duration_sec={duration_sec}, speed={speed}, height={height})")
        self._move_for_duration(duration_sec, x_vel=-abs(speed), y_vel=0.0, yaw_vel=0.0, height=height)

    def strafe_left(self, duration_sec: float, speed: float = 1, height: Optional[float] = None) -> None:
        """Strafe left (lateral move) for ``duration_sec`` seconds."""
        # In keyboard controller, positive internal y_vel corresponds to left.
        print(f"UnitreeSimRobot.strafe_left(duration_sec={duration_sec}, speed={speed}, height={height})")
        self._move_for_duration(duration_sec, x_vel=0.0, y_vel=-abs(speed), yaw_vel=0.0, height=height)

    def strafe_right(self, duration_sec: float, speed: float = 1, height: Optional[float] = None) -> None:
        """Strafe right (lateral move) for ``duration_sec`` seconds."""
        print(f"UnitreeSimRobot.strafe_right(duration_sec={duration_sec}, speed={speed}, height={height})")
        self._move_for_duration(duration_sec, x_vel=0.0, y_vel=abs(speed), yaw_vel=0.0, height=height)

    def rotate_left(self, duration_sec: float, yaw_speed: float = 1.5, height: Optional[float] = None) -> None:
        """Rotate left in place for ``duration_sec`` seconds."""
        # In keyboard controller, left rotation decreased yaw_vel (negative value)
        print(f"UnitreeSimRobot.rotate_left(duration_sec={duration_sec}, yaw_speed={yaw_speed}, height={height})")
        self._move_for_duration(duration_sec, x_vel=0.0, y_vel=0.0, yaw_vel=-abs(yaw_speed), height=height)

    def rotate_right(self, duration_sec: float, yaw_speed: float = 1.5, height: Optional[float] = None) -> None:
        """Rotate right in place for ``duration_sec`` seconds."""
        print(f"UnitreeSimRobot.rotate_right(duration_sec={duration_sec}, yaw_speed={yaw_speed}, height={height})")
        self._move_for_duration(duration_sec, x_vel=0.0, y_vel=0.0, yaw_vel=abs(yaw_speed), height=height)

    def crouch(self, duration_sec: float, height_offset: float = -0.6) -> None:
        """Set a lower height (crouch). Optionally hold for ``duration_sec`` then stop.

        ``height_offset`` is an offset from the default height (negative to crouch).
        """
        target_height = self._default_height + float(height_offset)
        print(
            f"UnitreeSimRobot.crouch(duration_sec={duration_sec}, height_offset={height_offset}, target_height={target_height})"
        )
        self._move_for_duration(duration_sec, x_vel=0.0, y_vel=0.0, yaw_vel=0.0, height=target_height)

    def stand(self) -> None:
        """Return to default standing height and zero velocity."""
        print(f"UnitreeSimRobot.stand(height={self._default_height})")
        self.stop(height=self._default_height)
        
        
if __name__ == "__main__":
    # Simple test of the RobotController
    controller = UnitreeSimRobot()

    print("Standing for 2 seconds...")
    controller.stand()
    time.sleep(2.0)

    print("Moving forward for 3 seconds...")
    controller.go_backward(duration_sec=3.0, speed=1.0,)

    print("Rotating right for 2 seconds...")
    controller.rotate_right(duration_sec=2.0, yaw_speed=0.6)

    print("Crouching for 10 seconds...")
    controller.crouch(height_offset=-0.5, duration_sec=10.0)
    
    time.sleep(10.0)

    print("Standing back up...")
    controller.stand()

    print("Test complete.")

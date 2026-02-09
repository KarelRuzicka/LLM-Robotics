import math
import threading
import time
from typing import Literal, Optional, Tuple
import logging
import logging_mp

import cv2
from pydantic_ai import BinaryContent, FunctionToolset, ModelRetry
from teleimager.image_client import ImageClient

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.std_msgs.msg.dds_ import String_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_


def _quat_xyzw_to_yaw_rad(x: float, y: float, z: float, w: float) -> float:
    """Convert quaternion (x, y, z, w) to yaw (radians)."""
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


def _wrap_to_pi(angle_rad: float) -> float:
    """Wrap angle to [-pi, pi]."""
    return (angle_rad + math.pi) % (2.0 * math.pi) - math.pi


############################################################
# Robot Controller
############################################################

class RobotController:

    def __init__(
        self,
        domain_id: int = 1,
        topic: str = "rt/run_command/cmd",
        lowstate_topic: str = "rt/lowstate",
        default_height: float = 0.8,
        rate_hz: float = 100.0,
    ) -> None:
        # HighState DDS publisher for movement commands
        ChannelFactoryInitialize(domain_id)
        self._publisher = ChannelPublisher(topic, String_)
        self._publisher.Init()

        # LowState DDS subscriber for IMU yaw feedback
        self._yaw_lock = threading.Lock()
        self._latest_yaw_rad: Optional[float] = None
        self._latest_lowstate_ts: float = 0.0

        self._lowstate_sub = ChannelSubscriber(lowstate_topic, LowState_)
        self._lowstate_sub.Init(self._on_lowstate, 32)

        self._default_height = float(default_height)
        self.tolerance_deg = 2.0
        
        self._period = 1.0 / rate_hz if rate_hz > 0 else 0.01

    def _on_lowstate(self, msg: LowState_) -> None:
        """DDS callback: cache latest yaw from IMU quaternion."""
        try:
            q = msg.imu_state.quaternion
            # unitree_sim_isaaclab/dds/g1_robot_dds.py publishes quaternion as [x, y, z, w]
            yaw = _quat_xyzw_to_yaw_rad(float(q[0]), float(q[1]), float(q[2]), float(q[3]))
            with self._yaw_lock:
                self._latest_yaw_rad = yaw
                self._latest_lowstate_ts = time.time()
        except Exception:
            return

    # ------------------------------------------------------------------

    def send_command(
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

    def move_for_duration(
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
            self.send_command(x_vel=x_vel, y_vel=y_vel, yaw_vel=yaw_vel, height=height)
            time.sleep(self._period)

        # Send a final stop command (zero velocities, keep height)
        self.stop(height=height)
        
    def stop(self, height: Optional[float] = None) -> None:
        """Send a zero-velocity command"""

        self.send_command(0.0, 0.0, 0.0, height)
        
        
    def get_yaw_rad(self) -> Optional[float]:
        """Get latest yaw (radians) from rt/lowstate, or None if not available yet."""
        with self._yaw_lock:
            return self._latest_yaw_rad

    def get_yaw_deg(self) -> Optional[float]:
        """Get latest yaw (degrees) from rt/lowstate, or None if not available yet."""
        yaw = self.get_yaw_rad()
        return None if yaw is None else math.degrees(yaw)
    
    
    def rotate(
        self,
        degrees: float,
        yaw_speed: float = 1.5,
        height: Optional[float] = None,
    ) -> None:
        """Rotate in place by a relative angle in degrees in range <-180, +180> where positive values correspond to counter-clockwise (left) rotation."""
        start = self.get_yaw_rad()
        if start is None:
            raise RuntimeError("Yaw not available yet.")

        # 20 second per 90 degrees of 1.5 speed
        timeout_s = 20 * (abs(degrees) / 90.0) * (1.5 / abs(yaw_speed))
        

        # Sign convention: positive degrees should rotate in the same direction
        # you expect when giving a positive yaw_speed to rotate_right().
        target = _wrap_to_pi(start + math.radians(float(degrees)))
        tol = math.radians(float(self.tolerance_deg))

        # Choose a fixed-direction yaw rate based on sign of requested degrees.
        cmd_rate = -abs(float(yaw_speed)) if degrees > 0 else abs(float(yaw_speed))

        t0 = time.time()
        while (time.time() - t0) < float(timeout_s):
            yaw = self.get_yaw_rad()
            if yaw is None:
                break
            err = _wrap_to_pi(target - yaw)
            if abs(err) <= tol:
                self.stop(height=height)
                return
            self.send_command(x_vel=0.0, y_vel=0.0, yaw_vel=cmd_rate, height=height)
            time.sleep(self._period)

        self.stop(height=height)
        raise RuntimeError("rotate_by_degrees() timed out before reaching target.")


############################################################
# TeleImager
############################################################

class TeleImagerSnapshotClient:
    """Small helper around TeleImager's `ImageClient` to fetch frames and save snapshots.

    This is a class-based version of `teleimager_snapshot.py` so it can be used
    from inside the Unitree simulator robot wrapper.
    """

    _CAMERA_TO_METHOD = {
        "head": "get_head_frame",
        "left": "get_left_wrist_frame",
        "right": "get_right_wrist_frame",
    }

    def __init__(self, host: str = "127.0.0.1") -> None:
        
        logger = logging.getLogger("teleimager.image_client")
        logger.setLevel(logging.WARNING)
        
        self._host = host
        self._client = ImageClient(host=host)
        
 

    def close(self) -> None:
        self._client.close()

    def get_frame(self, camera: str = "head") -> Tuple[Optional["cv2.typing.MatLike"], float]:
        """Return the latest frame (or None) and the receive FPS estimate."""
        if camera not in self._CAMERA_TO_METHOD:
            raise ValueError(f"Unknown camera '{camera}'. Expected one of {sorted(self._CAMERA_TO_METHOD)}")
        method = getattr(self._client, self._CAMERA_TO_METHOD[camera])
        img, fps = method()
        return img, float(fps)



############################################################
# Instances
############################################################

robot_controller = RobotController()
teleimager_client = TeleImagerSnapshotClient(host="127.0.0.1")



############################################################
# Tools
############################################################

toolset = FunctionToolset()
toolset.metadata = {}
toolset.metadata["robot_description"] = "Unitree G1 robot. Supports basic movement commands."

        
   
   
   
def walk(direction: Literal["forward", "backward", "left", "right"], duration_sec: float) -> None:
    """Walk the robot in the specified direction for a given duration and speed."""
    
    speed = 1
    print(f"[UnitreeRobot] Walking {direction} for {duration_sec} seconds at speed {speed}")
    
    try:
        match direction:
            case "forward":
                robot_controller.move_for_duration(duration_sec, x_vel=abs(speed), y_vel=0.0, yaw_vel=0.0)
            case "backward":
                robot_controller.move_for_duration(duration_sec, x_vel=-abs(speed), y_vel=0.0, yaw_vel=0.0)
            case "left":
                robot_controller.move_for_duration(duration_sec, x_vel=0.0, y_vel=-abs(speed), yaw_vel=0.0)
            case "right":
                robot_controller.move_for_duration(duration_sec, x_vel=0.0, y_vel=abs(speed), yaw_vel=0.0)
    except Exception as e:
        print(f"[UnitreeRobot] Error while walking: {e}")
        raise ModelRetry(f"Error while walking: {e}")
        
        
# def crouch(self, duration_sec: float, height_offset: float = -0.6) -> None:
#     """Set a lower height (crouch). Optionally hold for ``duration_sec`` then stop.

#     ``height_offset`` is an offset from the default height (negative to crouch).
#     """
#     target_height = self._default_height + float(height_offset)
#     print(
#         f"UnitreeSimRobot.crouch(duration_sec={duration_sec}, height_offset={height_offset}, target_height={target_height})"
#     )
#     self.move_for_duration(duration_sec, x_vel=0.0, y_vel=0.0, yaw_vel=0.0, height=target_height)

# def stand(self) -> None:
#     """Return to default standing height and zero velocity."""
#     print(f"UnitreeSimRobot.stand(height={self._default_height})")
#     self.stop(height=self._default_height)
    

def rotate(angle: float) -> None:
    """Rotate the robot in place by a relative angle in degrees in range <-180, +180> where positive values correspond to counter-clockwise (left) rotation."""
    
    speed = 1.5
    print(f"[UnitreeRobot] Rotating {angle} degrees at speed {speed}")
    
    try:
        robot_controller.rotate(angle, speed)
    except Exception as e:
        print(f"[UnitreeRobot] Error while rotating: {e}")
        raise ModelRetry(f"Error while rotating: {e}")
        

        
def get_rotation() -> float:
    """Get the current absolute rotation of the robot in degrees."""
    rotation = robot_controller.get_yaw_deg()
    
    if rotation is None:
        print(f"[UnitreeRobot] Yaw not available yet.")
        raise ModelRetry("Yaw not available yet.")
        
        
    print(f"[UnitreeRobot] Current rotation: {rotation} degrees")
    return rotation
        
        
def get_camera_snapshot() -> BinaryContent:
    """Get a snapshot from the head camera."""
    try:
        deadline = time.monotonic() + 5.0
        last_fps = 0.0
        while time.monotonic() < deadline:
            img, fps = teleimager_client.get_frame(camera="head")
            last_fps = fps
            if img is not None:
                ok, buf = cv2.imencode(".png", img)
                if not ok:
                    raise RuntimeError("cv2.imencode('.png', img) failed")
                return BinaryContent(data=buf.tobytes(), media_type="image/png")
            time.sleep(0.02)

        raise TimeoutError(
            f"Timed out waiting for head frame after 5.0s (last recv_fps≈{last_fps:.2f}). "
            "Is the simulator running and the teleimager server enabled?"
        )
    except Exception as e:
        print(f"[UnitreeRobot] Error while getting camera snapshot: {e}")
        raise ModelRetry(f"Error while getting camera snapshot: {e}")
        
        
        
toolset.add_function(walk)
toolset.add_function(rotate)
toolset.add_function(get_rotation)
toolset.add_function(get_camera_snapshot)
        
        
        
        
        
############################################################
# Demo
############################################################

if __name__ == "__main__":

    time.sleep(2)
    
    walk("forward", 2)
    
    time.sleep(2)
    
    print(f"Rotation: {get_rotation()}")
    rotate(90)
    print(f"Rotation: {get_rotation()}")
    
    content = get_camera_snapshot()

    out_path = f"camera_snapshot.png"

    with open(out_path, "wb") as f:
        f.write(content.data)
    

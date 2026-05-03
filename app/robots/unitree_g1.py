import math
import threading
import time
from typing import Literal, Optional, Tuple

from pydantic_ai import FunctionToolset, ModelRetry
from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

NETWORK_INTERFACE = None

ChannelFactoryInitialize(0, NETWORK_INTERFACE)

sport_client: LocoClient = LocoClient()
sport_client.SetTimeout(10.0)
sport_client.Init()


_imu_lock = threading.Lock()
_latest_yaw_rad: Optional[float] = None
_latest_rpy_rad: Optional[Tuple[float, float, float]] = None
_latest_lowstate_ts: float = 0.0


def _wrap_to_180(angle_deg: float) -> float:
    return (angle_deg + 180.0) % 360.0 - 180.0


def _on_lowstate(msg: LowState_) -> None:
    global _latest_yaw_rad, _latest_rpy_rad, _latest_lowstate_ts
    try:
        rpy = msg.imu_state.rpy
        r, p, y = float(rpy[0]), float(rpy[1]), float(rpy[2])
    except Exception:
        return

    with _imu_lock:
        _latest_rpy_rad = (r, p, y)
        _latest_yaw_rad = y
        _latest_lowstate_ts = time.time()


_lowstate_sub = ChannelSubscriber("rt/lowstate", LowState_)
_lowstate_sub.Init(_on_lowstate, 32)


def get_yaw_deg() -> float:
    with _imu_lock:
        yaw = _latest_yaw_rad

    if yaw is None:
        raise Exception("IMU yaw not available yet.")
    return math.degrees(yaw)



def get_rpy_deg() -> Tuple[float, float, float]:
    with _imu_lock:
        rpy = _latest_rpy_rad

    if rpy is None:
        raise Exception("IMU RPY not available yet.")

    return (math.degrees(rpy[0]), math.degrees(rpy[1]), math.degrees(rpy[2]))

def rotate_to(target_deg: float, yaw_speed: float = 0.8, tolerance_deg: float = 1.0, timeout_sec: float = 10.0) -> None:
    start_time = time.time()

    c = sport_client
    while True:
        if time.time() - start_time > timeout_sec:
            c.StopMove()
            raise Exception("rotate_to timed out")

        current = get_yaw_deg()
        error = _wrap_to_180(target_deg - current)
        if abs(error) <= tolerance_deg:
            break

        vyaw = yaw_speed if error > 0.0 else -yaw_speed
        c.Move(0.0, 0.0, vyaw, True)
        time.sleep(0.02)

    c.StopMove()
    time.sleep(0.2)



############################################################
# Tools
############################################################

toolset = FunctionToolset()
toolset.metadata = {}
toolset.metadata["robot_description"] = "Unitree G1 robot. Uses simple LocoClient commands from the G1 example."



def walk(direction: Literal["forward", "backward", "left", "right"], duration_sec: float) -> None:
    """
    Walk the robot in the specified direction for a given duration and speed.
    """
    
    print(f"[UnitreeRobot] Walking {direction} for {duration_sec} seconds")
    if duration_sec <= 0:
        raise ModelRetry("duration_sec must be > 0")

    speed = 0.3  # same scale as the example
    vx, vy = 0.0, 0.0

    if direction == "forward":
        vx = speed
    elif direction == "backward":
        vx = -speed
    elif direction == "left":
        vy = speed
    elif direction == "right":
        vy = -speed

    try:
        c = sport_client
        c.Move(vx, vy, 0.0, True)  # continuous move
        time.sleep(duration_sec)
        c.StopMove()
        print("Finished walking")
    except Exception as e:
        try:
            sport_client.StopMove()
        except Exception:
            pass
        print(f"[UnitreeRobot] Error while walking: {e}")
        raise ModelRetry(f"Error while walking: {e}")




def rotate(delta_deg: float) -> None:
    """
    Rotate in place by a relative angle in degrees in range <-180, +180> where positive values correspond to counter-clockwise (left) rotation.
    """
    
    if delta_deg < -180.0 or delta_deg > 180.0:
        raise ModelRetry("delta_deg must be in range [-180, 180]")
    
    print(f"[UnitreeRobot] Rotating {delta_deg} degrees")

    try:
        current = get_yaw_deg()
        target = _wrap_to_180(current + delta_deg)
        rotate_to(target)
    
    except Exception as e:
        try:
            sport_client.StopMove()
        except Exception:
            pass
        print(f"[UnitreeRobot] Error while rotating: {e}")
        raise ModelRetry(f"Error while rotating to target: {e}")
    

def get_rotation() -> float:
    """
    Get the current yaw rotation of the robot in degrees in range [-180, 180].
    """
    try:
        rotation = get_yaw_deg()
        print(f"[UnitreeRobot] Current rotation: {rotation} degrees")
        return rotation
    
    except Exception as e:
        print(f"[UnitreeRobot] Error while getting rotation: {e}")
        raise ModelRetry(f"Error while getting rotation: {e}")


def damp() -> None:
    try:
        print("[UnitreeRobot] Damping")
        sport_client.Damp()
    except Exception as e:
        print(f"[UnitreeRobot] Error while damping: {e}")
        raise ModelRetry(f"Error in damp: {e}")


# def squat_to_stand() -> None:
#     try:
#         c = _client()
#         c.Damp()
#         time.sleep(0.5)
#         c.Squat2StandUp()
#     except Exception as e:
#         raise ModelRetry(f"Error in squat_to_stand: {e}")


# def stand_to_squat() -> None:
#     try:
#         _client().StandUp2Squat()
#     except Exception as e:
#         raise ModelRetry(f"Error in stand_to_squat: {e}")


# def low_stand() -> None:
#     try:
#         _client().LowStand()
#     except Exception as e:
#         raise ModelRetry(f"Error in low_stand: {e}")


# def high_stand() -> None:
#     try:
#         _client().HighStand()
#     except Exception as e:
#         raise ModelRetry(f"Error in high_stand: {e}")


# def zero_torque() -> None:
#     try:
#         _client().ZeroTorque()
#     except Exception as e:
#         raise ModelRetry(f"Error in zero_torque: {e}")


# def wave_hand(turn_around: bool = False) -> None:
#     try:
#         _client().WaveHand(turn_around)
#     except Exception as e:
#         raise ModelRetry(f"Error in wave_hand: {e}")


# def shake_hand() -> None:
#     try:
#         c = _client()
#         c.ShakeHand()
#         time.sleep(3.0)
#         c.ShakeHand()
#     except Exception as e:
#         raise ModelRetry(f"Error in shake_hand: {e}")


# def lie_to_stand() -> None:
#     try:
#         c = _client()
#         c.Damp()
#         time.sleep(0.5)
#         c.Lie2StandUp()
#     except Exception as e:
#         raise ModelRetry(f"Error in lie_to_stand: {e}")



toolset.add_function(walk)
toolset.add_function(rotate)
toolset.add_function(get_rotation)
toolset.add_function(damp)
# toolset.add_function(squat_to_stand)
# toolset.add_function(stand_to_squat)
# toolset.add_function(low_stand)
# toolset.add_function(high_stand)
# toolset.add_function(zero_torque)
# toolset.add_function(wave_hand)
# toolset.add_function(shake_hand)
# toolset.add_function(lie_to_stand)



############################################################
# Demo
############################################################

if __name__ == "__main__":
    time.sleep(5.0)  # wait for subscribers to connect
    walk("forward", 5.0)
    time.sleep(1)
    rotate(90)
    walk("left", 3.0)
    
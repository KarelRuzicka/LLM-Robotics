import time
import util
from util import mock_settings
import path


def rotate_and_check(robot_sim, angle, tolerance):
    degrees_before = robot_sim.get_rotation()
    robot_sim.rotate(angle=angle)
    degrees_after = robot_sim.get_rotation()
    degrees_rotated = robot_sim.wrap_to_180(degrees_after - degrees_before)
    return abs(degrees_rotated)


def test_advanced_rotation(monkeypatch, mock_settings):
    
    monkeypatch.setattr("config.settings", mock_settings)
    
    import robots.unitree_sim as robot_sim # type: ignore
    
    time.sleep(1)  # Allow time for initialization
    
    tolerance = 5 # degrees
    
    result = rotate_and_check(robot_sim, 90.0, tolerance)
    assert result >= 90 - tolerance and result <= 90 + tolerance, f"Expected ~90° with tolerance {tolerance}°, got {result}°"
    
    result = rotate_and_check(robot_sim, -180.0, tolerance)
    assert result >= 180 - tolerance and result <= 180 + tolerance, f"Expected ~180° with tolerance {tolerance}°, got {result}°"
    
    result = rotate_and_check(robot_sim, 45, tolerance)
    assert result >= 45 - tolerance and result <= 45 + tolerance, f"Expected ~45° with tolerance {tolerance}°, got {result}°"
    
    result = rotate_and_check(robot_sim, -60, tolerance)
    assert result >= 60 - tolerance and result <= 60 + tolerance, f"Expected ~60° with tolerance {tolerance}°, got {result}°"

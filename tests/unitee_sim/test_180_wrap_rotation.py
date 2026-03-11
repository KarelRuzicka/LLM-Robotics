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
    
    original_rotation = robot_sim.get_rotation()
    
    result = rotate_and_check(robot_sim, 90.0, tolerance)
    assert result >= 90 - tolerance and result <= 90 + tolerance, f"Expected ~90° with tolerance {tolerance}°, got {result}°"
    
    result = rotate_and_check(robot_sim, 90.0, tolerance)
    assert result >= 90 - tolerance and result <= 90 + tolerance, f"Expected ~90° with tolerance {tolerance}°, got {result}°"
    
    result = rotate_and_check(robot_sim, 90.0, tolerance)
    assert result >= 90 - tolerance and result <= 90 + tolerance, f"Expected ~90° with tolerance {tolerance}°, got {result}°"
    
    result = rotate_and_check(robot_sim, 90.0, tolerance)
    assert result >= 90 - tolerance and result <= 90 + tolerance, f"Expected ~90° with tolerance {tolerance}°, got {result}°"
    

    
    total_tolerance = 20 # degrees
    last_rotation = robot_sim.get_rotation()
    assert last_rotation >= original_rotation - total_tolerance and last_rotation <= original_rotation + total_tolerance, f"Expected final rotation to be close to original rotation {original_rotation}° with tolerance {total_tolerance}°, but got {last_rotation}°"
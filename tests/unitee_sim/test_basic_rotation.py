import time
import util
from util import mock_settings
import path



def test_basic_rotation(monkeypatch, mock_settings):
    
    monkeypatch.setattr("config.settings", mock_settings)
    
    import robots.unitree_sim as robot_sim # type: ignore
    
    time.sleep(1)  # Allow time for initialization
    
    degrees_before = robot_sim.get_rotation()
    robot_sim.rotate(angle=90.0)
    degrees_after = robot_sim.get_rotation()
    degrees_rotated = robot_sim.wrap_to_180(degrees_after - degrees_before)
    
    
    tolerance = 5 # degrees
    
    assert degrees_rotated >= 90 - tolerance and degrees_rotated <= 90 + tolerance, f"Expected ~90° with tolerance {tolerance}°, got {degrees_rotated}°"

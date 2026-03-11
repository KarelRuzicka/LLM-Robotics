import time
import cv2
import numpy as np
import util
from util import mock_settings
import path


def test_teleimager(monkeypatch, mock_settings):

    monkeypatch.setattr("config.settings", mock_settings)

    import robots.unitree_sim as robot_sim  # type: ignore

    time.sleep(1)  # Allow time for initialization / first frame

    result = robot_sim.get_camera_snapshot()

    # Basic sanity checks on BinaryContent
    assert result is not None, "Expected camera snapshot, got None"
    assert isinstance(result.data, (bytes, bytearray)), "Snapshot data must be bytes-like"
    assert result.media_type == "image/png", f"Unexpected media_type: {result.media_type!r}"

    # Verify the bytes decode as a valid PNG image via OpenCV
    buf = np.frombuffer(result.data, dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)

    assert img is not None, "cv2.imdecode failed, snapshot is not a valid PNG image"
    h, w = img.shape[:2]
    assert h > 0 and w > 0, f"Decoded image has invalid dimensions: {w}x{h}"


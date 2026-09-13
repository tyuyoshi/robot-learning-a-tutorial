"""Save frames through LeRobot's actual ZMQ camera client; no robot commands."""

import argparse
from pathlib import Path

import cv2
from lerobot.cameras.zmq.camera_zmq import ZMQCamera
from lerobot.cameras.zmq.configuration_zmq import ZMQCameraConfig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    args = parser.parse_args()
    output = Path(__file__).resolve().parents[2] / "local/so101/camera-check"
    output.mkdir(parents=True, exist_ok=True)
    camera = ZMQCamera(ZMQCameraConfig(server_address=args.host, camera_name="wrist"))
    try:
        camera.connect()
        for i in range(30):
            frame = camera.read()
            if i in (9, 19, 29):
                path = output / f"windows-zmq-{i + 1}.png"
                if not cv2.imwrite(str(path), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)):
                    raise RuntimeError(f"Could not save {path}")
                print(f"保存: {path}", flush=True)
    finally:
        if camera.is_connected:
            camera.disconnect()


if __name__ == "__main__":
    main()

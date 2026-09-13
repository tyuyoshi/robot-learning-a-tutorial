# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["opencv-python-headless==4.13.0.92", "pyzmq==27.1.0"]
# ///
"""Windows camera publisher compatible with LeRobot 0.6.1 ZMQCamera."""

import argparse
import base64
import time

import cv2
import zmq


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind", required=True, help="Windows IP reachable from WSL")
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--port", type=int, default=5555)
    args = parser.parse_args()
    cap = cv2.VideoCapture(args.index, cv2.CAP_DSHOW)
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.setsockopt(zmq.SNDHWM, 1)
    publisher.setsockopt(zmq.LINGER, 0)
    try:
        if not cap.isOpened():
            raise RuntimeError("Camera could not be opened; close Windows Camera or try --index 1")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        publisher.bind(f"tcp://{args.bind}:{args.port}")
        print(f"Camera {args.index}: tcp://{args.bind}:{args.port}; Ctrl+C to stop", flush=True)
        count = 0
        last_report = time.monotonic()
        while True:
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError("Windows camera frame capture failed")
            ok, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ok:
                raise RuntimeError("JPEG encoding failed")
            publisher.send_json({"images": {"wrist": base64.b64encode(jpeg).decode("ascii")}})
            count += 1
            now = time.monotonic()
            if now - last_report >= 5:
                print(f"Publishing {frame.shape[1]}x{frame.shape[0]}, {count / (now - last_report):.1f} fps", flush=True)
                count = 0
                last_report = now
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        publisher.close()
        context.term()


if __name__ == "__main__":
    main()

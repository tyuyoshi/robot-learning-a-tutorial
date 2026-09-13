"""Capture three MJPG test frames without connecting to the robot arms."""

import argparse
from pathlib import Path

import cv2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    args = parser.parse_args()
    if args.width <= 0 or args.height <= 0:
        parser.error("width and height must be positive")
    output = Path(__file__).resolve().parents[2] / "local/so101/camera-check"
    output.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
    try:
        if not cap.isOpened():
            raise RuntimeError("カメラを開けません。接続とvideoグループを確認してください。")
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
        cap.set(cv2.CAP_PROP_FPS, 30)
        code = int(cap.get(cv2.CAP_PROP_FOURCC))
        actual_format = "".join(chr((code >> (8 * i)) & 255) for i in range(4))
        print(f"実際の形式: {actual_format}", flush=True)
        print(
            f"設定: {cap.get(cv2.CAP_PROP_FRAME_WIDTH):g} x "
            f"{cap.get(cv2.CAP_PROP_FRAME_HEIGHT):g}, "
            f"{cap.get(cv2.CAP_PROP_FPS):g} fps（実測ではありません）",
            flush=True,
        )
        if actual_format != "MJPG":
            print("注意: MJPGが適用されていません。実際の形式で取得します。", flush=True)
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if (actual_width, actual_height) != (args.width, args.height):
            raise RuntimeError("要求した解像度が適用されませんでした")
        for i in range(30):
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError(f"{i + 1}枚目の取得に失敗しました")
            if i in (9, 19, 29):
                path = output / f"mjpg-{actual_width}x{actual_height}-check-{i + 1}.png"
                if not cv2.imwrite(str(path), frame):
                    raise RuntimeError(f"画像保存に失敗しました: {path}")
                print(f"保存: {path}", flush=True)
    finally:
        cap.release()


if __name__ == "__main__":
    main()

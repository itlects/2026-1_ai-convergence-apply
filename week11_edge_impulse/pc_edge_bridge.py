"""Linux Edge Impulse .eim webcam inference -> ESP32 USB serial."""
import argparse
import time

CLASSES = {"bottle", "can", "paper"}

def decide(scores, threshold=0.75):
    if not scores:
        return "ERROR", "unknown", 0.0
    label, value = max(scores.items(), key=lambda item: item[1])
    score = float(value)
    return ("OK" if label in CLASSES and score >= threshold else "ERROR", label, score)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model")
    p.add_argument("--port")
    p.add_argument("--camera", type=int, default=0)
    p.add_argument("--threshold", type=float, default=0.75)
    p.add_argument("--demo", action="store_true")
    p.add_argument("--once", action="store_true")
    a = p.parse_args()
    if a.demo:
        for scores in [
            {"bottle": .93, "can": .04, "paper": .03},
            {"bottle": .35, "can": .40, "paper": .25},
            {"bottle": .04, "can": .90, "paper": .06},
        ]:
            print(decide(scores, a.threshold))
        return
    if not a.model or not a.port:
        p.error("--model and --port required without --demo")
    if not 0 <= a.threshold <= 1:
        p.error("--threshold must be between 0 and 1")
    import cv2
    import serial
    from edge_impulse_linux.image import ImageImpulseRunner

    camera = cv2.VideoCapture(a.camera)
    if not camera.isOpened():
        raise RuntimeError("Camera not available")
    port = serial.Serial(a.port, 115200, timeout=0.2)
    time.sleep(2.5)
    port.reset_input_buffer()
    port.write(b"READY\n")
    try:
        with ImageImpulseRunner(a.model) as runner:
            info = runner.init()
            labels = info["model_parameters"]["labels"]
            if set(labels) != CLASSES:
                raise ValueError(f"Expected labels {CLASSES}; got {labels}")
            capture = a.once
            while True:
                if port.readline().decode("utf-8", "replace").strip() == "CAPTURE":
                    capture = True
                if not capture:
                    continue
                capture = False
                port.write(b"BUSY\n")
                try:
                    ok, bgr = camera.read()
                    if not ok:
                        raise RuntimeError("Cannot read image")
                    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                    features, _ = runner.get_features_from_image(rgb)
                    result = runner.classify(features)
                    scores = result["result"].get("classification")
                    if scores is None:
                        raise ValueError("Image classification model required")
                    status, label, score = decide(scores, a.threshold)
                    print(status, label, round(score, 3), flush=True)
                    port.write((status + "\n").encode())
                except (ValueError, RuntimeError, KeyError) as error:
                    print(error, flush=True)
                    port.write(b"ERROR\n")
                if a.once:
                    break
    finally:
        port.write(b"DONE\n")
        port.flush()
        port.close()
        camera.release()

if __name__ == "__main__":
    main()

"""Play stored score rows into ESP32 over USB serial."""
import argparse
import csv
import time
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "scores.csv"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    args = parser.parse_args()
    try:
        import serial
    except ImportError as exc:
        raise SystemExit("Install pyserial: python -m pip install pyserial") from exc
    with DATA.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    with serial.Serial(args.port, 115200, timeout=0.3) as ser:
        time.sleep(2)
        for row in rows:
            ser.write(f'SCORE,{float(row["confidence"]):.3f}\n'.encode())
            time.sleep(0.3)
            while ser.in_waiting:
                print(ser.readline().decode(errors="replace").strip())


if __name__ == "__main__":
    main()

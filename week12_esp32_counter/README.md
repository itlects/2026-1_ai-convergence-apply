# Week 12 — ESP32 confidence threshold and event counter

## Hands-on workbooks
1. [Workbook 1: threshold dial and model-like confidence scores](workbook1/WORKBOOK.md)
2. [Workbook 2: analog microphone sound-event counter](workbook2/WORKBOOK.md)

## Materials
- [Offline labeled confidence CSV](data/scores.csv)
- [ESP32 WB1 wiring SVG](diagrams/wb1_wiring.svg)
- [ESP32 WB2 wiring SVG](diagrams/wb2_wiring.svg)
- [Python threshold evaluation](workbook1/evaluate.py)
- [ESP32 threshold dial sketch](workbook1/counter_dial.ino)
- [ESP32 microphone counter sketch](workbook2/sound_counter.ino)

Workbook 1 uses precomputed confidence scores, not an installed AI model; workbook 2 uses audio amplitude, not inference confidence. Refer to Workbooks for electrical safety and verification.

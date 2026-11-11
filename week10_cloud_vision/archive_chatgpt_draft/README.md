# Week10 — ESP32 DevKitC V4 and Google Cloud Vision

## Circuit
ESP32 GPIO18 -> 220 ohm -> green LED anode; LED cathode -> GND.
ESP32 GPIO19 -> 220 ohm -> red LED anode; LED cathode -> GND.
ESP32 GPIO23 -> button -> GND (INPUT_PULLUP).
Power from USB only; no direct 5V into GPIO.

## Run order
1. Build circuit; upload esp32_trigger.ino with Arduino IDE for ESP32 Dev Module. Press button; 115200 serial prints CAPTURE_REQUEST. Send DONE to reset LEDs.
2. ESP32 DevKitC V4 has no camera. Use the distinct week09 ESP32-CAM to capture JPEG files, or sample ZIP from the downloadable classroom materials.
3. Colab: upload picture, install google-cloud-vision, enable API and billing, authenticate, set project ID, and run cloud_vision.py. Do not upload credential secrets to GitHub.
4. Upload labels.csv and run split_evaluate.py in Colab: per-class 70/15/15, random seed 42. It uses DEMO predictions, not Cloud Vision outputs.
5. For actual API accuracy, predefine target classes and a mapping of Vision label output, annotate gold labels, and evaluate test set without test leakage.

## Concepts
pinMode, INPUT_PULLUP, digitalRead, digitalWrite, millis, ImageAnnotatorClient, label_detection, score, accuracy_score, confusion_matrix. Score != accuracy. Cloud Vision Label Detection is pretrained multi-label annotation; data splits here do not train it.

## Dataset
Separate ZIP with 60 synthetic three-shape labeled images is available in downloadable class bundle; these are intended for dataset partition exercises, not valid assessment of Vision's real-world object classification.

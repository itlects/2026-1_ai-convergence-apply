/*
 * Week09 / Workbook 2: AI Thinker ESP32-CAM + OV2640 + microSD.
 * Board selection: AI Thinker ESP32-CAM; SD_MMC 1-bit mode.
 * Separate camera board (not wired directly to DevKitC V4).
 * USB-TTL upload: adapter TX->U0R, RX->U0T, GND->GND,
 * regulated 5V->5V; GPIO0->GND only while flashing.
 * Remove GPIO0 jumper, reset, then view Serial at 115200.
 * Serial 'c' captures JPEG into /image_0001.jpg, etc.
 */
#include <Arduino.h>
#include "esp_camera.h"
#include "FS.h"
#include "SD_MMC.h"

#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

uint32_t imageCounter = 0;

bool initCamera() {
  camera_config_t config = {};
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;  // 320x240
  config.jpeg_quality = 12;
  config.fb_count = 1;
  config.fb_location = CAMERA_FB_IN_DRAM;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  return esp_camera_init(&config) == ESP_OK;
}

void captureToSd() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }

  char filename[32];
  snprintf(filename, sizeof(filename), "/image_%04lu.jpg",
           (unsigned long)++imageCounter);
  File file = SD_MMC.open(filename, FILE_WRITE);
  if (!file) {
    Serial.println("SD file open failed");
    esp_camera_fb_return(fb);
    return;
  }
  size_t written = file.write(fb->buf, fb->len);
  file.close();
  Serial.printf("%s, %ux%u, %u bytes, written %u\n",
                filename, (unsigned)fb->width, (unsigned)fb->height,
                (unsigned)fb->len, (unsigned)written);
  esp_camera_fb_return(fb);
}

void setup() {
  Serial.begin(115200);
  delay(1200);
  if (!initCamera()) {
    Serial.println("Camera initialization failed. Check board and camera.");
    return;
  }
  if (!SD_MMC.begin("/sdcard", true)) {
    Serial.println("SD mounting failed. Check card/FAT32.");
    return;
  }
  Serial.println("Ready. Send c + Enter to capture.");
}

void loop() {
  if (Serial.available()) {
    char ch = Serial.read();
    if (ch == 'c' || ch == 'C') {
      captureToSd();
    }
  }
}
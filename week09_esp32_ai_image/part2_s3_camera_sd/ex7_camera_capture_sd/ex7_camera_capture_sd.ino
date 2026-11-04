/*
  9주차 예제 7 — 카메라로 촬영해서 microSD에 JPEG 저장하기
  보드 : ESP32-S3-WROOM CAM 보드 (Freenove 호환, OV2640/OV3660 카메라 + microSD 슬롯)
  Arduino IDE 설정 : 예제6과 동일 (ESP32S3 Dev Module, PSRAM = OPI PSRAM 반드시!)

  카메라 핀 (보드 내부 배선, 연결할 필요 없음 — ESP32-S3-EYE와 같은 배치)
    XCLK=15  SIOD(SDA)=4  SIOC(SCL)=5  VSYNC=6  HREF=7  PCLK=13
    Y2=11 Y3=9 Y4=8 Y5=10 Y6=12 Y7=18 Y8=17 Y9=16   (PWDN, RESET 없음)
  microSD : CMD=38, CLK=39, D0=40 (1비트)

  사용법 (시리얼 모니터 115200, 줄 끝: "새 줄" 또는 "Both NL & CR")
    BOOT 버튼(GPIO0) 누르기 또는 c 입력 → 사진 1장 촬영 후 /photos/IMG_0001.jpg ... 로 저장
    1 → 해상도 QVGA 320x240 (기본)
    2 → 해상도 VGA  640x480
    3 → 해상도 96x96 (센서가 직접 96x96으로 출력)
    l → /photos 파일 목록 보기

  원리 : 센서가 빛을 픽셀 값으로 바꿈 → 카메라 칩이 JPEG로 압축 → 프레임 버퍼(PSRAM)에 저장
        → esp_camera_fb_get() 으로 버퍼를 받아 SD 파일에 그대로 기록 → esp_camera_fb_return() 으로 반납
*/
#include "esp_camera.h"
#include "FS.h"
#include "SD_MMC.h"

// ---- 카메라 핀 (ESP32-S3-WROOM CAM / ESP32S3_EYE 배치) ----
#define PWDN_GPIO_NUM  -1
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM  15
#define SIOD_GPIO_NUM   4
#define SIOC_GPIO_NUM   5
#define Y9_GPIO_NUM    16
#define Y8_GPIO_NUM    17
#define Y7_GPIO_NUM    18
#define Y6_GPIO_NUM    12
#define Y5_GPIO_NUM    10
#define Y4_GPIO_NUM     8
#define Y3_GPIO_NUM     9
#define Y2_GPIO_NUM    11
#define VSYNC_GPIO_NUM  6
#define HREF_GPIO_NUM   7
#define PCLK_GPIO_NUM  13

// ---- microSD 핀 ----
#define SD_MMC_CMD 38
#define SD_MMC_CLK 39
#define SD_MMC_D0  40

#define BOOT_BUTTON 0          // 보드의 BOOT 버튼 (누르면 LOW)

bool cameraOK = false, sdOK = false;
int  photoIndex = 0;           // 다음 파일 번호
int  lastBtn = HIGH;

bool initCamera() {
  camera_config_t config = {};
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk  = XCLK_GPIO_NUM;
  config.pin_pclk  = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href  = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn  = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;            // 카메라에 주는 클록 20MHz
  config.pixel_format = PIXFORMAT_JPEG;      // JPEG로 압축해서 받기
  config.frame_size   = FRAMESIZE_QVGA;      // 320 x 240
  config.jpeg_quality = 12;                  // 0~63, 숫자가 작을수록 고화질(파일 큼)
  config.fb_count     = 1;
  config.grab_mode    = CAMERA_GRAB_LATEST;  // 항상 가장 최신 프레임 사용

  if (psramFound()) {
    config.fb_location = CAMERA_FB_IN_PSRAM;
  } else {
    Serial.println("⚠ PSRAM 없음 → 도구 > PSRAM 을 'OPI PSRAM' 으로 바꾸고 다시 업로드하세요.");
    config.fb_location = CAMERA_FB_IN_DRAM;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("카메라 초기화 실패 (0x%x) → 카메라 리본 케이블 방향·잠금 확인 후 리셋\n", err);
    return false;
  }
  sensor_t *s = esp_camera_sensor_get();
  Serial.printf("카메라 센서 PID: 0x%02X (%s)\n", s->id.PID,
                s->id.PID == OV2640_PID ? "OV2640" : s->id.PID == OV3660_PID ? "OV3660" :
                s->id.PID == OV5640_PID ? "OV5640" : "기타");
  if (s->id.PID == OV3660_PID) { s->set_vflip(s, 1); }   // OV3660은 상하 반전 보정
  return true;
}

bool initSD() {
  SD_MMC.setPins(SD_MMC_CLK, SD_MMC_CMD, SD_MMC_D0);
  if (!SD_MMC.begin("/sdcard", true)) {
    Serial.println("SD 마운트 실패 → 예제6으로 카드 상태를 먼저 확인하세요.");
    return false;
  }
  if (!SD_MMC.exists("/photos")) SD_MMC.mkdir("/photos");
  return true;
}

// /photos 안의 IMG_xxxx.jpg 중 가장 큰 번호 다음 번호를 찾는다 (전원을 껐다 켜도 덮어쓰지 않도록)
int findNextIndex() {
  int maxNum = 0;
  File dir = SD_MMC.open("/photos");
  File f = dir.openNextFile();
  while (f) {
    String n = f.name();                       // 예: IMG_0007.jpg
    if (n.startsWith("IMG_") && n.endsWith(".jpg")) {
      int num = n.substring(4, 8).toInt();
      if (num > maxNum) maxNum = num;
    }
    f = dir.openNextFile();
  }
  return maxNum + 1;
}

void listPhotos() {
  Serial.println("[ /photos 목록 ]");
  File dir = SD_MMC.open("/photos");
  File f = dir.openNextFile();
  int count = 0;
  while (f) {
    Serial.printf("  %-14s %7u B\n", f.name(), (unsigned)f.size());
    count++;
    f = dir.openNextFile();
  }
  Serial.printf("  총 %d개\n", count);
}

void setResolution(framesize_t size, const char *name) {
  sensor_t *s = esp_camera_sensor_get();
  s->set_framesize(s, size);
  // 해상도를 바꾼 직후 프레임은 이전 크기일 수 있으므로 1장 버린다
  camera_fb_t *fb = esp_camera_fb_get();
  if (fb) esp_camera_fb_return(fb);
  Serial.printf("해상도 변경: %s\n", name);
}

void capturePhoto() {
  if (!cameraOK || !sdOK) { Serial.println("카메라 또는 SD 준비 안 됨"); return; }

  camera_fb_t *fb = esp_camera_fb_get();       // 1) 프레임 받기
  if (!fb) { Serial.println("촬영 실패"); return; }

  char path[32];
  snprintf(path, sizeof(path), "/photos/IMG_%04d.jpg", photoIndex);

  File file = SD_MMC.open(path, FILE_WRITE);   // 2) 파일 만들기
  if (!file) {
    Serial.println("파일 생성 실패");
  } else {
    size_t written = file.write(fb->buf, fb->len);   // 3) JPEG 바이트 그대로 기록
    file.close();
    Serial.printf("📷 저장: %s  |  %d x %d 픽셀  |  %u 바이트 (%.1f KB)  |  기록 %u B\n",
                  path, fb->width, fb->height, (unsigned)fb->len, fb->len / 1024.0, (unsigned)written);
    photoIndex++;
  }
  esp_camera_fb_return(fb);                    // 4) 버퍼 반납 (안 하면 다음 촬영 불가)
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println("\n예제7: 카메라 촬영 → microSD 저장");
  pinMode(BOOT_BUTTON, INPUT_PULLUP);

  cameraOK = initCamera();
  sdOK     = initSD();
  if (cameraOK && sdOK) {
    photoIndex = findNextIndex();
    // 처음 몇 장은 노출(밝기) 자동 조정 중이라 어두우므로 버린다
    for (int i = 0; i < 3; i++) { camera_fb_t *fb = esp_camera_fb_get(); if (fb) esp_camera_fb_return(fb); delay(100); }
    Serial.printf("준비 완료! 다음 파일 번호: %04d\n", photoIndex);
    Serial.println("BOOT 버튼 또는 c=촬영 | 1=QVGA 2=VGA 3=96x96 | l=목록");
  }
}

void loop() {
  // BOOT 버튼: 누르는 순간 1번만 촬영
  int btn = digitalRead(BOOT_BUTTON);
  if (lastBtn == HIGH && btn == LOW) { delay(30); if (digitalRead(BOOT_BUTTON) == LOW) capturePhoto(); }
  lastBtn = btn;

  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'c') capturePhoto();
    else if (c == '1') setResolution(FRAMESIZE_QVGA, "QVGA 320x240");
    else if (c == '2') setResolution(FRAMESIZE_VGA,  "VGA 640x480");
    else if (c == '3') setResolution(FRAMESIZE_96X96, "96x96");
    else if (c == 'l') listPhotos();
  }
  delay(10);
}

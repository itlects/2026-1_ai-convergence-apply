/*
  9주차 예제 6 — microSD 카드 확인하기 (SD_MMC 1비트 모드)
  보드 : ESP32-S3-WROOM CAM 보드 (Freenove 호환, 카메라·microSD 슬롯 내장)

  Arduino IDE 설정 (도구 메뉴)
    보드           : ESP32S3 Dev Module
    USB CDC On Boot: Disabled   (보드의 'COM'/'UART' 쪽 USB-C 포트에 연결할 때)
                     Enabled    (보드의 'USB'/'OTG' 쪽 USB-C 포트에 연결할 때)
    Flash Size     : 8MB (N8R8 보드) 또는 16MB (N16R8 보드)
    PSRAM          : OPI PSRAM
    Partition      : 8M with spiffs (3MB APP/1.5MB SPIFFS)  ※ 16MB 보드도 그대로 써도 됨
    시리얼 모니터   : 115200

  microSD 연결 : 보드에 슬롯이 이미 배선되어 있으므로 따로 연결할 선이 없다.
    CMD = GPIO38, CLK = GPIO39, D0 = GPIO40  (1비트 SDMMC 모드)
  준비 : 32GB 이하 microSD 카드를 FAT32로 포맷해서 꽂는다. (64GB 이상 exFAT은 인식 안 될 수 있음)

  동작 : 카드 종류·용량 출력 → /hello.txt 쓰기·읽기 → /photos 폴더 만들기 → 루트 파일 목록 출력
*/
#include "FS.h"
#include "SD_MMC.h"

#define SD_MMC_CMD 38
#define SD_MMC_CLK 39
#define SD_MMC_D0  40

void listDir(fs::FS &fs, const char *dirname) {
  Serial.printf("\n[목록] %s\n", dirname);
  File root = fs.open(dirname);
  if (!root || !root.isDirectory()) { Serial.println("  폴더를 열 수 없음"); return; }
  File file = root.openNextFile();
  while (file) {
    if (file.isDirectory()) Serial.printf("  <DIR>  %s\n", file.name());
    else                    Serial.printf("  %7u B  %s\n", (unsigned)file.size(), file.name());
    file = root.openNextFile();
  }
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println("\n예제6: microSD 카드 확인");

  SD_MMC.setPins(SD_MMC_CLK, SD_MMC_CMD, SD_MMC_D0);       // 핀 지정 (CLK, CMD, D0 순서)
  if (!SD_MMC.begin("/sdcard", true)) {                     // true = 1비트 모드
    Serial.println("SD 카드 마운트 실패 → 카드 삽입 방향, FAT32 포맷, 32GB 이하 여부를 확인하세요.");
    return;
  }

  uint8_t type = SD_MMC.cardType();
  const char *typeName = (type == CARD_MMC) ? "MMC" : (type == CARD_SD) ? "SDSC" : (type == CARD_SDHC) ? "SDHC" : "알 수 없음";
  Serial.printf("카드 종류: %s\n", typeName);
  Serial.printf("카드 용량: %llu MB\n", SD_MMC.cardSize() / (1024 * 1024));
  Serial.printf("사용 공간: %llu MB / 전체 %llu MB\n",
                SD_MMC.usedBytes() / (1024 * 1024), SD_MMC.totalBytes() / (1024 * 1024));

  // 1) 쓰기
  File f = SD_MMC.open("/hello.txt", FILE_WRITE);
  if (f) { f.println("Hello ESP32-S3! 9주차 SD 테스트"); f.close(); Serial.println("쓰기 완료: /hello.txt"); }

  // 2) 읽기
  f = SD_MMC.open("/hello.txt");
  if (f) {
    Serial.print("읽은 내용: ");
    while (f.available()) Serial.write(f.read());
    f.close();
  }

  // 3) 사진 저장용 폴더
  if (!SD_MMC.exists("/photos")) SD_MMC.mkdir("/photos");

  listDir(SD_MMC, "/");
  Serial.println("\n✅ SD 카드 테스트 완료 → 예제7(카메라 촬영)로 진행하세요.");
}

void loop() {}

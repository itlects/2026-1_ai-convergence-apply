/*
  9주차 예제 8 — 이미지 갤러리 웹 앱 (ESP32-S3가 직접 웹서버가 된다)
  보드 : ESP32-S3-WROOM CAM 보드 (Freenove 호환)
  Arduino IDE 설정 : 예제6·7과 동일 (ESP32S3 Dev Module, PSRAM = OPI PSRAM)

  동작
    1) ESP32-S3가 Wi-Fi 공유기(AP)가 된다.   이름: W09-CAM-xxxx   비밀번호: 12345678
       (xxxx는 보드마다 다른 4자리 → 옆 친구 보드와 헷갈리지 않도록 시리얼 모니터에서 확인)
    2) 스마트폰/노트북을 그 Wi-Fi에 연결하고 브라우저에서 http://192.168.4.1 접속
    3) [📷 촬영] 버튼 → 사진을 찍어 microSD /photos 에 저장하고 갤러리에 바로 표시
    4) 사진을 누르면 원본 크기 / 96×96(중앙 자르기) 변환 결과를 비교하고 PNG로 내려받을 수 있다.
       ※ 96×96 변환은 ESP32가 아니라 '브라우저'의 canvas가 계산한다 (Colab 워크북 3과 같은 원리)

  웹 주소(엔드포인트)
    /            갤러리 HTML 페이지
    /list        사진 목록 JSON  [{"name":"IMG_0001.jpg","size":12345}, ...]
    /photo?n=..  JPEG 파일 한 장
    /capture     촬영 후 저장, 결과 JSON
    /delete?n=.. 사진 한 장 삭제

  학교 Wi-Fi에 붙이고 싶으면 아래 STA_SSID/STA_PASS에 입력 (비워두면 AP 모드)
*/
#include "esp_camera.h"
#include "FS.h"
#include "SD_MMC.h"
#include <WiFi.h>
#include <WebServer.h>

const char *STA_SSID = "";          // 예: "MyClassWiFi"   (비워 두면 보드가 직접 AP가 됨)
const char *STA_PASS = "";
const char *AP_PASS  = "12345678";  // AP 모드 비밀번호 (8자 이상)

// ---- 카메라 핀 (ESP32S3_EYE 배치) ----
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
// ---- microSD ----
#define SD_MMC_CMD 38
#define SD_MMC_CLK 39
#define SD_MMC_D0  40
#define BOOT_BUTTON 0

WebServer server(80);
bool cameraOK = false, sdOK = false;
int photoIndex = 1;
int lastBtn = HIGH;

// ------------------------- 갤러리 HTML (브라우저에서 실행) -------------------------
const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ESP32-S3 갤러리</title>
<style>
 body{font-family:sans-serif;margin:0;background:#f4f5f7;color:#222}
 header{background:#1f4e79;color:#fff;padding:12px 16px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
 header h1{font-size:18px;margin:0;flex:1}
 button{border:0;border-radius:6px;padding:8px 14px;font-size:15px;cursor:pointer}
 .cap{background:#ffb703} .ref{background:#e0e0e0}
 #msg{padding:6px 16px;font-size:14px;min-height:20px}
 #grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;padding:0 16px 16px}
 .card{background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px #0002;cursor:pointer}
 .card img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;background:#ddd}
 .card div{font-size:12px;padding:4px 6px}
 #view{position:fixed;inset:0;background:#000c;display:none;align-items:center;justify-content:center}
 #box{background:#fff;border-radius:10px;padding:14px;max-width:95vw;max-height:92vh;overflow:auto}
 #box img{max-width:100%}
 canvas{image-rendering:pixelated;width:192px;height:192px;border:1px solid #999}
 .row{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start}
 table{border-collapse:collapse;font-size:13px;margin-top:8px} td{border:1px solid #ccc;padding:3px 8px}
</style></head><body>
<header><h1>📷 ESP32-S3 이미지 갤러리</h1>
<button class="cap" onclick="capture()">📷 촬영</button>
<button class="ref" onclick="load()">↻ 새로고침</button></header>
<div id="msg"></div><div id="grid"></div>
<div id="view" onclick="if(event.target.id=='view')this.style.display='none'"><div id="box">
 <b id="vname"></b>
 <div class="row"><div><div>원본</div><img id="vimg"></div>
 <div><div>96×96 (중앙 자르기, 2배 확대 표시)</div><canvas id="cv" width="96" height="96"></canvas><br>
 <label><input type="checkbox" id="gray" onchange="draw96()"> 흑백</label>
 <button class="ref" onclick="savePng()">PNG 저장</button></div></div>
 <table id="info"></table>
 <p><button class="ref" onclick="del()">🗑 삭제</button>
 <button class="ref" onclick="view.style.display='none'">닫기</button></p>
</div></div>
<script>
const view=document.getElementById('view'),cv=document.getElementById('cv'),vimg=document.getElementById('vimg');
let cur=null;
function msg(t){document.getElementById('msg').textContent=t}
async function load(){
  const list=await (await fetch('/list')).json();
  list.sort((a,b)=>b.name.localeCompare(a.name));
  const g=document.getElementById('grid'); g.innerHTML='';
  for(const p of list){
    const c=document.createElement('div'); c.className='card';
    c.innerHTML=`<img loading="lazy" src="/photo?n=${p.name}"><div>${p.name}<br>${(p.size/1024).toFixed(1)} KB</div>`;
    c.onclick=()=>open1(p); g.appendChild(c);
  }
  msg(`사진 ${list.length}장`);
}
async function capture(){
  msg('촬영 중...');
  const r=await (await fetch('/capture')).json();
  msg(r.ok?`저장: ${r.name} (${r.width}x${r.height}, ${(r.size/1024).toFixed(1)} KB)`:'촬영 실패: '+r.error);
  load();
}
function open1(p){
  cur=p; document.getElementById('vname').textContent=p.name;
  vimg.onload=()=>{draw96();
    document.getElementById('info').innerHTML=
     `<tr><td></td><td>원본</td><td>96×96</td></tr>
      <tr><td>해상도</td><td>${vimg.naturalWidth}×${vimg.naturalHeight}</td><td>96×96</td></tr>
      <tr><td>픽셀 수</td><td>${vimg.naturalWidth*vimg.naturalHeight}</td><td>9216</td></tr>
      <tr><td>파일 크기</td><td>${(p.size/1024).toFixed(1)} KB (JPEG)</td><td>-</td></tr>`;};
  vimg.src='/photo?n='+p.name; view.style.display='flex';
}
function draw96(){
  const w=vimg.naturalWidth,h=vimg.naturalHeight,s=Math.min(w,h);
  const ctx=cv.getContext('2d');
  ctx.drawImage(vimg,(w-s)/2,(h-s)/2,s,s,0,0,96,96);   // 중앙 정사각형 → 96x96
  if(document.getElementById('gray').checked){
    const d=ctx.getImageData(0,0,96,96);
    for(let i=0;i<d.data.length;i+=4){const y=0.299*d.data[i]+0.587*d.data[i+1]+0.114*d.data[i+2];d.data[i]=d.data[i+1]=d.data[i+2]=y;}
    ctx.putImageData(d,0,0);
  }
}
function savePng(){const a=document.createElement('a');a.download=cur.name.replace('.jpg','_96.png');a.href=cv.toDataURL('image/png');a.click();}
async function del(){ if(!confirm(cur.name+' 삭제?'))return; await fetch('/delete?n='+cur.name); view.style.display='none'; load(); }
load();
</script></body></html>
)rawliteral";

// ------------------------- 카메라 / SD 초기화 -------------------------
bool initCamera() {
  camera_config_t config = {};
  config.ledc_channel = LEDC_CHANNEL_0;  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM; config.pin_d1 = Y3_GPIO_NUM; config.pin_d2 = Y4_GPIO_NUM; config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM; config.pin_d5 = Y7_GPIO_NUM; config.pin_d6 = Y8_GPIO_NUM; config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM; config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM; config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM; config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM; config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size   = FRAMESIZE_QVGA;      // 320x240 (VGA로 바꾸려면 FRAMESIZE_VGA)
  config.jpeg_quality = 12;
  config.fb_count     = 1;
  config.grab_mode    = CAMERA_GRAB_LATEST;
  config.fb_location  = psramFound() ? CAMERA_FB_IN_PSRAM : CAMERA_FB_IN_DRAM;
  if (esp_camera_init(&config) != ESP_OK) { Serial.println("카메라 초기화 실패"); return false; }
  sensor_t *s = esp_camera_sensor_get();
  if (s->id.PID == OV3660_PID) s->set_vflip(s, 1);
  for (int i = 0; i < 3; i++) { camera_fb_t *fb = esp_camera_fb_get(); if (fb) esp_camera_fb_return(fb); }
  return true;
}

bool initSD() {
  SD_MMC.setPins(SD_MMC_CLK, SD_MMC_CMD, SD_MMC_D0);
  if (!SD_MMC.begin("/sdcard", true)) { Serial.println("SD 마운트 실패"); return false; }
  if (!SD_MMC.exists("/photos")) SD_MMC.mkdir("/photos");
  File dir = SD_MMC.open("/photos");
  for (File f = dir.openNextFile(); f; f = dir.openNextFile()) {
    String n = f.name();
    if (n.startsWith("IMG_") && n.endsWith(".jpg")) photoIndex = max(photoIndex, (int)n.substring(4, 8).toInt() + 1);
  }
  return true;
}

// 파일 이름 검사: "IMG_0001.jpg" 형태만 허용 (../ 같은 경로 공격 방지)
bool validName(const String &n) {
  return n.length() == 12 && n.startsWith("IMG_") && n.endsWith(".jpg") && n.indexOf('/') < 0;
}

String capturePhoto() {           // 결과를 JSON 문자열로 돌려줌
  if (!cameraOK || !sdOK) return "{\"ok\":false,\"error\":\"camera or sd not ready\"}";
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) return "{\"ok\":false,\"error\":\"capture failed\"}";
  char name[16], path[32];
  snprintf(name, sizeof(name), "IMG_%04d.jpg", photoIndex);
  snprintf(path, sizeof(path), "/photos/%s", name);
  File file = SD_MMC.open(path, FILE_WRITE);
  String json;
  if (file) {
    file.write(fb->buf, fb->len); file.close(); photoIndex++;
    json = String("{\"ok\":true,\"name\":\"") + name + "\",\"size\":" + fb->len +
           ",\"width\":" + fb->width + ",\"height\":" + fb->height + "}";
    Serial.printf("📷 %s  %dx%d  %u B\n", path, fb->width, fb->height, (unsigned)fb->len);
  } else {
    json = "{\"ok\":false,\"error\":\"file open failed\"}";
  }
  esp_camera_fb_return(fb);
  return json;
}

// ------------------------- 웹 요청 처리 -------------------------
void handleList() {
  String json = "[";
  File dir = SD_MMC.open("/photos");
  bool first = true;
  for (File f = dir.openNextFile(); f; f = dir.openNextFile()) {
    if (f.isDirectory()) continue;
    String n = f.name();
    if (!validName(n)) continue;
    if (!first) json += ",";
    json += "{\"name\":\"" + n + "\",\"size\":" + String((unsigned)f.size()) + "}";
    first = false;
  }
  json += "]";
  server.send(200, "application/json", json);
}

void handlePhoto() {
  String n = server.arg("n");
  if (!validName(n)) { server.send(400, "text/plain", "bad name"); return; }
  File f = SD_MMC.open("/photos/" + n);
  if (!f) { server.send(404, "text/plain", "not found"); return; }
  server.sendHeader("Cache-Control", "max-age=3600");
  server.streamFile(f, "image/jpeg");
  f.close();
}

void handleDelete() {
  String n = server.arg("n");
  if (!validName(n)) { server.send(400, "text/plain", "bad name"); return; }
  bool ok = SD_MMC.remove("/photos/" + n);
  server.send(200, "application/json", ok ? "{\"ok\":true}" : "{\"ok\":false}");
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println("\n예제8: 이미지 갤러리 웹 앱");
  pinMode(BOOT_BUTTON, INPUT_PULLUP);
  cameraOK = initCamera();
  sdOK = initSD();

  if (strlen(STA_SSID) > 0) {                       // 기존 Wi-Fi에 접속
    WiFi.mode(WIFI_STA);
    WiFi.begin(STA_SSID, STA_PASS);
    Serial.print("Wi-Fi 연결 중");
    for (int i = 0; i < 40 && WiFi.status() != WL_CONNECTED; i++) { delay(500); Serial.print("."); }
    Serial.println();
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("접속 주소: http://%s\n", WiFi.localIP().toString().c_str());
  } else {                                          // 보드가 직접 AP가 됨
    WiFi.mode(WIFI_AP);
    uint8_t mac[6]; WiFi.softAPmacAddress(mac);
    char ssid[20]; snprintf(ssid, sizeof(ssid), "W09-CAM-%02X%02X", mac[4], mac[5]);
    WiFi.softAP(ssid, AP_PASS);
    Serial.printf("Wi-Fi 이름: %s  비밀번호: %s\n", ssid, AP_PASS);
    Serial.printf("접속 주소: http://%s\n", WiFi.softAPIP().toString().c_str());
  }

  server.on("/", []() { server.send_P(200, "text/html", INDEX_HTML); });
  server.on("/list", handleList);
  server.on("/photo", handlePhoto);
  server.on("/capture", []() { server.send(200, "application/json", capturePhoto()); });
  server.on("/delete", handleDelete);
  server.onNotFound([]() { server.send(404, "text/plain", "not found"); });
  server.begin();
  Serial.println("웹서버 시작 — BOOT 버튼으로도 촬영할 수 있습니다.");
}

void loop() {
  server.handleClient();
  int btn = digitalRead(BOOT_BUTTON);
  if (lastBtn == HIGH && btn == LOW) { delay(30); if (digitalRead(BOOT_BUTTON) == LOW) capturePhoto(); }
  lastBtn = btn;
  delay(2);
}

#include "Arduino.h"
#include "WiFi.h"
#include <fstream>
#include <sstream>
#include <map>
HardwareSerial Serial; WiFiClass WiFi;
static unsigned long t = 0;
unsigned long millis() { return t += 7; }
void delay(unsigned long d) { t += d; }
void pinMode(int, int) {}
std::map<int,int> pins;
void digitalWrite(int p, int v) { pins[p] = v; }
int digitalRead(int) { return HIGH; }
void tone(uint8_t, unsigned int f, unsigned long) { printf("    (tone %u Hz)\n", f); }
std::string lastPath;
const char* ROOT = getenv("DATA_ROOT");
int mockGET(const std::string& url, std::string& out) {
  auto p = url.find("week10_fruits/"); if (p == std::string::npos) return 404;
  lastPath = url.substr(p + 14);
  std::ifstream f(std::string(ROOT) + "/" + lastPath, std::ios::binary);
  if (!f) return 404;
  std::stringstream ss; ss << f.rdbuf(); out = ss.str(); return 200;
}
// 시뮬레이션용 가짜 응답 (실제 Vision 결과 아님)
int mockPOST(const std::string& url, const std::string& body, std::string& out) {
  if (url.find("key=TESTKEY") == std::string::npos) { out = "{\"error\":{\"code\":400,\"message\":\"API key not valid.\"}}"; return 400; }
  if (body.find("LABEL_DETECTION") == std::string::npos || body.find("\"content\":\"/9j/") == std::string::npos) { out = "{}"; return 400; }
  std::string L;
  if (lastPath.find("apple_04") != std::string::npos) L = "[{\"description\":\"Fruit\",\"score\":0.95},{\"description\":\"Red\",\"score\":0.81}]";
  else if (lastPath.find("lemon_12") != std::string::npos) L = "[{\"description\":\"Citrus\",\"score\":0.93},{\"description\":\"Orange\",\"score\":0.72},{\"description\":\"Lemon\",\"score\":0.61}]";
  else if (lastPath.find("apple") != std::string::npos) L = "[{\"mid\":\"/m/1\",\"description\":\"Fruit\",\"score\":0.96,\"topicality\":0.96},{\"description\":\"Apple\",\"score\":0.93},{\"description\":\"Mcintosh\",\"score\":0.80}]";
  else if (lastPath.find("banana") != std::string::npos) L = "[{\"description\":\"Banana\",\"score\":0.97},{\"description\":\"Cooking plantain\",\"score\":0.80}]";
  else if (lastPath.find("orange") != std::string::npos) L = "[{\"description\":\"Citrus\",\"score\":0.94},{\"description\":\"Orange\",\"score\":0.91},{\"description\":\"Mandarin orange\",\"score\":0.88}]";
  else L = "[{\"description\":\"Lemon\",\"score\":0.92},{\"description\":\"Citrus\",\"score\":0.90},{\"description\":\"Yellow\",\"score\":0.84}]";
  out = "{\"responses\":[{\"labelAnnotations\":" + L + "}]}"; return 200;
}

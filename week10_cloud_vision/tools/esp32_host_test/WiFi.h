#pragma once
#include "Arduino.h"
#define WIFI_STA 1
#define WL_CONNECTED 3
struct IPAddressStub { };
inline void printIP() {}
struct WiFiClass {
  void mode(int) {}
  void begin(const char*, const char*) {}
  int status() { return WL_CONNECTED; }
  const char* localIP() { return "192.168.0.23"; }
  int RSSI() { return -58; }
};
extern WiFiClass WiFi;
struct NetworkClient {
  std::string data; size_t pos = 0;
  size_t available() { return std::min<size_t>(data.size() - pos, 1024); }
  size_t readBytes(uint8_t* b, size_t n) { memcpy(b, data.data() + pos, n); pos += n; return n; }
};
typedef NetworkClient WiFiClient;

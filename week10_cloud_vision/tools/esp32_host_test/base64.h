#pragma once
#include "Arduino.h"
class base64 { public:
  static String encode(const uint8_t* d, size_t n) {
    static const char* T = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    std::string o; size_t i = 0;
    for (; i + 2 < n; i += 3) { uint32_t v = d[i] << 16 | d[i+1] << 8 | d[i+2]; o += T[v>>18]; o += T[(v>>12)&63]; o += T[(v>>6)&63]; o += T[v&63]; }
    if (n - i == 1) { uint32_t v = d[i] << 16; o += T[v>>18]; o += T[(v>>12)&63]; o += "=="; }
    else if (n - i == 2) { uint32_t v = d[i] << 16 | d[i+1] << 8; o += T[v>>18]; o += T[(v>>12)&63]; o += T[(v>>6)&63]; o += '='; }
    return String(o);
  }
};

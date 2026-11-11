#pragma once
#define ARDUINO 10819
#define ARDUINOJSON_ENABLE_PROGMEM 0
#define ARDUINOJSON_ENABLE_ARDUINO_STREAM 0
#define ARDUINOJSON_ENABLE_ARDUINO_PRINT 0
#include <cstdio>
#include <cstdint>
#include <cstdarg>
#include <cstring>
#include <string>
#include <algorithm>
#include <cctype>
#define HIGH 1
#define LOW 0
#define INPUT_PULLUP 2
#define OUTPUT 1
class String {
 public:
  std::string s;
  String() {}
  String(const char* c) : s(c ? c : "") {}
  String(const std::string& x) : s(x) {}
  explicit String(int v) : s(std::to_string(v)) {}
  String(char c) : s(1, c) {}
  const char* c_str() const { return s.c_str(); }
  unsigned int length() const { return s.size(); }
  bool reserve(unsigned int n) { s.reserve(n); return true; }
  bool concat(const char* c) { s += c; return true; }
  bool concat(const char* c, unsigned int n) { s.append(c, n); return true; }
  bool concat(char c) { s += c; return true; }
  String& operator+=(const String& o) { s += o.s; return *this; }
  String& operator+=(const char* o) { s += o; return *this; }
  String& operator+=(char o) { s += o; return *this; }
  String substring(unsigned a, unsigned b) const { return a >= s.size() ? String("") : String(s.substr(a, b - a)); }
  String substring(unsigned a) const { return a >= s.size() ? String("") : String(s.substr(a)); }
  void trim() { size_t a = s.find_first_not_of(" \t\r\n"); size_t b = s.find_last_not_of(" \t\r\n"); s = a == std::string::npos ? "" : s.substr(a, b - a + 1); }
  void toLowerCase() { for (auto& ch : s) ch = tolower(ch); }
  int indexOf(const char* x) const { auto p = s.find(x); return p == std::string::npos ? -1 : (int)p; }
  bool operator==(const char* o) const { return s == o; }
  char operator[](unsigned i) const { return s[i]; }
};
inline String operator+(const String& a, const String& b) { return String(a.s + b.s); }
inline String operator+(const String& a, const char* b) { return String(a.s + b); }
inline String operator+(const char* a, const String& b) { return String(std::string(a) + b.s); }
struct HardwareSerial {
  std::string input;
  size_t pos = 0;
  void begin(int) {}
  int available() { return (int)(input.size() - pos); }
  int read() { return pos < input.size() ? input[pos++] : -1; }
  void print(const char* x) { fputs(x, stdout); }
  void print(const String& x) { fputs(x.c_str(), stdout); }
  void println() { puts(""); }
  void println(const char* x) { puts(x); }
  void println(const String& x) { puts(x.c_str()); }
  int printf(const char* f, ...) { va_list a; va_start(a, f); int r = vprintf(f, a); va_end(a); return r; }
};
extern HardwareSerial Serial;
unsigned long millis();
void delay(unsigned long);
void pinMode(int, int);
void digitalWrite(int, int);
int digitalRead(int);
void tone(uint8_t, unsigned int, unsigned long = 0);

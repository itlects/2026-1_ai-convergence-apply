#pragma once
#include "WiFi.h"
enum followRedirects_t { HTTPC_DISABLE_FOLLOW_REDIRECTS, HTTPC_STRICT_FOLLOW_REDIRECTS, HTTPC_FORCE_FOLLOW_REDIRECTS };
#define HTTP_CODE_OK 200
int mockGET(const std::string& url, std::string& out);
int mockPOST(const std::string& url, const std::string& body, std::string& out);
class HTTPClient {
  std::string url, resp; NetworkClient stream; bool done = false;
 public:
  bool begin(NetworkClient&, String u) { url = u.s; return true; }
  void setTimeout(uint16_t) {}
  void setFollowRedirects(followRedirects_t) {}
  void addHeader(const String&, const String&) {}
  int GET() { int c = mockGET(url, resp); stream.data = resp; return c; }
  int POST(String b) { return mockPOST(url, b.s, resp); }
  int getSize() { return (int)resp.size(); }
  NetworkClient* getStreamPtr() { return &stream; }
  bool connected() { return stream.pos < stream.data.size(); }
  String getString() { return String(resp); }
  void end() {}
};

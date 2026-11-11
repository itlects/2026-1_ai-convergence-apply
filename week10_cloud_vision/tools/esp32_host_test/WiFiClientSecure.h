#pragma once
#include "WiFi.h"
struct NetworkClientSecure : NetworkClient { void setInsecure() {} };
typedef NetworkClientSecure WiFiClientSecure;

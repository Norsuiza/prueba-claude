[app]
title = Sistema IPH
package.name = sistemaiph
package.domain = mx.culiacan.transito
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,kivy,requests,certifi,urllib3,charset-normalizer,idna,pymupdf

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1

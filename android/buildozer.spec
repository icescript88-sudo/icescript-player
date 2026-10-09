[app]

# (str) Title of your application
title = Icescript Player

# (str) Package name
package.name = icescriptplayer

# (str) Package domain (needed for android/ios packaging)
package.domain = org.icescript

# (str) Source code where the main.py lives
source.dir = app

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,db

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,videos/*

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,kivymd,cryptography,sqlite3,pillow

# (str) Supported orientations (portrait, landscape, sensorLandscape, all)
orientation = portrait,landscape

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (string) Presplash background color (for android toolchain)
android.presplash_color = #0A0E17

# (list) Permissions
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 24

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements.
android.accept_sdk_license = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

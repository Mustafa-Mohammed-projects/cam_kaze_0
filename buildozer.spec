[app]

# (str) Title of your application
title = Camkaze Camera

# (str) Package name
package.name = camkaze

# (str) Package domain (needed for android/ios packaging)
package.domain = com.camkaze

# (str) Application version
version = 0.1

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
requirements = python3,kivy,android

# (list) Permissions
android.permissions = CAMERA, READ_MEDIA_IMAGES, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 24

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Accept SDK license automatically
android.accept_sdk_license = True

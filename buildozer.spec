[app]

# (str) Title of your application
title = Camkaze Camera

# (str) Package name
package.name = camkaze

# (str) Package domain (needed for android/ios packaging)
package.domain = com.camkaze

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,android

# (list) Permissions
android.permissions = CAMERA, READ_MEDIA_IMAGES, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be 33 for Android 13
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 24

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip building an APK ($ buildozer android debug)
android.accept_sdk_license = True
android.archs = arm64-v8a
#android.release_artifact = apk

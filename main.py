from datetime import datetime

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.lang import Builder
from kivy.uix.camera import Camera

from jnius import autoclass, PythonJavaClass, java_method
from android.permissions import request_permissions, Permission

PythonActivity = autoclass('org.kivy.android.PythonActivity')
ContentValues = autoclass('android.content.ContentValues')
ImagesMedia = autoclass('android.provider.MediaStore$Images$Media')
AndroidCamera = autoclass('android.hardware.Camera')

KV = """
FloatLayout:
    Label:
        id: status
        size_hint: 1, None
        height: dp(40)
        pos_hint: {'top': 1}
    BoxLayout:
        size_hint: 1, None
        height: dp(100)
        padding: dp(16)
        spacing: dp(16)
        canvas.before:
            Color:
                rgba: 0, 0, 0, .6
            Rectangle:
                pos: self.pos
                size: self.size
        Button:
            id: flash_btn
            text: 'Flash: OFF'
            on_release: app.toggle_flash()
        Button:
            text: 'CAPTURE'
            bold: True
            on_release: app.capture()
        Button:
            id: cam_btn
            text: 'Camera: BACK'
            on_release: app.switch_camera()
"""


class PictureCb(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/Camera$PictureCallback']
    __javacontext__ = 'app'

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('([BLandroid/hardware/Camera;)V')
    def onPictureTaken(self, data, camera):
        self.callback(data)


def to_bytes(data):
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    try:
        return data.tobytes()
    except Exception:
        return bytes(b & 0xFF for b in data)


def save_to_gallery(raw):
    """Saves JPEG to Pictures/CamKaze using MediaStore (no storage permission)."""
    activity = PythonActivity.mActivity
    resolver = activity.getContentResolver()
    name = datetime.now().strftime('IMG_%Y%m%d_%H%M%S.jpg')

    values = ContentValues()
    values.put('_display_name', name)
    values.put('mime_type', 'image/jpeg')
    values.put('relative_path', 'Pictures/CamKaze')

    uri = resolver.insert(ImagesMedia.EXTERNAL_CONTENT_URI, values)
    out = resolver.openOutputStream(uri)
    out.write(bytearray(raw))
    out.flush()
    out.close()


class CamKazeApp(App):
    index = 0            # 0 = back, 1 = front
    flash_on = False
    cam = None
    busy = False
    allowed = False

    def build(self):
        self.root_w = Builder.load_string(KV)
        self.root_w.bind(size=self.layout_cam)
        return self.root_w

    # ---------- lifecycle ----------
    def on_start(self):
        request_permissions([Permission.CAMERA], self.on_perm)

    def on_perm(self, perms, grants):
        if all(grants):
            self.allowed = True
            Clock.schedule_once(lambda dt: self.start_camera(), 0)
        else:
            self.say('Camera permission denied')

    def on_pause(self):
        self.stop_camera()
        return True

    def on_resume(self):
        if self.allowed:
            self.start_camera()

    # ---------- camera ----------
    def start_camera(self):
        self.stop_camera()
        self.flash_on = False
        self.root_w.ids.flash_btn.text = 'Flash: OFF'
        self.cam = Camera(index=self.index, play=True, size_hint=(None, None))
        with self.cam.canvas.before:
            PushMatrix()
            self.rot = Rotate(angle=-90 if self.index == 0 else 90)
        with self.cam.canvas.after:
            PopMatrix()
        self.cam.bind(pos=self.update_rot, size=self.update_rot)
        self.root_w.add_widget(self.cam, index=len(self.root_w.children))
        self.layout_cam()

    def stop_camera(self):
        if not self.cam:
            return
        self.cam.play = False
        try:
            self.cam._camera._release_camera()
        except Exception:
            pass
        self.root_w.remove_widget(self.cam)
        self.cam = None

    def android_cam(self):
        try:
            return self.cam._camera._android_camera
        except Exception:
            return None

    def layout_cam(self, *args):
        if not self.cam:
            return
        w, h = self.root_w.size
        side = min(h, w * 4 / 3)          # preview is 4:3, rotated to portrait
        self.cam.size = (side, side * 3 / 4)
        self.cam.center = self.root_w.center

    def update_rot(self, *args):
        self.rot.origin = self.cam.center

    # ---------- actions ----------
    def switch_camera(self):
        if AndroidCamera.getNumberOfCameras() < 2:
            return self.say('Only one camera available')
        self.index = 1 - self.index
        self.root_w.ids.cam_btn.text = 'Camera: ' + ('BACK' if self.index == 0 else 'FRONT')
        self.start_camera()

    def toggle_flash(self):
        ac = self.android_cam()
        if not ac:
            return
        params = ac.getParameters()
        modes = params.getSupportedFlashModes()
        if modes is None or not modes.contains('torch'):
            return self.say('Flash not supported on this camera')
        self.flash_on = not self.flash_on
        params.setFlashMode('torch' if self.flash_on else 'off')
        ac.setParameters(params)
        self.root_w.ids.flash_btn.text = 'Flash: ON' if self.flash_on else 'Flash: OFF'

    def capture(self):
        ac = self.android_cam()
        if not ac or self.busy:
            return
        self.busy = True
        params = ac.getParameters()
        params.setRotation(90 if self.index == 0 else 270)
        ac.setParameters(params)
        self.pic_cb = PictureCb(self.on_jpeg)   # keep a reference!
        ac.takePicture(None, None, self.pic_cb)

    def on_jpeg(self, data):                    # runs on Android thread
        try:
            save_to_gallery(to_bytes(data))
            msg = 'Saved to Pictures/CamKaze'
        except Exception as e:
            msg = 'Save failed: %s' % e
        self.after_capture(msg)

    @mainthread
    def after_capture(self, msg):
        self.say(msg)
        self.busy = False
        if self.cam:                            # takePicture stops the preview
            self.cam.play = False
            self.cam.play = True

    def say(self, text):
        self.root_w.ids.status.text = text
        Clock.schedule_once(lambda dt: setattr(self.root_w.ids.status, 'text', ''), 3)


if __name__ == '__main__':
    CamKazeApp().run()

from kivy.app import App
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock
from camera4kivy import Preview

KV = """
FloatLayout:
    CamPreview:
        id: preview
        pos_hint: {'x': 0, 'y': 0}
        size_hint: 1, 1

    BoxLayout:
        size_hint: 1, None
        height: dp(110)
        padding: dp(20)
        spacing: dp(20)
        canvas.before:
            Color:
                rgba: 0, 0, 0, 0.5
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

    Label:
        id: status
        text: ''
        size_hint: 1, None
        height: dp(40)
        pos_hint: {'top': 0.98}
"""

class CamPreview(Preview):
    pass

class CamKazeApp(App):
    facing = 'back'
    flash_on = False

    def build(self):
        self.root_widget = Builder.load_string(KV)
        return self.root_widget

    @property
    def preview(self):
        return self.root_widget.ids.preview

    def on_start(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA], self._on_permissions)
        else:
            self._start_camera()

    def _on_permissions(self, permissions, grants):
        if all(grants):
            Clock.schedule_once(lambda dt: self._start_camera(), 0)
        else:
            self.root_widget.ids.status.text = 'Camera permission denied'

    def _start_camera(self):
        self.preview.connect_camera(camera_id=self.facing,
                                    filepath_callback=self.on_saved)

    def on_stop(self):
        self.preview.disconnect_camera()

    def on_pause(self):
        self.preview.disconnect_camera()
        return True

    def on_resume(self):
        self._start_camera()

    def toggle_flash(self):
        self.flash_on = not self.flash_on
        self.preview.flash('on' if self.flash_on else 'off')
        self.root_widget.ids.flash_btn.text = (
            'Flash: ON' if self.flash_on else 'Flash: OFF')

    def switch_camera(self):
        self.facing = 'front' if self.facing == 'back' else 'back'
        self.preview.select_camera(self.facing)
        self.root_widget.ids.cam_btn.text = f'Camera: {self.facing.upper()}'

    def capture(self):
        # Saves to Pictures/CamKaze (shared storage)
        self.preview.capture_photo(location='shared', subdir='CamKaze')

    def on_saved(self, file_path):
        self.root_widget.ids.status.text = 'Photo saved to Pictures/CamKaze'
        Clock.schedule_once(
            lambda dt: setattr(self.root_widget.ids.status, 'text', ''), 2.5)

if __name__ == '__main__':
    CamKazeApp().run()

import os
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

class CamkazeApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        
        # Camera Widget
        self.camera = Camera(index=0, resolution=(1280, 720), play=True)
        self.layout.add_widget(self.camera)
        
        # Status Label
        self.status_label = Label(
            text="Ready", 
            size_hint_y=0.1,
            color=(1, 1, 1, 1)
        )
        self.layout.add_widget(self.status_label)
        
        # Capture Button
        self.capture_button = Button(
            text="Capture Photo", 
            size_hint_y=0.15,
            background_color=(0.2, 0.6, 1, 1)
        )
        self.capture_button.bind(on_press=self.take_picture)
        self.layout.add_widget(self.capture_button)
        
        # Request Android Runtime Permissions
        if platform == 'android':
            self.request_android_permissions()
            
        return self.layout

    def request_android_permissions(self):
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.CAMERA,
            Permission.READ_MEDIA_IMAGES,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE
        ])

    def get_save_directory(self):
        if platform == 'android':
            from android.storage import primary_external_storage_path
            base_dir = primary_external_storage_path()
            target_dir = os.path.join(base_dir, 'Pictures', 'camkaze')
        else:
            target_dir = os.path.join(os.path.expanduser('~'), 'Pictures', 'camkaze')
            
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            
        return target_dir

    def take_picture(self, instance):
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"CAMKAZE_{timestamp}.png"
            directory = self.get_save_directory()
            full_path = os.path.join(directory, filename)
            
            # Export picture from Camera preview
            self.camera.export_to_png(full_path)
            self.status_label.text = f"Saved: {filename}"
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"

if __name__ == '__main__':
    CamkazeApp().run()

from jnius import autoclass
from kivy import platform
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime
from helpers import check_permission
# only works in build
if platform == "android":
    from android.permissions import request_permissions
    from android.storage import primary_external_storage_path

Builder.load_file("audio_recorder.kv")


class MyRecorder:
    """ Main class for using a Recorder for Android apps """
    required_permissions = [
            "android.permission.WRITE_EXTERNAL_STORAGE",
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.RECORD_AUDIO",
        ]

    def __init__(self):
        if not platform == "android":
            return
        self.MediaRecorder = autoclass('android.media.MediaRecorder')
        self.AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        self.OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
        self.AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
        #
        self.ask_permissions()

        if self.check_required_permission():
            self.create_recorder()

    def ask_permissions(self):
        request_permissions(self.required_permissions)

    def check_required_permission(self):
        permissions = self.required_permissions
        #
        has_permissions = True
        for permission in permissions:
            if not check_permission(permission):
                has_permissions = False

        return has_permissions

    def create_recorder(self):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S") \
            .replace(" ", "").replace(":", "").replace("/", "")
        primary_ext_storage = primary_external_storage_path()
        path = primary_ext_storage + '/{}.3gp'.format(dt_string)
        #
        self.recorder = self.MediaRecorder()
        self.recorder.setAudioSource(self.AudioSource.MIC)
        self.recorder.setOutputFormat(self.OutputFormat.THREE_GPP)
        self.recorder.setOutputFile(path)
        self.recorder.setAudioEncoder(self.AudioEncoder.AMR_NB)
        self.recorder.prepare()

    def get_recorder(self):
        if not hasattr(self, "recorder"):
            self.create_recorder()
        return self.recorder

    def remove_recorder(self):
        delattr(self, "recorder")


class AudioApp(App):
    def build(self):
        return AudioTool()

# GUI for the example
class AudioTool(BoxLayout):
    def __init__(self, **kwargs):
        super(AudioTool, self).__init__(**kwargs)
        #
        self.start_button = self.ids['start_button']
        self.stop_button = self.ids['stop_button']
        self.display_label = self.ids['display_label']
        self.switch = self.ids['duration_switch']
        self.user_input = self.ids['user_input']
        self.recorder = MyRecorder()

    def enforce_numeric(self):
        """Make sure the textinput only accepts numbers"""
        if self.user_input.text.isdigit() == False:
            digit_list = [num for num in self.user_input.text if num.isdigit()]
            self.user_input.text = "".join(digit_list)

    def start_recording_clock(self):
        recorder = self.recorder
        if not recorder.check_required_permission():
            return
        self.mins = 0  # Reset the minutes
        self.zero = 1  # Reset if the function gets called more than once
        self.duration = int(self.user_input.text)  # Take the input from the user and convert to a number
        Clock.schedule_interval(self.update_display, 1)
        self.start_button.disabled = True  # Prevents the user from clicking start again which may crash the program
        self.stop_button.disabled = False
        self.switch.disabled = True  # Switch disabled when start is pressed
        Clock.schedule_once(self.start_recording)  # start the recording

    def start_recording(self, dt):
        recorder = self.recorder
        if recorder.check_required_permission():
            recorder.get_recorder().start()
        else:
            recorder.ask_permissions()

    def stop_recording(self):
        recorder = self.recorder
        if recorder:
            Clock.unschedule(self.update_display)
            recorder.get_recorder().stop()
            recorder.get_recorder().reset()
            recorder.get_recorder().release()
            # we need to do this in order to make the object reusable
            recorder.remove_recorder()
        #
        Clock.unschedule(self.start_recording)
        self.display_label.text = 'Finished Recording!'
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.switch.disabled = False

    def update_display(self, dt):
        if self.switch.active == False:
            if self.zero < 60 and len(str(self.zero)) == 1:
                self.display_label.text = '0' + str(self.mins) + ':0' + str(self.zero)
                self.zero += 1

            elif self.zero < 60 and len(str(self.zero)) == 2:
                self.display_label.text = '0' + str(self.mins) + ':' + str(self.zero)
                self.zero += 1

            elif self.zero == 60:
                self.mins += 1
                self.display_label.text = '0' + str(self.mins) + ':00'
                self.zero = 1

        elif self.switch.active == True:
            if self.duration == 0:  # 0
                self.display_label.text = 'Recording Finished!'
                self.stop_recording()
            elif self.duration > 0 and len(str(self.duration)) == 1:  # 0-9
                self.display_label.text = '00' + ':0' + str(self.duration)
                self.duration -= 1

            elif self.duration > 0 and self.duration < 60 and len(str(self.duration)) == 2:  # 0-59
                self.display_label.text = '00' + ':' + str(self.duration)
                self.duration -= 1

            elif self.duration >= 60 and len(str(self.duration % 60)) == 1:  # EG 01:07
                self.mins = self.duration / 60
                self.display_label.text = '0' + str(self.mins) + ':0' + str(self.duration % 60)
                self.duration -= 1

            elif self.duration >= 60 and len(str(self.duration % 60)) == 2:  # EG 01:17
                self.mins = self.duration / 60
                self.display_label.text = '0' + str(self.mins) + ':' + str(self.duration % 60)
                self.duration -= 1


if __name__ == '__main__':
    AudioApp().run()

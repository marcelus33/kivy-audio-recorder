
"""Recoded and simplified AudioRecorder from the previous
version.
YouTube example-Author-Leon-NetPwn """
from jnius import autoclass
from kivy import platform, Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from helpers import check_permission, ask_permission
# solo funciona en el build
if platform == "android":
    from android.permissions import request_permissions, Permission

Builder.load_file("audio_recorder.kv")


class MyRecorder:

    def __init__(self):
        """Recorder object To access Android Hardware"""
        if not platform == "android":
            return

        self.MediaRecorder = autoclass('android.media.MediaRecorder')
        self.AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        self.OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
        self.AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')

        self.ask_permissions()

        if self.check_required_permission():
            self.create_recorder()

    def ask_permissions(self):
        permissions = [
            "android.permission.WRITE_EXTERNAL_STORAGE",
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.RECORD_AUDIO",
        ]

        request_permissions(permissions)

    def check_required_permission(self):
        permissions = [
            "android.permission.WRITE_EXTERNAL_STORAGE",
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.RECORD_AUDIO",
        ]

        has_permissions = True
        for permission in permissions:
            if not check_permission(permission):
                has_permissions = False
            Logger.info("Has permission: " + str(permission))

        return has_permissions

    def create_recorder(self):
        self.mRecorder = self.MediaRecorder()
        self.mRecorder.setAudioSource(self.AudioSource.MIC)
        self.mRecorder.setOutputFormat(self.OutputFormat.THREE_GPP)
        self.mRecorder.setOutputFile('/sdcard/MYAUDIO.3gp')
        self.mRecorder.setAudioEncoder(self.AudioEncoder.AMR_NB)
        self.mRecorder.prepare()


class AudioApp(App):
    def build(self):
        return AudioTool()


class AudioTool(BoxLayout):
    def __init__(self, **kwargs):
        super(AudioTool, self).__init__(**kwargs)

        self.start_button = self.ids['start_button']
        self.stop_button = self.ids['stop_button']
        self.display_label = self.ids['display_label']
        self.switch = self.ids['duration_switch']
        self.user_input = self.ids['user_input']

    def enforce_numeric(self):
        """Make sure the textinput only accepts numbers"""
        if self.user_input.text.isdigit() == False:
            digit_list = [num for num in self.user_input.text if num.isdigit()]
            self.user_input.text = "".join(digit_list)

    def start_recording_clock(self):
        self.r = MyRecorder()
        if not self.r.check_required_permission():
            return
        self.mins = 0  # Reset the minutes
        self.zero = 1  # Reset if the function gets called more than once
        self.duration = int(self.user_input.text)  # Take the input from the user and convert to a number
        Clock.schedule_interval(self.update_display, 1)
        self.start_button.disabled = True  # Prevents the user from clicking start again which may crash the program
        self.stop_button.disabled = False
        self.switch.disabled = True  # TUT Switch disabled when start is pressed
        Clock.schedule_once(self.start_recording)  ## NEW start the recording

    def start_recording(self, dt):  # NEW start the recorder
        self.r = MyRecorder()
        if self.r.check_required_permission():
            self.r.mRecorder.start()
        else:
            self.r.ask_permissions()

    def stop_recording(self):
        if hasattr(self.r, "mRecorder"):
            Clock.unschedule(self.update_display)
            self.r.mRecorder.stop()
            self.r.mRecorder.release()
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

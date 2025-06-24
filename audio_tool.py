import pyaudio
import wave

class GopiAIBaseTool:
    def __init__(self):
        pass

class AudioTool(GopiAIBaseTool):
    def __init__(self):
        super().__init__()
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.p = pyaudio.PyAudio()

    def record_audio(self, filename="output.wav", duration=5):
        """Записывает аудио в WAV файл."""
        try:
            stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)
            print("Recording...")
            frames = []
            for i in range(0, int(self.RATE / self.CHUNK * duration)):
                data = stream.read(self.CHUNK)
                frames.append(data)
            print("Finished recording.")
            stream.stop_stream()
            stream.close()

            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            return filename
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None

    def play_audio(self, filename="output.wav"):
        """Воспроизводит аудио из WAV файла."""
        try:
            wf = wave.open(filename, 'rb')
            stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                                  channels=wf.getnchannels(),
                                  rate=wf.getframerate(),
                                  output=True)
            data = wf.readframes(self.CHUNK)
            while data:
                stream.write(data)
                data = wf.readframes(self.CHUNK)
            stream.stop_stream()
            stream.close()
            wf.close()
            print("Finished playing.")
        except Exception as e:
            print(f"Error playing audio: {e}")

    def close(self):
        self.p.terminate()

# Пример использования
tool = AudioTool()
recorded_file = tool.record_audio()
if recorded_file:
    tool.play_audio(recorded_file)
tool.close()
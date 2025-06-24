import os
import sounddevice as sd
import soundfile as sf

class GopiAIAudioTool:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels

    def record(self, filename, duration):
        print(f"Запись аудио в файл {filename} на {duration} секунд...")
        try:
            recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=self.channels)
            sd.wait()
            sf.write(filename, recording, self.sample_rate)
            print(f"Запись завершена.")
        except Exception as e:
            print(f"Ошибка записи: {e}")

    def play(self, filename):
        print(f"Воспроизведение аудио из файла {filename}...")
        try:
            data, samplerate = sf.read(filename)
            sd.play(data, samplerate)
            sd.wait()
            print(f"Воспроизведение завершено.")
        except FileNotFoundError:
            print(f"Файл {filename} не найден.")
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")

    def get_info(self, filename):
        try:
            info = sf.info(filename)
            return info
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Ошибка получения информации о файле: {e}")
            return None         

# Пример использования:
tool = GopiAIAudioTool()
tool.record("recording.wav", 10)  # Запись 10 секунд
tool.play("recording.wav")      # Воспроизведение
info = tool.get_info("recording.wav")
print(info)
"""
Manejo de efectos de sonido mecánicos y sintetizador de voz natural en español.
Multiplataforma: compatible con Linux, macOS y Windows.
Compatible con empaquetado de ejecutable único (PyInstaller sys._MEIPASS).
"""

import hashlib
import math
import os
import platform
import shutil
import struct
import subprocess
import sys
import threading
import wave

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")
CACHE_DIR = os.path.join(SOUNDS_DIR, "cache")


def _generate_click_wav(filepath: str):
    sample_rate = 22050
    duration = 0.045
    num_samples = int(sample_rate * duration)

    with wave.open(filepath, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        data = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            envelope = math.exp(-t * 90.0)
            freq1 = 1800.0 - 1200.0 * (t / duration)
            freq2 = 850.0
            val = 0.6 * math.sin(2.0 * math.pi * freq1 * t) + 0.4 * math.sin(2.0 * math.pi * freq2 * t)
            noise = ((i * 1103515245 + 12345) & 0x7FFFFFFF) / 0x7FFFFFFF * 2.0 - 1.0
            sample_val = int((val * 0.75 + noise * 0.25) * envelope * 24000)
            sample_val = max(-32767, min(32767, sample_val))
            data.extend(struct.pack("<h", sample_val))

        wav.writeframes(data)


def _generate_chime_wav(filepath: str):
    sample_rate = 22050
    duration = 0.35
    num_samples = int(sample_rate * duration)

    with wave.open(filepath, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        data = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            envelope = math.exp(-t * 8.0)
            f1 = 880.0
            f2 = 1320.0
            f3 = 1760.0
            val = (0.5 * math.sin(2 * math.pi * f1 * t) +
                   0.3 * math.sin(2 * math.pi * f2 * t) +
                   0.2 * math.sin(2 * math.pi * f3 * t))
            sample_val = int(val * envelope * 26000)
            sample_val = max(-32767, min(32767, sample_val))
            data.extend(struct.pack("<h", sample_val))

        wav.writeframes(data)


class SoundPlayer:
    _instance = None

    def __init__(self):
        os.makedirs(SOUNDS_DIR, exist_ok=True)
        os.makedirs(CACHE_DIR, exist_ok=True)

        self.click_path = os.path.join(SOUNDS_DIR, "click.wav")
        self.chime_path = os.path.join(SOUNDS_DIR, "chime.wav")

        if not os.path.exists(self.click_path):
            _generate_click_wav(self.click_path)
        if not os.path.exists(self.chime_path):
            _generate_chime_wav(self.chime_path)

        self.system = platform.system()

        self.mp3_player = None
        for cmd in ["afplay", "mpv", "ffplay", "pw-play", "paplay", "aplay"]:
            if shutil.which(cmd):
                self.mp3_player = cmd
                break

        self.has_gtts = False
        try:
            from gtts import gTTS
            self.has_gtts = True
        except ImportError:
            self.has_gtts = False

        self.macos_voice = None
        if self.system == "Darwin" and shutil.which("say"):
            self._detect_macos_spanish_voice()

        self.system_tts = None
        if shutil.which("spd-say"):
            self.system_tts = "spd-say"
        elif shutil.which("espeak"):
            self.system_tts = "espeak"

        self.muted = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SoundPlayer()
        return cls._instance

    def _detect_macos_spanish_voice(self):
        try:
            out = subprocess.check_output(["say", "-v", "?"], text=True, errors="ignore")
            preferred = ["Monica", "Paulina", "Jorge", "Soledad", "Diego", "Angelica", "Juan"]
            for voice in preferred:
                if voice in out:
                    self.macos_voice = voice
                    return
            for line in out.splitlines():
                if "es_" in line or "es-" in line:
                    parts = line.split()
                    if parts:
                        self.macos_voice = parts[0]
                        return
        except Exception:
            pass

    def play_click(self):
        if self.muted or not self.mp3_player:
            return
        threading.Thread(target=self._play_file, args=(self.click_path,), daemon=True).start()

    def play_chime(self):
        if self.muted or not self.mp3_player:
            return
        threading.Thread(target=self._play_file, args=(self.chime_path,), daemon=True).start()

    def speak_text(self, text: str):
        if self.muted:
            return
        threading.Thread(target=self._do_speak, args=(text,), daemon=True).start()

    def _do_speak(self, text: str):
        cache_key = hashlib.md5(text.strip().encode("utf-8")).hexdigest()
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.mp3")

        if os.path.exists(cache_file):
            self._play_file(cache_file)
            return

        if self.has_gtts:
            try:
                from gtts import gTTS
                tts = gTTS(text=text, lang="es")
                tts.save(cache_file)
                self._play_file(cache_file)
                return
            except Exception:
                pass

        if self.system == "Darwin" and shutil.which("say"):
            try:
                cmd = ["say", "-r", "160"]
                if self.macos_voice:
                    cmd.extend(["-v", self.macos_voice])
                cmd.append(text)
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                return
            except Exception:
                pass

        if self.system_tts == "spd-say":
            try:
                subprocess.run(["spd-say", "-l", "es", "-r", "-10", text],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                return
            except Exception:
                pass
        elif self.system_tts == "espeak":
            try:
                subprocess.run(["espeak", "-v", "es", "-s", "140", text],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                return
            except Exception:
                pass

    def _play_file(self, filepath: str):
        try:
            if not self.mp3_player:
                return

            if self.mp3_player == "mpv":
                subprocess.run(["mpv", "--no-video", "--really-quiet", filepath],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            elif self.mp3_player == "ffplay":
                subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", filepath],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            elif self.mp3_player == "afplay":
                subprocess.run(["afplay", filepath],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            elif self.mp3_player in ["pw-play", "paplay", "aplay"]:
                subprocess.run([self.mp3_player, filepath],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except Exception:
            pass

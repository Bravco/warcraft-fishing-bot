import numpy as np
import time, random, pyaudio
import win32gui, win32api, win32con

def getInputDeviceIndex():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        if device["name"].__contains__("Stereo Mix"):
            return device["index"]

def cast():
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_F6, 0)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_F6, 0)

if __name__ == "__main__":
    hwnd = win32gui.FindWindow(None, "World of Warcraft")
    p = pyaudio.PyAudio()

    cast()
    while True:
        start_time = time.time()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index = getInputDeviceIndex())

        while stream.is_active():
            try:
                data = stream.read(1024, exception_on_overflow = False)
            except Exception as e:
                print("Error reading audio stream:", e)
                break

            data = np.frombuffer(data, dtype=np.int16) / 32768.0
            rms = np.sqrt(np.mean(data**2))
            db = round(20 * np.log10(rms / ((2**15) / 32768.0)))
            print("dB:", db)
            if db > -45:
                time.sleep(random.uniform(0.75, 1.5)) # Wait before catching the fish
                cast() # Catch
                time.sleep(random.uniform(2, 4)) # Wait before casting a bait
                break
            elif (time.time() - start_time) > 17:
                break

        cast() # Bait
        start_time = time.time()

        stream.stop_stream()
        stream.close()

    p.terminate()
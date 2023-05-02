import numpy as np
import time, random, pyaudio
import win32gui, win32api, win32con

def cast(isBait):
    global hwnd
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_F6, 0)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_F6, 0)
    if isBait:
        print("BAIT")
    else:
        print("CATCH")

hwnd = win32gui.FindWindow(None, "World of Warcraft")
p = pyaudio.PyAudio()
input_device_index = 0

for i in range(p.get_device_count()):
    device = p.get_device_info_by_index(i)
    if device["name"].__contains__("Stereo Mix"):
        input_device_index = device["index"]
        break

while True:
    start_time = time.time()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index = input_device_index)

    while stream.is_active():
        data = stream.read(1024, exception_on_overflow = False)
        data = np.frombuffer(data, dtype=np.int16) / 32768.0
        rms = np.sqrt(np.mean(data**2))
        db = round(20 * np.log10(rms / ((2**15) / 32768.0)))
        print(f"dB: {db}")
        if db > -45:
            cast(isBait=False)
            break
        elif (time.time() - start_time) > 17:
            break

    time.sleep(random.uniform(2, 4))
    cast(isBait=True)
    start_time = time.time()
    time.sleep(random.uniform(2, 4))

    stream.stop_stream()
    stream.close()
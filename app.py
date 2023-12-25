import numpy as np
import time, random, pyaudio, keyboard
import win32gui, win32api, win32con

DECIBEL_THRESHOLD = -45
isRunning = True

def toggleRunning(event):
    activeWindow = win32gui.GetForegroundWindow()
    className = win32gui.GetClassName(activeWindow)
    if className == "ConsoleWindowClass":
        global isRunning
        isRunning = not isRunning
        if isRunning:
            print("Resumed")
        else:
            print("Paused")

def cast(isBait):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_F6, 0)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_F6, 0)
    if isBait:
        print("You threw the lure.")
    else:
        print("You caught something.")

if __name__ == "__main__":
    hwnd = win32gui.FindWindow(None, "World of Warcraft")
    p = pyaudio.PyAudio()
    deviceIndex = next((i for i in range(p.get_device_count()) if "Stereo Mix" in p.get_device_info_by_index(i)["name"]), None)

    keyboard.on_press_key("space", toggleRunning)

    print("<Space> - Pause/Resume")
    input("<Enter> - Start")
    cast(isBait=True)
    while True:
        if isRunning:
            start_time = time.time()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index=deviceIndex)

            while stream.is_active():
                if not isRunning:
                    break
                
                try:
                    data = stream.read(1024, exception_on_overflow = False)
                except Exception as e:
                    print("Error reading audio stream:", e)
                    break

                data = np.frombuffer(data, dtype=np.int16) / 32768.0
                rms = np.sqrt(np.mean(data**2))
                db = round(20 * np.log10(rms / ((2**15) / 32768.0)))
                print("dB:", db)

                if db > DECIBEL_THRESHOLD:
                    time.sleep(random.uniform(.5, 1))
                    cast(isBait=False)
                    break
                elif (time.time() - start_time) > 17:
                    break
                    
            if isRunning:
                time.sleep(random.uniform(3, 5))
                cast(isBait=True)
                start_time = time.time()

            stream.stop_stream()
            stream.close()

    p.terminate()
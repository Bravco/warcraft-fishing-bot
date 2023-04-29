import tkinter as tk
import numpy as np
import time, random, pyaudio
import win32gui, win32api, win32con

def cast(isBait):
    global hwnd, iterator
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_F6, 0)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_F6, 0)
    if isBait:
        iterator = 0

def toggle():
    global isRunning
    isRunning = not isRunning

def update():
    global iterator, db, decibelLabel
    if isRunning:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index = input_device_index)

        if stream.is_active():
            data = stream.read(1024, exception_on_overflow = False)
            data = np.frombuffer(data, dtype=np.int16) / 32768.0
            rms = np.sqrt(np.mean(data**2))
            db = round(20 * np.log10(rms / ((2**15) / 32768.0)))
            if db > -45:
                cast(isBait=False)
                time.sleep(random.uniform(2, 4))
                cast(isBait=True)
            elif iterator > 17:
                cast(isBait=True)
        
        decibelLabel.config(text=f"Decibel: {db} dB")
        iterator += .1

        stream.stop_stream()
        stream.close()
    else:
        decibelLabel.config(text="Decibel: - dB")
    
    root.after(10, update)

if __name__ == "__main__":
    isRunning = False
    iterator = 0
    db = 0

    hwnd = win32gui.FindWindow(None, "World of Warcraft")
    p = pyaudio.PyAudio()
    input_device_index = 0

    for i in range(p.get_device_count()):
        if p.get_device_info_by_index(i)["name"] == "Stereo Mix (Realtek(R) Audio)":
            input_device_index = i
            break

    root = tk.Tk()
    root.title("wfb")
    root.geometry(newGeometry="192x64")

    decibelLabel = tk.Label(text="Decibel: - dB")
    decibelLabel.pack()

    button = tk.Button(root, text="Run / Stop", command=toggle)
    button.pack()

    update()
    root.mainloop()
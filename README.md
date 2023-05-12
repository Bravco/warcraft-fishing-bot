# World of Warcraft Fishing Bot

A World of Warcraft fishing bot programmed in Python. It uses the audio output of World of Warcraft window to automatically fish.

![Image](https://static.icy-veins.com/images/wow/og-image-fishing.jpg)

## Getting Started

1. You will need to have Stereo Mix input device in your computer enabled. If you don't see Stereo Mix in your input devices try to update drivers and make sure you have some sort of output device connected to your computer which the Stereo Mix is listening to.

2. Make sure that the ouput device for World of Warcraft is the same output device which the Stereo Mix is listening to. You can check if you have the correct setup by looking at the dB value when sound in the game is played.

3. Install addon called [Better Fishing](https://www.curseforge.com/wow/addons/better-fishing).

4. Make sure that the addon's keybind ```Cast and Interact``` is bind to F6.

5. Turn off every sound type except "Sound Effects". And set your sound volume to following:
    - Master Volume (5% is recommended at 100% system volume, but this can vary based on your system settings.)
    - Music 0%
    - Effects 100%
    - Ambience 0%
    - Dialog 0%

6. Go to a silent place and run the app.exe or app.py and let the bot do the work. It is recommended to don't do anything else on the computer while the bot is fishing, because you can interfere with the sound output!

### Python script

1. You need to install [Python](https://www.python.org/downloads/) onto your computer.

2. After you have installed Python, you need to install all the required libraries to run the fishing bot script. Run ```pip install -r requirements.txt``` in the terminal.

## Supported Platforms

| Platform | Status                     |
|:--------:|:--------------------------:|
| Windows  | :green_heart: Supported    |
| MacOS    | :x: Not supported          |
| Linux    | :grey_question: Not tested |
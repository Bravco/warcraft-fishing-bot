# World of Warcraft Fishing Bot

A simple fishing bot made it python. It uses the audio output of World of Warcraft to auto-fish. Only works for Windows.

## Getting Started

1. You will need to have Stereo Mix input device in your computer enabled. If you don't see Stereo Mix in your input devices try to update drivers and make sure you have some sort of output device connected to your computer which the Stereo Mix is listening to.

2. Make sure that the ouput device for World of Warcraft is the same output device which the Stereo Mix is listening to. You can check if you have the correct setup by looking at the dB value when sound in the game is played.

3. You also need to install [Python](https://www.python.org/downloads/) onto your computer and after you installed Python you need to install all the required libraries to run the fishing bot script. Run ```pip install -r requirements.txt``` in the terminal.

3. Install addon called [Better Fishing](https://www.curseforge.com/wow/addons/better-fishing).

4. Make sure that the addon's keybind cast and interact is set to F6.

5. Turn off every sound type except "Sound Effects". And set your sound volume to following:
    - Master Volume 5% (5% is recommended at 100% system volume, but this can vary based on your system settings.)
    - Music 0%
    - Effects 100%
    - Ambience 0%
    - Dialog 0%

6. Go to a silent place.

7. Now just run the python script and let the bot do the work. It is recommended to don't do anything else on the computer while the bot is fishing, because you can interfere with the sound output!
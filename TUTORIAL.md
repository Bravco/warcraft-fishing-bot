# 🎣 Fishing Bot — Tutorial

## What is this?

An audio-based fishing bot for World of Warcraft. It listens to the game audio via **WASAPI loopback** (no Stereo Mix needed) and automatically reels in when it hears a fish bite sound, then casts again.

---

## How to use

### 1. Run the bot
Double-click `Fishing.exe` or run from terminal:

```cmd
Fishing.exe
```

### 2. Audio device selection
The bot lists all available **loopback devices** — these capture whatever sound is playing through your speakers or headphones. It picks the default one automatically.

> If your game audio goes through a specific device (e.g. "Headphones (Astro A50 Game)"), change it in `config.json` (see "Configuration" below).

### 3. Start fishing
1. Go to World of Warcraft with your character near water
2. Equip a fishing rod
3. Press **Enter** in the bot terminal
4. The bot casts the line and waits for a bite

### 4. Controls

| Key | Action |
|-----|--------|
| `Space` | Pause / Resume |
| `Ctrl+C` | Stop the bot completely |

### 5. What happens
- The bot casts → waits → listens to audio
- When the dB level goes above **-45 dB** (fish bite sound), it reels in
- If nothing happens for **17 seconds**, it re-casts
- Between casts there's a **3–5 second** pause (normal fishing behavior)

---

## Configuration

### Language

Open `config.json` (created automatically next to `Fishing.exe`):

```json
{
  "language": "en"
}
```

Change to `"pt-BR"` for Portuguese. Run the bot again.

### Volume threshold (`DECIBEL_THRESHOLD`)

If the bot catches too early (false positives) or misses bites, adjust the threshold. Currently **-45 dB**. Open `app.py` and change line:

```python
DECIBEL_THRESHOLD = -45
```

Lower (more negative) = harder to trigger. Higher (closer to 0) = easier to trigger.

### Catch delay (`MIN_TIME_BEFORE_CATCH`)

The bot ignores audio for **4 seconds** after each cast to avoid the cast sound itself triggering a catch. Adjust in `app.py`:

```python
MIN_TIME_BEFORE_CATCH = 4
```

---

## Translation system

The bot supports **English** and **Portuguese (Brazil)** out of the box.

### Files

```
Fishing.exe root folder/
├── lang/
│   ├── en.json        ← English phrases
│   └── pt-BR.json     ← Portuguese phrases
├── config.json        ← Language setting
└── Fishing.exe
```

### How to create a new language

1. Copy `lang/en.json` to `lang/fr.json` (or any code you want)
2. Translate the phrases inside
3. Set `"language": "fr"` in `config.json`
4. Run the bot

Each key in the JSON file is a translatable string. Keys you don't translate will fall back to English automatically.

### Editable fields in translation files

| Key | What it is |
|-----|------------|
| `lure_phrases` | Random phrases shown when casting |
| `catch_phrases` | Random phrases shown when catching |
| `header_dB` | "dB:" label in the header |
| `header_pause` | Text for "to pause" / "pausar" |
| `header_unpause` | Text for "to unpause" / "retomar" |
| `header_stop` | Text for "to stop" / "parar" |
| `audio_devices` | Section title when listing devices |
| `pause_resume` | Instruction shown before starting |
| `resumed` / `paused` | Status messages |
| `error` | Error prefix |
| `to_start` | "Press Enter" prompt |

---

## Logs

All terminal output is saved to:

```
logs/2026-07-19.log
```

One file per day, plain text (no colors).

---

## Building from source

Requires Python 3.11+ and pip:

```cmd
pip install -r requirements.txt
pyinstaller --onefile --console --name Fishing ^
  --hidden-import soundcard.mediafoundation ^
  --hidden-import win32console app.py
```

The `.exe` will be in the `dist/` folder.

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| "no loopback device found" | No WASAPI output available | Enable Stereo Mix in Windows Sound Panel (Recording tab, show disabled devices) |
| Bot catches immediately after casting | Cast sound is above -45 dB | Increase `MIN_TIME_BEFORE_CATCH` or lower `DECIBEL_THRESHOLD` |
| Bot never catches | Game volume too low | Raise game volume or lower `DECIBEL_THRESHOLD` (more negative) |
| Header duplicates as logs scroll | Terminal scroll region issue | Restart the bot — the scroll region is set at startup |
| Language not changing | `config.json` might be in wrong folder | Put `config.json` next to `Fishing.exe` |

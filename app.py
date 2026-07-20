import numpy as np
import soundcard as sc
import time, random, keyboard
from datetime import datetime
import win32gui, win32api, win32con, win32console
import os, re, warnings, atexit, sys, json, locale

# ── suppress soundcard WASAPI discontinuity warnings ──
warnings.filterwarnings("ignore", message="data discontinuity")

# ── Console handle ──
hCon = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)

# ── Language system ──
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LANG_DIR = os.path.join(BASE_DIR, 'lang')
os.makedirs(LANG_DIR, exist_ok=True)

DEFAULT_LANG = {
    "en": {
    "audio_devices": "=== audio devices ===",
    "default": "(default)",
    "no_loopback": "[!] no loopback device found",
    "using": "using:",
    "pause_resume": "[space] pause / resume",
    "to_start": "[enter] to start...",
    "resumed": "resumed",
    "paused": "paused",
    "header_pause": "to pause",
    "header_unpause": "to unpause",
    "error": "error",
    "lure_phrases": [
        "lured 🎣",
        "hooked 🎣",
        "casting 🎣",
        "line in water 🎣",
        "bait dropped 🎣"
    ],
    "catch_phrases": [
        "catched 🐟",
        "fish on! 🐟",
        "reeled in 🐟",
        "got one! 🐟",
        "yanked! 🐟"
    ],
    "header_dB": "dB:",
    "header_stop": "to stop",
    "or": "or",
    "key_space": "Space",
    "key_ctrl": "Ctrl",
    "key_c": "C",
    "bracket_open": "[",
    "bracket_close": "]"
},
    "pt-BR": {
    "audio_devices": "=== dispositivos de audio ===",
    "default": "(padrao)",
    "no_loopback": "[!] nenhum dispositivo loopback encontrado",
    "using": "usando:",
    "pause_resume": "[space] pausar / retomar",
    "to_start": "[enter] para comecar...",
    "resumed": "retomado",
    "paused": "pausado",
    "header_pause": "pausar",
    "header_unpause": "para retomar",
    "error": "erro",
    "lure_phrases": [
        "isca lancada 🎣",
        "linha na agua 🎣",
        "anzol jogado 🎣",
        "boia no lago 🎣",
        "aguardando... 🎣"
    ],
    "catch_phrases": [
        "pescado 🐟",
        "fisgou! 🐟",
        "pegou! 🐟",
        "puxou! 🐟",
        "na rede! 🐟"
    ],
    "header_dB": "dB:",
    "header_stop": "parar",
    "or": "ou",
    "key_space": "Espaço",
    "key_ctrl": "Ctrl",
    "key_c": "C",
    "bracket_open": "[",
    "bracket_close": "]"
},
    "fr": {
    "audio_devices": "=== peripheriques audio ===",
    "default": "(par defaut)",
    "no_loopback": "[!] aucun peripherique loopback trouve",
    "using": "utilise :",
    "pause_resume": "[space] pause / reprendre",
    "to_start": "[entree] pour commencer...",
    "resumed": "repris",
    "paused": "en pause",
    "header_pause": "mettre en pause",
    "header_unpause": "reprendre",
    "header_stop": "arreter",
    "or": "ou",
    "error": "erreur",
    "lure_phrases": [
        "lancer 🎣",
        "hamecon a l eau 🎣",
        "ligne lancee 🎣",
        "appat pose 🎣",
        "en attendant... 🎣"
    ],
    "catch_phrases": [
        "attrape 🐟",
        "poisson ! 🐟",
        "ferre ! 🐟",
        "tire ! 🐟",
        "dans le filet ! 🐟"
    ],
    "header_dB": "dB:",
    "key_space": "Espace",
    "key_ctrl": "Ctrl",
    "key_c": "C",
    "bracket_open": "[",
    "bracket_close": "]"
},
    "es": {
    "audio_devices": "=== dispositivos de audio ===",
    "default": "(por defecto)",
    "no_loopback": "[!] ningun dispositivo loopback encontrado",
    "using": "usando:",
    "pause_resume": "[space] pausar / reanudar",
    "to_start": "[enter] para comenzar...",
    "resumed": "reanudado",
    "paused": "pausado",
    "header_pause": "pausar",
    "header_unpause": "reanudar",
    "header_stop": "detener",
    "or": "o",
    "error": "error",
    "lure_phrases": [
        "lanzado 🎣",
        "anzuelo al agua 🎣",
        "linea lanzada 🎣",
        "cebo puesto 🎣",
        "esperando... 🎣"
    ],
    "catch_phrases": [
        "atrapado 🐟",
        "pescado! 🐟",
        "picada! 🐟",
        "tirado! 🐟",
        "en la red! 🐟"
    ],
    "header_dB": "dB:",
    "key_space": "Espacio",
    "key_ctrl": "Ctrl",
    "key_c": "C",
    "bracket_open": "[",
    "bracket_close": "]"
},
    "it": {
    "audio_devices": "=== dispositivi audio ===",
    "default": "(predefinito)",
    "no_loopback": "[!] nessun dispositivo loopback trovato",
    "using": "usando:",
    "pause_resume": "[space] pausa / riprendi",
    "to_start": "[invio] per iniziare...",
    "resumed": "ripreso",
    "paused": "in pausa",
    "header_pause": "metti in pausa",
    "header_unpause": "riprendi",
    "header_stop": "ferma",
    "or": "o",
    "error": "errore",
    "lure_phrases": [
        "lanciato 🎣",
        "amo in acqua 🎣",
        "lenza lanciata 🎣",
        "esca pronta 🎣",
        "in attesa... 🎣"
    ],
    "catch_phrases": [
        "preso 🐟",
        "pesce! 🐟",
        "allamata! 🐟",
        "tirato! 🐟",
        "nella rete! 🐟"
    ],
    "header_dB": "dB:",
    "key_space": "Spazio",
    "key_ctrl": "Ctrl",
    "key_c": "C",
    "bracket_open": "[",
    "bracket_close": "]"
},
    "ru": {
    "audio_devices": "=== audio ustroistva ===",
    "default": "(po umolchaniyu)",
    "no_loopback": "[!] ne naideno loopback-ustroistvo",
    "using": "ispolzuetsya:",
    "pause_resume": "[space] pauza / prodolzhit",
    "to_start": "[enter] dlya nachala...",
    "resumed": "prodolzheno",
    "paused": "priostanovleno",
    "header_pause": "priostanovit",
    "header_unpause": "prodolzhit",
    "header_stop": "ostanovit",
    "or": "ili",
    "error": "oshibka",
    "lure_phrases": [
        "zabrosheno 🎣",
        "krjuchok v vode 🎣",
        "leska zabroshena 🎣",
        "nazhivka na meste 🎣",
        "ozhidanie... 🎣"
    ],
    "catch_phrases": [
        "poiman 🐟",
        "ryba! 🐟",
        "podeseka! 🐟",
        "vytyanuto! 🐟",
        "v seti! 🐟"
    ],
    "header_dB": "dB:",
    "key_space": "Пробел",
    "key_ctrl": "Ctrl",
    "key_c": "C",
    "bracket_open": "[",
    "bracket_close": "]"
}
}# Write default translation files if missing
for code, data in DEFAULT_LANG.items():
    fpath = os.path.join(LANG_DIR, f"{code}.json")
    if not os.path.exists(fpath):
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# ── Config ──
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
config = {}

# Load existing config or create default
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

# Resolve language: config file > auto-detect from Windows locale
if "language" in config:
    LANG_CODE = config["language"]
else:
    # Auto-detect from Windows locale
    try:
        sys_locale = locale.getlocale(locale.LC_CTYPE)[0] or "en"
    except Exception:
        sys_locale = "en"
    LANG_MAP = {"pt_BR": "pt-BR", "pt": "pt-BR", "fr_FR": "fr", "fr": "fr", "es_ES": "es", "es": "es", "it_IT": "it", "it": "it", "ru_RU": "ru", "ru": "ru"}
    LANG_CODE = LANG_MAP.get(sys_locale, "en")
    # Save detected language to config so user can edit it
    config["_available"] = "en, pt-BR, fr, es, it, ru — set 'language' to one of these"
    config["language"] = LANG_CODE
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# Load translation file (user may have edited it)
lang_path = os.path.join(LANG_DIR, f"{LANG_CODE}.json")
if os.path.exists(lang_path):
    with open(lang_path, "r", encoding="utf-8") as f:
        LANG = json.load(f)
else:
    LANG = DEFAULT_LANG.get(LANG_CODE, DEFAULT_LANG["en"])

def t(key):
    """Shorthand for LANG lookup with fallback to English."""
    val = LANG.get(key)
    if val is not None:
        return val
    return DEFAULT_LANG["en"].get(key, f"?{key}?")

# ── Windows Console color attributes ──
GRAY   = win32console.FOREGROUND_BLUE | win32console.FOREGROUND_GREEN | win32console.FOREGROUND_RED
BRIGHT = win32console.FOREGROUND_INTENSITY
WHITE  = GRAY | BRIGHT
CYAN   = win32console.FOREGROUND_BLUE | win32console.FOREGROUND_GREEN | BRIGHT
YELLOW = win32console.FOREGROUND_GREEN | win32console.FOREGROUND_RED | BRIGHT
GREEN  = win32console.FOREGROUND_GREEN | BRIGHT

# ── Terminal padding ──
PAD     = " " * 5
PAD_TOP = 2
HEADER_Y = PAD_TOP
SPACER_Y = PAD_TOP + 1
SCROLL_TOP = PAD_TOP + 2 + 1

# ── Logging ──
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def log_line(msg, to_stdout=True):
    clean = re.sub(r'\033\[[0-9;]*m', '', msg)
    date = datetime.now().strftime("%Y-%m-%d")
    with open(os.path.join(LOG_DIR, f"{date}.log"), "a", encoding="utf-8") as f:
        f.write(clean + "\n")
    if to_stdout:
        print(f"{PAD}{msg}")

def ts():
    return datetime.now().strftime("%H:%M:%S")

# ── Config ──
DECIBEL_THRESHOLD = -40
MIN_TIME_BEFORE_CATCH = 4
isRunning = True

class _State:
    pass
STATE = _State()
STATE.last_db = -999

def toggleRunning(event):
    global isRunning
    isRunning = not isRunning
    status = t("resumed") if isRunning else t("paused")
    log_line(f"\033[90m[{ts()}]\033[0m \033[97m{status}\033[0m")
    # update header immediately to show new state
    draw_header(STATE.last_db)

def cast(isBait):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_F6, 0)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_F6, 0)
    pool = t("lure_phrases") if isBait else t("catch_phrases")
    phrase = random.choice(pool)
    log_line(f"\033[90m[{ts()}]\033[0m {phrase}")

def db_color_attr(db_val):
    if db_val < -60:
        return GRAY
    elif db_val < DECIBEL_THRESHOLD:
        return WHITE
    else:
        return GREEN

def build_header_text(db_val, running):
    """Assemble the header line from translatable parts + running/paused status."""
    S = t
    pause_key = "header_pause" if running else "header_unpause"
    return (f"{S('header_dB')} {db_val:4.0f}"
            f"    {S('bracket_open')}{S('key_space')}{S('bracket_close')} {S(pause_key)}"
            f"  {S('or')}  "
            f"{S('bracket_open')}{S('key_ctrl')}+{S('key_c')}{S('bracket_close')} {S('header_stop')}")

def draw_header(db_val):
    """Write header directly to console buffer with per-segment colors."""
    db_attr = db_color_attr(db_val)
    S = t
    pause_key = "header_pause" if isRunning else "header_unpause"

    segments = [
        (PAD, GRAY),
        (f"{S('header_dB')} ", GRAY),
        (f"{db_val:4.0f}", db_attr),
        ("    ", GRAY),
        (S('bracket_open'), GRAY),
        (S('key_space'), CYAN),
        (S('bracket_close') + " ", GRAY),
        (S(pause_key), GRAY),
        ("  " + S('or') + "  ", GRAY),
        (S('bracket_open'), GRAY),
        (S('key_ctrl'), YELLOW),
        ("+", GRAY),
        (S('key_c'), YELLOW),
        (S('bracket_close') + " ", GRAY),
        (S('header_stop'), GRAY),
    ]

    text = ""
    attrs = []
    for seg_text, seg_attr in segments:
        text += seg_text
        attrs.extend([seg_attr] * len(seg_text))

    text = text.ljust(100)
    while len(attrs) < 100:
        attrs.append(GRAY)

    coord = win32console.PyCOORDType(0, HEADER_Y)
    hCon.WriteConsoleOutputCharacter(text, coord)
    hCon.WriteConsoleOutputAttribute(attrs, coord)

if __name__ == "__main__":
    # ── terminal title ──
    win32console.SetConsoleTitle("Fishing... or not")

    hwnd = win32gui.FindWindow(None, "World of Warcraft")

    # ── list loopback devices ──
    loopbacks = [m for m in sc.all_microphones(include_loopback=True) if m.isloopback]
    default_speaker_name = sc.default_speaker().name
    print()
    print(f"\033[90m{t('audio_devices')}\033[0m")
    for i, lb in enumerate(loopbacks):
        tag = f"  \033[90m{t('default')}\033[0m" if lb.name == default_speaker_name else ""
        print(f"  [{i}] {lb.name}{tag}")

    # ── pick device ──
    loopback = None
    for lb in loopbacks:
        if lb.name == default_speaker_name:
            loopback = lb
            break
    if loopback is None and loopbacks:
        loopback = loopbacks[0]

    if loopback is None:
        print(f"\033[90m{t('no_loopback')}\033[0m")
        exit(1)

    samplerate = 44100
    print(f"\n\033[90m{t('using')}\033[0m {loopback.name}")

    keyboard.on_press_key("space", toggleRunning)
    print(f"\n\033[90m{t('pause_resume')}\033[0m")
    input(f"\033[90m{t('to_start')}\033[0m ")

    # ── clear screen ──
    print("\033[2J\033[H\033[?25l", end="")
    atexit.register(lambda: print("\033[?25h\033[r", end="", flush=True))

    # ── build layout ──
    for _ in range(PAD_TOP):
        print()
    print(f"{PAD}{'':60}")
    print(f"{PAD}")

    info = hCon.GetConsoleScreenBufferInfo()
    buf_h = info['Size'].Y
    print(f"\033[{SCROLL_TOP};{buf_h}r", end="", flush=True)
    print(f"\033[{SCROLL_TOP};1H", end="", flush=True)

    draw_header(-999)
    cast(isBait=True)

    try:
        with loopback.recorder(samplerate=samplerate, blocksize=1024) as rec:
            while True:
                if isRunning:
                    startTime = time.time()
                    lastPrintDb = -999

                    while True:
                        if not isRunning:
                            break

                        try:
                            data = rec.record(numframes=1024)
                        except Exception as e:
                            log_line(f"{t('error')}: {e}")
                            break

                        if data.ndim > 1 and data.shape[1] > 1:
                            data = data.mean(axis=1)

                        rms = np.sqrt(np.mean(data.astype(np.float64) ** 2))
                        if rms > 0:
                            db = np.round(20 * np.log10(rms / 1.0))
                        else:
                            db = -100

                        if abs(db - lastPrintDb) >= 3:
                            lastPrintDb = db
                            STATE.last_db = db
                            draw_header(db)

                        if db > DECIBEL_THRESHOLD and (time.time() - startTime) > MIN_TIME_BEFORE_CATCH:
                            time.sleep(random.uniform(.5, 1))
                            cast(isBait=False)
                            break
                        elif (time.time() - startTime) > 17:
                            break

                    if isRunning:
                        time.sleep(random.uniform(3, 5))
                        cast(isBait=True)
    except Exception as e:
        log_line(f"{t('error')}: {e}")

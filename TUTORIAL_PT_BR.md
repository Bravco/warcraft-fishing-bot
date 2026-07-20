# 🎣 Fishing Bot — Tutorial

## O que é?

Um bot de pesca para World of Warcraft baseado em áudio. Ele escuta o áudio do jogo via **WASAPI loopback** (sem precisar de Stereo Mix) e fisga automaticamente quando ouve o som de mordida, então lança a isca novamente.

---

## Como usar

### 1. Execute o bot
Clique duas vezes no `Fishing.exe` ou rode no terminal:

```cmd
Fishing.exe
```

### 2. Seleção do dispositivo de áudio
O bot lista todos os **dispositivos loopback** disponíveis — eles capturam o som que está saindo pelas suas caixas de som ou fone. Ele escolhe o padrão automaticamente.

> Se o áudio do jogo sair por um dispositivo específico (ex.: "Headphones (Astro A50 Game)"), mude no `config.json` (veja "Configuração" abaixo).

### 3. Comece a pescar
1. Vá para o World of Warcraft com seu personagem perto da água
2. Equipe uma vara de pesca
3. Aperte **Enter** no terminal do bot
4. O bot lança a isca e aguarda a mordida

### 4. Controles

| Tecla | Ação |
|-------|------|
| `Space` | Pausar / Retomar |
| `Ctrl+C` | Parar o bot completamente |

### 5. O que acontece
- O bot lança → espera → escuta o áudio
- Quando o nível de dB passa de **-45 dB** (som de mordida), ele fisga
- Se nada acontecer por **17 segundos**, ele lança novamente
- Entre cada lançamento há uma pausa de **3–5 segundos** (comportamento normal de pesca)

---

## Configuração

### Idioma

Abra o `config.json` (criado automaticamente ao lado do `Fishing.exe`):

```json
{
  "language": "pt-BR"
}
```

Mude para `"en"` se quiser inglês. Execute o bot novamente.

### Sensibilidade do áudio (`DECIBEL_THRESHOLD`)

Se o bot fisgar cedo demais (falso positivo) ou não detectar as mordidas, ajuste o threshold. Atualmente **-45 dB**. Abra o `app.py` e altere a linha:

```python
DECIBEL_THRESHOLD = -45
```

Mais negativo = mais difícil de disparar. Mais perto de 0 = mais fácil.

### Tempo mínimo por lançamento (`MIN_TIME_BEFORE_CATCH`)

O bot ignora áudio por **4 segundos** após cada lançamento para evitar que o som do próprio arremesso dispare uma fisgada. Ajuste no `app.py`:

```python
MIN_TIME_BEFORE_CATCH = 4
```

---

## Sistema de tradução

O bot suporta **Português (Brasil)** e **Inglês** diretamente.

### Arquivos

```
pasta do Fishing.exe/
├── lang/
│   ├── en.json        ← Frases em inglês
│   └── pt-BR.json     ← Frases em português
├── config.json        ← Configuração de idioma
└── Fishing.exe
```

### Como criar um novo idioma

1. Copie `lang/en.json` para `lang/fr.json` (ou o código que quiser)
2. Traduza as frases dentro do arquivo
3. Defina `"language": "fr"` no `config.json`
4. Execute o bot

Cada chave no JSON é uma string traduzível. Chaves não traduzidas cairão para o inglês automaticamente.

### Campos editáveis nos arquivos de tradução

| Chave | O que é |
|-------|---------|
| `lure_phrases` | Frases aleatórias ao lançar isca |
| `catch_phrases` | Frases aleatórias ao pescar |
| `header_dB` | Rótulo "dB:" no cabeçalho |
| `header_pause` | Texto para "pausar" |
| `header_unpause` | Texto para "retomar" |
| `header_stop` | Texto para "parar" |
| `audio_devices` | Título da seção ao listar dispositivos |
| `pause_resume` | Instrução mostrada antes de começar |
| `resumed` / `paused` | Mensagens de status |
| `error` | Prefixo de erro |
| `to_start` | Texto do "Pressione Enter" |

---

## Logs

Toda a saída do terminal é salva em:

```
logs/2026-07-19.log
```

Um arquivo por dia, texto puro (sem cores).

---

## Compilando a partir do código-fonte

Requer Python 3.11+ e pip:

```cmd
pip install -r requirements.txt
pyinstaller --onefile --console --name Fishing ^
  --hidden-import soundcard.mediafoundation ^
  --hidden-import win32console app.py
```

O `.exe` estará na pasta `dist/`.

---

## Solução de problemas

| Problema | Causa | Solução |
|----------|-------|---------|
| "no loopback device found" | Nenhuma saída WASAPI disponível | Ative o Stereo Mix no Painel de Som do Windows (aba Gravação, mostrar dispositivos desativados) |
| Bot fisga logo após lançar | Som do arremesso está acima de -45 dB | Aumente `MIN_TIME_BEFORE_CATCH` ou diminua `DECIBEL_THRESHOLD` |
| Bot nunca fisga | Volume do jogo muito baixo | Aumente o volume do jogo ou diminua `DECIBEL_THRESHOLD` (mais negativo) |
| Header duplica conforme os logs sobem | Problema de scroll region | Reinicie o bot — a scroll region é definida na inicialização |
| Idioma não muda | `config.json` pode estar na pasta errada | Coloque o `config.json` ao lado do `Fishing.exe` |

from pathlib import Path
from bs4 import BeautifulSoup
from gtts import gTTS

# ---- config ----
HTML_IN = Path("jp-big-story.html")                  # original file
HTML_OUT = Path("jp-big-story-with-audio.html")      # file with data-audio attributes
AUDIO_DIR = Path("audio")                            # folder for mp3 files
AUDIO_DIR.mkdir(exist_ok=True)

# ---- read HTML ----
html = HTML_IN.read_text(encoding="utf-8")
soup = BeautifulSoup(html, "lxml")

# ---- collect unique Japanese words from spans ----
unique_words = []
seen = set()

for span in soup.select("span.word"):
    jp = span.get_text(strip=True)
    if not jp:
        continue
    if jp not in seen:
        seen.add(jp)
        unique_words.append(jp)

print(f"Found {len(unique_words)} unique word(s).")

# ---- generate audio per word ----
mapping = {}  # jp -> filename

for idx, jp in enumerate(unique_words, start=1):
    # file name like w001_わたし.mp3  (Japanese in filename is OK on modern systems)
    filename = f"w{idx:03}_{jp}.mp3"
    filepath = AUDIO_DIR / filename

    # Skip if already exists (so you don't regenerate every time)
    if filepath.exists():
        print(f"Skip existing: {filepath.name}")
    else:
        print(f"Generating: {jp} -> {filepath.name}")
        tts = gTTS(text=jp, lang="ja", slow=True)  # slow=True = clearer pronunciation
        tts.save(str(filepath))

    mapping[jp] = filename

# ---- write data-audio attributes into HTML ----
for span in soup.select("span.word"):
    jp = span.get_text(strip=True)
    if jp in mapping:
        span["data-audio"] = f"audio/{mapping[jp]}"

# ---- save updated HTML ----
HTML_OUT.write_text(str(soup), encoding="utf-8")
print(f"Updated HTML saved to: {HTML_OUT}")
print("Place jp-big-story-with-audio.html and audio/ folder together and open in browser.")

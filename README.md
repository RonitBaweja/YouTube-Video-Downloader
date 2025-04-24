# 🎥 YouTube Video Downloader GUI (Python + CustomTkinter)

A modern, user-friendly desktop app to download YouTube videos, shorts, playlists, and extract information from videos, shorts, playlists, and channels — all from a single, clean interface. Built with Python, CustomTkinter, and pytubefix.

---

## 🚀 Features

- 🎞️ **Video Download Tab**
  - Download individual YouTube videos in MP4, WebM, or MP3 format
  - Select preferred resolution
  - Live progress bar and status messages

- 📂 **Playlist Download Tab**
  - Bulk download videos from a playlist
  - Set format and resolution globally
  - Automatic threading to keep UI responsive

- ℹ️ **Video Info Tab**
  - Extract metadata like title, author, channel ID, keywords, and more
  - Copy info directly to clipboard

- 📑 **Playlist Info Tab**
  - Get detailed info about YouTube playlists
  - Scrollable, copy-friendly output

- 👤 **Channel Info Tab**
  - Extract public stats from YouTube channels
  - Details like total videos, views, description, thumbnails, etc.

- ✅ Fully modular tab switching with automatic reset
- 💡 Clean and modern UI using `CustomTkinter`
- 🎯 Threaded downloading to avoid freezing interface

---

## 🛠️ Tech Stack

- **Python 3.12.7**
- [`pytubefix`](https://pypi.org/project/pytubefix/) — for handling YouTube streams
- `CustomTkinter` — for a polished modern GUI
- `threading` — for smooth downloads without blocking
- `Pillow` — to handle button images (e.g., Reset, Back)
- `pyperclip` — to enable copying info to clipboard

---

## 📦 Installation

1. **Clone this repo**
   ```bash
   git clone https://github.com/RonitBaweja/YouTube-Video-Downloader
   ```

2. **Install dependencies**
   ```bash
   pip install pytubefix customtkinter pillow pyperclip
   ```

3. **Run the app**
   ```bash
   python YouTubeDownloader_CompleteCode.py
   ```

---

## 📁 Project Structure

```
📁 youtube-video-downloader/
├── YouTubeDownloader_CompleteCode.py
├── README.md
├── LICENSE
├── HOW_IT_WORKS.md
├── images used/
│   ├── copy_icon.png
│   ├── Reset_Button_Icon.png
│   └── back_button_icon.png
├── TestData.txt
├── YouTubeDownloader_CompleteCode.txt
```

---

## 🔮 Future Improvements

- Theme switcher (Light/Dark)
- Download progress logs
- Save last-used options (format, quality)
- `.exe` packaging using `PyInstaller`

---

## 🧑‍💻 Author

**Ronit Baweja**  
📫 bawejaronit164@gmail.com

🔗 www.linkedin.com/in/ronit-baweja-5a7ab2325

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

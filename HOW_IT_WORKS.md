# 🔍 How the YouTube Downloader Works

This file explains how each tab in the application is structured, the logic behind each feature, and things a developer should modify before running the app on their machine.

---

## 🏗️ General Structure

- The app uses **CustomTkinter** for GUI.
- Each tab is built dynamically using separate `create_<tab>_frame()` functions.
- Threading is used to ensure the GUI remains responsive during downloads.
- Status updates and progress bars are included for better user experience.
- **pyperclip** is used to enable copying info to clipboard.

---

## 🎞️ 1. Video Download Tab

### Logic Flow:

1. **User enters a YouTube video URL**
2. **Creates a YouTube object**  
   → `yt = YouTube(url, on_progress_callback=...)`
3. **Filters available streams**  
   → `.filter(resolution=res, progressive=True, file_extension=format).first()`
4. **Selects and downloads the stream**  
   → `stream.download(output_path=savepath)`
5. **Progress bar and status label update**  
   → Uses `update_video_progress()` and `update_status()`

---

## 📂 2. Playlist Download Tab

### Logic Flow:

1. User enters a **playlist URL**
2. A **Playlist object** is created using `pytubefix.Playlist`
3. Iterates through all video URLs
4. For each video:
   - Creates YouTube object
   - Filters streams
   - Downloads to folder
5. Uses threading to maintain GUI responsiveness

---

## ℹ️ 3. Video Info Tab

1. User enters a **video URL**
2. Creates a YouTube object
3. Based on selected checkboxes, extracts:
   - Title, description, views, keywords, etc.
4. Info is displayed in a scrollable frame with a **copy to clipboard** button

---

## 📑 4. Playlist Info Tab

1. Similar to Video Info but for playlists
2. Uses `pytubefix.Playlist` to extract:
   - Title, video count, channel info, etc.
3. Displays in a scrollable frame

---

## 👤 5. Channel Info Tab

1. User enters a **channel URL**
2. Uses `pytubefix.Channel` to extract:
   - Total views, subscriber count, uploads, etc.

---

## 💫 6. Tab Switch Logic

1. Uses **Tab Initialization Functions** for initial setup of tab's UI.
   - *Clean Reset*: Each time a tab is selected, its UI is created from 
                  scratch, guaranteeing a clean reset.
   - *Simplified Logic*: Need for complex reset logic for individual 
                         widgets is eliminated.
   - *Improved Organization*: The code becomes more modular and easier to 
                            maintain, with each tab's UI code isolated in its own function.
2. This function works as follows:-
   - *current_tab* is initialised to **Video Download Tab** at first.
   - When a tab is switched this function destroys the CTkFrame of current_tab.
   - Calls appropriate create_frame() function for newly selected tab.
   - New Frame with all necessary widgets created for the selected tab.
   - *current_tab* updated to selected tab.
   - We use a dictionary `tab_frames` to keep track of the main CTkFrame for each tab.
      * Remember which frame is currently associated with each tab.
      * ***Centralized Storage***: It provides a central place to manage the frames associated with each tab.

---

## ⚠️ Things to Change Before Running

- 📁 **Image Paths**  
  → Update `"images/back.png"` and similar paths to match your machine’s folder structure.


- 🧩 **Dependencies**  
  Make sure these are installed:
  ```bash
  pip install pytubefix 
  pip install customtkinter 
  pip install pillow
  pip install pyperclip
  ```

---

## 🧠 Tips for Developers

- Modular tab creation helps clean memory and resets states on tab switch
- Avoid using global widget variables across tabs unless necessary
- You can improve theming further by abstracting colors into a config dictionary

---

### ⚠️ Important Note on YouTube & pytubefix
> ⚠️ Disclaimer: YouTube's internal API structure and streaming logic frequently change.
> As a result, the functionality of the pytubefix library — and consequently, this application — may break unexpectedly if YouTube makes significant updates.

To minimize issues:

- Always ensure you're using the **latest version of `pytubefix`:**
```bash
pip install --upgrade pytubefix
```

Keep an eye on the pytubefix GitHub repository or PyPI page for updates and fixes.

**If errors occur while downloading or parsing streams, it's likely due to upstream changes from YouTube, not this code.**

---
Thank You 😉✨

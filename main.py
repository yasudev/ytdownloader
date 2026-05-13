import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import yt_dlp

def fetch_info():
    url = url_entry.get().strip()
    if not url:
        return

    fetch_btn.config(state=tk.DISABLED, text="Fetching...")
    info_text.delete("1.0", tk.END)
    tree.delete(*tree.get_children())

    def worker():
        try:
            ydl_opts = {"quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            root.after(0, display_info, info)
        except Exception as e:
            root.after(0, lambda: info_text.insert(tk.END, f"Error: {e}"))
        finally:
            root.after(0, lambda: fetch_btn.config(state=tk.NORMAL, text="Fetch Info"))

    threading.Thread(target=worker, daemon=True).start()

def display_info(info):
    title = info.get("title", "N/A")
    uploader = info.get("uploader", info.get("channel", "N/A"))
    duration = info.get("duration", 0)
    duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
    view_count = info.get("view_count", "N/A")
    like_count = info.get("like_count", "N/A")

    info_text.insert(tk.END, f"Title: {title}\n")
    info_text.insert(tk.END, f"Channel: {uploader}\n")
    info_text.insert(tk.END, f"Duration: {duration_str}\n")
    info_text.insert(tk.END, f"Views: {view_count}\n")
    info_text.insert(tk.END, f"Likes: {like_count}\n")

    formats = info.get("formats", [])
    seen = set()
    for f in formats:
        resolution = f.get("resolution") or f.get("format_note", "") or ""
        ext = f.get("ext", "")
        filesize = f.get("filesize") or f.get("filesize_approx") or 0
        size_str = f"{filesize / 1024 / 1024:.1f} MB" if filesize else "N/A"
        codec = f.get("vcodec", "audio")
        fps = f.get("fps", "")
        abr = f.get("abr", "")

        row_key = (resolution, ext)
        if row_key in seen:
            continue
        seen.add(row_key)

        if codec != "none":
            fps_str = f"{fps}fps" if fps else ""
            tree.insert("", tk.END, values=(f"{resolution} {fps_str}".strip(), ext, size_str, codec))
        else:
            abr_str = f"{abr}kbps" if abr else ""
            tree.insert("", tk.END, values=(f"audio {abr_str}".strip(), ext, size_str, "audio"))

root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("750x550")

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill=tk.BOTH, expand=True)

input_frame = ttk.Frame(main_frame)
input_frame.pack(fill=tk.X, pady=(0, 10))

ttk.Label(input_frame, text="YouTube URL:").pack(side=tk.LEFT)
url_entry = ttk.Entry(input_frame)
url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
url_entry.bind("<Return>", lambda e: fetch_info())

fetch_btn = ttk.Button(input_frame, text="Fetch Info", command=fetch_info)
fetch_btn.pack(side=tk.LEFT)

info_text = scrolledtext.ScrolledText(main_frame, height=6, wrap=tk.WORD)
info_text.pack(fill=tk.X, pady=(0, 10))

ttk.Label(main_frame, text="Available Formats:").pack(anchor=tk.W)
tree_frame = ttk.Frame(main_frame)
tree_frame.pack(fill=tk.BOTH, expand=True)

tree = ttk.Treeview(tree_frame, columns=("resolution", "ext", "size", "codec"), show="headings", height=12)
tree.heading("resolution", text="Resolution")
tree.heading("ext", text="Format")
tree.heading("size", text="Size")
tree.heading("codec", text="Codec")
tree.column("resolution", width=180)
tree.column("ext", width=80)
tree.column("size", width=100)
tree.column("codec", width=120)

scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

root.mainloop()

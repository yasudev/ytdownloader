import tkinter as tk
from tkinter import ttk
import threading
import os
import yt_dlp
from datetime import timedelta

def format_duration(seconds):
    if not seconds:
        return "N/A"
    return str(timedelta(seconds=int(seconds)))

def format_size(bytes_val):
    if not bytes_val:
        return "N/A"
    mb = bytes_val / 1024 / 1024
    if mb > 1024:
        return f"{mb / 1024:.2f} GB"
    return f"{mb:.1f} MB"

def update_progress(current, total, status_text=""):
    if total > 0:
        pct = current / total * 100
        progress_bar["value"] = pct
        progress_label.config(text=f"{pct:.1f}%")
    progress_status.config(text=status_text)
    root.update_idletasks()

class ProgressHook:
    def __init__(self):
        self.downloaded = 0
        self.total = 0

    def __call__(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            speed = d.get("speed", 0)
            speed_str = f"{speed / 1024 / 1024:.1f} MB/s" if speed else ""
            eta = d.get("eta", 0)
            eta_str = str(timedelta(seconds=int(eta))) if eta else ""
            status = f"{speed_str}  ETA: {eta_str}" if speed or eta else ""
            update_progress(downloaded, total, status)
        elif d["status"] == "finished":
            update_progress(1, 1, "Processing...")

def store_selection():
    sel = tree.selection()
    if sel:
        current_format_id = tree.item(sel[0], "values")[4]

def download():
    url = url_entry.get().strip()
    sel = tree.selection()
    if not url or not sel:
        return

    item = tree.item(sel[0], "values")
    fmt_id = item[4]
    ext = item[1]

    dl_frame.pack(fill=tk.X, pady=(5, 0))
    progress_bar["value"] = 0
    progress_label.config(text="0%")
    progress_status.config(text="Starting...")
    dl_btn.config(state=tk.DISABLED, text="Downloading...")
    tree.column("select", width=30)

    def worker():
        try:
            outtmpl = os.path.join(os.path.expanduser("~/Downloads"), "%(title)s.%(ext)s")
            ydl_opts = {
                "format": fmt_id,
                "outtmpl": outtmpl,
                "quiet": True,
                "no_warnings": True,
                "progress_hooks": [ProgressHook()],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            root.after(0, lambda: progress_status.config(text="Complete!"))
        except Exception as e:
            root.after(0, lambda: progress_status.config(text=f"Error: {e}"))
        finally:
            root.after(0, lambda: dl_btn.config(state=tk.NORMAL, text="Download"))

    threading.Thread(target=worker, daemon=True).start()

def fetch_info():
    url = url_entry.get().strip()
    if not url:
        return

    fetch_btn.config(state=tk.DISABLED, text="Fetching...")
    dl_frame.pack_forget()
    progress_bar["value"] = 0
    progress_label.config(text="")
    progress_status.config(text="")
    title_label.config(text="")
    channel_label.config(text="")
    duration_label.config(text="")
    views_label.config(text="")
    likes_label.config(text="")
    for item in tree.get_children():
        tree.delete(item)

    def worker():
        try:
            ydl_opts = {"quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            root.after(0, lambda: display_info(info))
        except Exception as e:
            root.after(0, lambda: title_label.config(text=f"Error: {e}"))
        finally:
            root.after(0, lambda: fetch_btn.config(state=tk.NORMAL, text="Fetch Info"))

    threading.Thread(target=worker, daemon=True).start()

def display_info(info):
    title = info.get("title", "N/A")
    uploader = info.get("uploader") or info.get("channel") or "N/A"
    duration = format_duration(info.get("duration"))
    views = f"{info.get('view_count', 0):,}" if info.get("view_count") else "N/A"
    likes = f"{info.get('like_count', 0):,}" if info.get("like_count") else "N/A"

    title_label.config(text=title)
    channel_label.config(text=uploader)
    duration_label.config(text=duration)
    views_label.config(text=views)
    likes_label.config(text=likes)

    formats = info.get("formats", [])
    seen = set()
    for f in formats:
        fmt_id = f.get("format_id", "")
        resolution = f.get("resolution") or f.get("format_note", "") or ""
        ext = f.get("ext", "")
        filesize = f.get("filesize") or f.get("filesize_approx") or 0
        codec = f.get("vcodec", "audio")
        fps = f.get("fps", "")
        abr = f.get("abr", "")

        row_key = (resolution, ext, fmt_id)
        if row_key in seen:
            continue
        seen.add(row_key)

        if codec != "none":
            fps_str = f"{fps}fps" if fps else ""
            label = f"{resolution} {fps_str}".strip()
        else:
            abr_str = f"{abr}k" if abr else ""
            label = f"Audio {abr_str}".strip()

        size_str = format_size(filesize)

        select = "\u2713" if row_key == next(iter(seen)) else ""
        tree.insert("", tk.END, values=(select, label, ext, size_str, fmt_id))

root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("800x600")
root.minsize(600, 400)

main_frame = ttk.Frame(root, padding=12)
main_frame.pack(fill=tk.BOTH, expand=True)

url_frame = ttk.LabelFrame(main_frame, text="Video URL", padding=8)
url_frame.pack(fill=tk.X, pady=(0, 10))

url_entry = ttk.Entry(url_frame)
url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
url_entry.bind("<Return>", lambda e: fetch_info())

fetch_btn = ttk.Button(url_frame, text="Fetch Info", command=fetch_info)
fetch_btn.pack(side=tk.RIGHT)

info_frame = ttk.LabelFrame(main_frame, text="Video Info", padding=8)
info_frame.pack(fill=tk.X, pady=(0, 10))

info_grid = ttk.Frame(info_frame)
info_grid.pack(fill=tk.X)

ttk.Label(info_grid, text="Title:", font=("", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=1)
title_label = ttk.Label(info_grid, text="", wraplength=600)
title_label.grid(row=0, column=1, sticky=tk.W, pady=1, padx=(5, 0))

ttk.Label(info_grid, text="Channel:", font=("", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=1)
channel_label = ttk.Label(info_grid, text="")
channel_label.grid(row=1, column=1, sticky=tk.W, pady=1, padx=(5, 0))

ttk.Label(info_grid, text="Duration:", font=("", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=1)
duration_label = ttk.Label(info_grid, text="")
duration_label.grid(row=2, column=1, sticky=tk.W, pady=1, padx=(5, 0))

ttk.Label(info_grid, text="Views:", font=("", 9, "bold")).grid(row=0, column=2, sticky=tk.W, pady=1, padx=(20, 0))
views_label = ttk.Label(info_grid, text="")
views_label.grid(row=0, column=3, sticky=tk.W, pady=1, padx=(5, 0))

ttk.Label(info_grid, text="Likes:", font=("", 9, "bold")).grid(row=1, column=2, sticky=tk.W, pady=1, padx=(20, 0))
likes_label = ttk.Label(info_grid, text="")
likes_label.grid(row=1, column=3, sticky=tk.W, pady=1, padx=(5, 0))

formats_frame = ttk.LabelFrame(main_frame, text="Available Formats", padding=8)
formats_frame.pack(fill=tk.BOTH, expand=True)

tree_frame = ttk.Frame(formats_frame)
tree_frame.pack(fill=tk.BOTH, expand=True)

tree = ttk.Treeview(
    tree_frame,
    columns=("select", "resolution", "ext", "size", "fmt_id"),
    show="headings",
    height=10,
)
tree.heading("select", text="")
tree.heading("resolution", text="Resolution / Quality")
tree.heading("ext", text="Format")
tree.heading("size", text="Size")
tree.heading("fmt_id", text="")

tree.column("select", width=30, anchor=tk.CENTER)
tree.column("resolution", width=220)
tree.column("ext", width=80, anchor=tk.CENTER)
tree.column("size", width=100, anchor=tk.CENTER)
tree.column("fmt_id", width=0, stretch=False)
tree.bind("<<TreeviewSelect>>", store_selection)

scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

dl_frame = ttk.Frame(main_frame)
progress_bar = ttk.Progressbar(dl_frame, mode="determinate")
progress_bar.pack(fill=tk.X, pady=(5, 2))
progress_info = ttk.Frame(dl_frame)
progress_info.pack(fill=tk.X)
progress_label = ttk.Label(progress_info, text="", width=6)
progress_label.pack(side=tk.LEFT)
progress_status = ttk.Label(progress_info, text="")
progress_status.pack(side=tk.LEFT, padx=(10, 0))

dl_btn_frame = ttk.Frame(main_frame)
dl_btn_frame.pack(fill=tk.X, pady=(8, 0))
dl_btn = ttk.Button(dl_btn_frame, text="Download Selected", command=download)
dl_btn.pack(side=tk.RIGHT)

root.mainloop()

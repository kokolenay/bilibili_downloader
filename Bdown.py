import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from queue import Queue


class YouGetDownloader:
    def __init__(self, root):
        self.root = root
        root.title("You-Get 下载器")
        root.geometry("600x400")
        
        # 创建队列用于线程间通信
        self.queue = Queue()
        
        # 创建UI元素
        self.create_widgets()
        
        # 定期检查队列
        self.root.after(100, self.process_queue)

    def create_widgets(self):
        # 创建选项卡
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 视频下载选项卡
        self.video_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.video_tab, text="视频下载")
        
        # 音乐下载选项卡
        self.music_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.music_tab, text="音乐下载")
        
        # 创建视频下载UI
        self.create_video_tab()
        
        # 创建音乐下载UI
        self.create_music_tab()
        
        # 日志区域 (放在底部，共享)
        self.log_text = tk.Text(self.root, height=8, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def create_video_tab(self):
        # 链接输入
        tk.Label(self.video_tab, text="视频链接:").pack(pady=(10, 0), padx=10, anchor="w")
        self.video_url_entry = tk.Entry(self.video_tab, width=50)
        self.video_url_entry.pack(pady=(0, 10), padx=10)
        
        # 下载位置
        tk.Label(self.video_tab, text="下载位置:").pack(pady=(0, 0), padx=10, anchor="w")
        self.video_path_frame = tk.Frame(self.video_tab)
        self.video_path_frame.pack(pady=(0, 10), padx=10, fill="x")
        
        self.video_path_entry = tk.Entry(self.video_path_frame, width=40)
        self.video_path_entry.pack(side="left", fill="x", expand=True)
        
        self.video_browse_btn = tk.Button(self.video_path_frame, text="浏览...", command=lambda: self.browse_path(self.video_path_entry))
        self.video_browse_btn.pack(side="right")
        
        # 进度条
        self.video_progress_label = tk.Label(self.video_tab, text="准备下载...")
        self.video_progress_label.pack(pady=(10, 0), padx=10, anchor="w")
        
        self.video_progress = ttk.Progressbar(self.video_tab, orient="horizontal", length=400, mode="determinate")
        self.video_progress.pack(pady=(0, 20), padx=10)
        
        # 下载按钮
        self.video_download_btn = tk.Button(self.video_tab, text="开始下载视频", command=self.start_video_download)
        self.video_download_btn.pack(pady=(10, 0))

    def create_music_tab(self):
        # 歌曲名称输入
        tk.Label(self.music_tab, text="歌曲名称:").pack(pady=(10, 0), padx=10, anchor="w")
        self.music_name_entry = tk.Entry(self.music_tab, width=50)
        self.music_name_entry.pack(pady=(0, 10), padx=10)
        
        # 歌手名称输入 (可选)
        tk.Label(self.music_tab, text="歌手名称 (可选):").pack(pady=(0, 0), padx=10, anchor="w")
        self.artist_name_entry = tk.Entry(self.music_tab, width=50)
        self.artist_name_entry.pack(pady=(0, 10), padx=10)
        
        # 下载位置
        tk.Label(self.music_tab, text="下载位置:").pack(pady=(0, 0), padx=10, anchor="w")
        self.music_path_frame = tk.Frame(self.music_tab)
        self.music_path_frame.pack(pady=(0, 10), padx=10, fill="x")
        
        self.music_path_entry = tk.Entry(self.music_path_frame, width=40)
        self.music_path_entry.pack(side="left", fill="x", expand=True)
        
        self.music_browse_btn = tk.Button(self.music_path_frame, text="浏览...", command=lambda: self.browse_path(self.music_path_entry))
        self.music_browse_btn.pack(side="right")
        
        # 进度条
        self.music_progress_label = tk.Label(self.music_tab, text="准备下载...")
        self.music_progress_label.pack(pady=(10, 0), padx=10, anchor="w")
        
        self.music_progress = ttk.Progressbar(self.music_tab, orient="horizontal", length=400, mode="determinate")
        self.music_progress.pack(pady=(0, 20), padx=10)
        
        # 下载按钮
        self.music_download_btn = tk.Button(self.music_tab, text="开始下载音乐", command=self.start_music_download)
        self.music_download_btn.pack(pady=(10, 0))

    def browse_path(self, entry_widget):
        directory = filedialog.askdirectory()
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)

    def start_video_download(self):
        url = self.video_url_entry.get().strip()
        path = self.video_path_entry.get().strip()
        
        if not url:
            messagebox.showerror("错误", "请输入视频链接")
            return
        
        if not path:
            path = os.getcwd()  # 使用当前目录如果未指定
        
        # 禁用按钮防止重复点击
        self.video_download_btn.config(state="disabled")
        self.video_progress["value"] = 0
        self.video_progress_label.config(text="准备下载...")
        self.log_message(f"开始下载视频: {url}")
        
        # 启动下载线程
        download_thread = Thread(target=self.download_video, args=(url, path), daemon=True)
        download_thread.start()

    def start_music_download(self):
        song_name = self.music_name_entry.get().strip()
        artist_name = self.artist_name_entry.get().strip()
        path = self.music_path_entry.get().strip()
        
        if not song_name:
            messagebox.showerror("错误", "请输入歌曲名称")
            return
        
        if not path:
            path = os.getcwd()  # 使用当前目录如果未指定
        
        # 构造搜索查询
        search_query = f"{song_name} {artist_name}".strip()
        
        # 禁用按钮防止重复点击
        self.music_download_btn.config(state="disabled")
        self.music_progress["value"] = 0
        self.music_progress_label.config(text="准备下载...")
        self.log_message(f"开始下载音乐: {search_query}")
        
        # 启动下载线程
        download_thread = Thread(target=self.download_music, args=(search_query, path), daemon=True)
        download_thread.start()

    def download_video(self, url, path):
        try:
            # 构造you-get命令
            cmd = ["you-get", "--output-dir", path, url]
            
            # 启动子进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )
            
            # 读取输出
            for line in process.stdout:
                self.queue.put(("video", line.strip()))
                
                # 解析进度
                if "download:" in line.lower():
                    try:
                        percent = line.split("%")[0].split()[-1]
                        percent = float(percent)
                        self.queue.put(("video_progress", percent))
                    except (IndexError, ValueError):
                        pass
            
            process.wait()
            
            if process.returncode == 0:
                self.queue.put(("video_complete", "视频下载完成!"))
            else:
                self.queue.put(("video_error", f"视频下载失败，返回码: {process.returncode}"))
                
        except Exception as e:
            self.queue.put(("video_error", f"视频下载出错: {str(e)}"))

    def download_music(self, search_query, path):
        try:
            # 使用spotdl下载音乐
            cmd = ["spotdl", "download", search_query, "--output", path]
            
            # 启动子进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )
            
            # 读取输出
            for line in process.stdout:
                self.queue.put(("music", line.strip()))
                
                # 解析进度 (spotdl的输出格式可能变化)
                if "%" in line and "downloading" in line.lower():
                    try:
                        percent = line.split("%")[0].split()[-1]
                        percent = float(percent)
                        self.queue.put(("music_progress", percent))
                    except (IndexError, ValueError):
                        pass
            
            process.wait()
            
            if process.returncode == 0:
                self.queue.put(("music_complete", "音乐下载完成!"))
            else:
                self.queue.put(("music_error", f"音乐下载失败，返回码: {process.returncode}"))
                
        except Exception as e:
            self.queue.put(("music_error", f"音乐下载出错: {str(e)}"))

    def process_queue(self):
        try:
            while True:
                # 从队列获取消息
                message = self.queue.get_nowait()
                
                if isinstance(message, tuple):
                    # 处理特殊消息
                    msg_type, content = message
                    
                    if msg_type == "video_progress":
                        self.video_progress["value"] = content
                        self.video_progress_label.config(text=f"下载中: {content:.1f}%")
                    elif msg_type == "video_complete":
                        self.video_progress["value"] = 100
                        self.video_progress_label.config(text=content)
                        self.video_download_btn.config(state="normal")
                        self.log_message(content)
                    elif msg_type == "video_error":
                        self.video_progress_label.config(text=content)
                        self.video_download_btn.config(state="normal")
                        self.log_message(f"视频错误: {content}", error=True)
                    
                    elif msg_type == "music_progress":
                        self.music_progress["value"] = content
                        self.music_progress_label.config(text=f"下载中: {content:.1f}%")
                    elif msg_type == "music_complete":
                        self.music_progress["value"] = 100
                        self.music_progress_label.config(text=content)
                        self.music_download_btn.config(state="normal")
                        self.log_message(content)
                    elif msg_type == "music_error":
                        self.music_progress_label.config(text=content)
                        self.music_download_btn.config(state="normal")
                        self.log_message(f"音乐错误: {content}", error=True)
                    
                    elif msg_type in ("video", "music"):
                        # 普通日志消息
                        self.log_message(content)
                    
                else:
                    # 处理普通日志消息
                    self.log_message(message)
                    
        except:
            pass
        
        # 继续检查队列
        self.root.after(100, self.process_queue)

    def log_message(self, message, error=False):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        if error:
            self.log_text.tag_add("error", "end-1c linestart", "end-1c lineend")
        self.log_text.config(state="disabled")
        self.log_text.see("end")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # 检查you-get和spotdl是否安装
    try:
        subprocess.run(["you-get", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print("警告: you-get未安装，视频下载功能将不可用 (pip install you-get)")
    
    try:
        subprocess.run(["spotdl", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print("警告: spotdl未安装，音乐下载功能将不可用 (pip install spotdl)")
    
    root = tk.Tk()
    app = YouGetDownloader(root)
    
    # 配置错误标签样式
    app.log_text.tag_config("error", foreground="red")
    
    app.run()
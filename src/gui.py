# import os
# import sys
# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox
# import threading
# from pathlib import Path
# import logging
# import shutil
# import tempfile
# import time

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('app.log', encoding='utf-8'),
#         logging.StreamHandler()
#     ]
# )

# try:
#     from model_loader import ModelLoader
# except ImportError:
#     from src.model_loader import ModelLoader

# class WhisperGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("語音轉文字應用程式")
#         self.root.geometry("600x400")
        
#         # 初始化模型載入器
#         self.model_loader = ModelLoader()
        
#         # 創建臨時目錄
#         self.temp_dir = tempfile.mkdtemp(prefix="whisper_")
#         logging.info(f"創建臨時目錄: {self.temp_dir}")
        
#         self.setup_gui()
#         self.load_model()
        
#     def setup_gui(self):
#         """設置 GUI 元件"""
#         # 設置樣式
#         style = ttk.Style()
#         style.configure("TButton", padding=6)
#         style.configure("TProgressbar", thickness=20)

#         # 建立主框架
#         main_frame = ttk.Frame(self.root, padding="10")
#         main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

#         # 資料夾選擇按鈕
#         self.folder_button = ttk.Button(
#             main_frame, 
#             text="選擇音檔資料夾", 
#             command=self.select_folder
#         )
#         self.folder_button.grid(row=1, column=0, columnspan=2, pady=10)

#         # 顯示所選資料夾路徑
#         self.folder_path_var = tk.StringVar()
#         self.folder_path_label = ttk.Label(
#             main_frame, 
#             textvariable=self.folder_path_var, 
#             wraplength=500
#         )
#         self.folder_path_label.grid(row=2, column=0, columnspan=2, pady=10)

#         # 進度條
#         self.progress_var = tk.DoubleVar()
#         self.progress_bar = ttk.Progressbar(
#             main_frame, 
#             length=400, 
#             mode='determinate',
#             variable=self.progress_var
#         )
#         self.progress_bar.grid(row=3, column=0, columnspan=2, pady=10)

#         # 狀態標籤
#         self.status_var = tk.StringVar(value="準備就緒")
#         self.status_label = ttk.Label(
#             main_frame, 
#             textvariable=self.status_var
#         )
#         self.status_label.grid(row=4, column=0, columnspan=2, pady=10)

#         # 開始轉換按鈕
#         self.start_button = ttk.Button(
#             main_frame, 
#             text="開始轉換", 
#             command=self.start_conversion
#         )
#         self.start_button.grid(row=5, column=0, columnspan=2, pady=10)

#         # 初始化處理狀態
#         self.processing = False
        
#         # 設定關閉視窗的處理
#         self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

#     def load_model(self):
#         """載入模型"""
#         self.status_var.set("正在載入模型...")
#         self.root.update()
        
#         try:
#             if self.model_loader.load_model():
#                 self.status_var.set("模型載入完成")
#             else:
#                 messagebox.showerror("錯誤", "模型載入失敗")
#                 self.status_var.set("模型載入失敗")
#         except Exception as e:
#             messagebox.showerror("錯誤", f"載入模型時發生錯誤：\n{str(e)}")
#             self.status_var.set("模型載入失敗")

#     def copy_file_with_retry(self, src, dst, max_retries=3):
#         """複製文件，包含重試機制"""
#         for attempt in range(max_retries):
#             try:
#                 shutil.copy2(src, dst)
#                 # 確認文件存在且大小正確
#                 if os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(src):
#                     return True
#             except Exception as e:
#                 logging.warning(f"複製文件失敗 (嘗試 {attempt + 1}/{max_retries}): {str(e)}")
#                 time.sleep(1)  # 等待一秒後重試
#         return False

#     def select_folder(self):
#         """選擇資料夾"""
#         try:
#             folder_path = filedialog.askdirectory()
#             if folder_path:
#                 # 使用 Path 物件處理路徑
#                 folder_path = Path(folder_path).resolve()
#                 self.folder_path_var.set(str(folder_path))
#                 logging.info(f"選擇資料夾: {folder_path}")
                
#                 # 檢查資料夾中的音頻文件
#                 audio_files = list(folder_path.glob("*.mp3")) + \
#                             list(folder_path.glob("*.wav")) + \
#                             list(folder_path.glob("*.m4a")) + \
#                             list(folder_path.glob("*.flac"))
                
#                 if not audio_files:
#                     messagebox.showwarning("警告", "所選資料夾中沒有支援的音頻文件")
#                 else:
#                     self.status_var.set(f"找到 {len(audio_files)} 個音頻文件")
#         except Exception as e:
#             messagebox.showerror("錯誤", f"選擇資料夾時發生錯誤：\n{str(e)}")

#     def start_conversion(self):
#         """開始轉換"""
#         if not self.folder_path_var.get():
#             messagebox.showerror("錯誤", "請先選擇音檔資料夾")
#             return

#         if self.processing:
#             return

#         # 在新執行緒中執行轉換
#         conversion_thread = threading.Thread(target=self.convert_files)
#         conversion_thread.start()

#     def convert_files(self):
#         """轉換檔案"""
#         try:
#             self.processing = True
#             self.start_button.config(state='disabled')
#             self.folder_button.config(state='disabled')

#             # 使用 Path 物件處理路徑
#             folder_path = Path(self.folder_path_var.get())
            
#             # 獲取所有音頻文件
#             audio_files = []
#             for ext in ['.mp3', '.wav', '.m4a', '.flac']:
#                 audio_files.extend(folder_path.glob(f'*{ext}'))

#             if not audio_files:
#                 messagebox.showinfo("提示", "所選資料夾中沒有支援的音檔")
#                 return

#             # 處理每個音檔
#             for i, audio_path in enumerate(audio_files, 1):
#                 if not self.processing:
#                     break

#                 try:
#                     # 在臨時目錄中創建唯一的文件名
#                     temp_filename = f"temp_{time.time()}_{audio_path.name}"
#                     temp_path = Path(self.temp_dir) / temp_filename
                    
#                     logging.info(f"處理文件: {audio_path}")
#                     logging.info(f"臨時文件路徑: {temp_path}")
                    
#                     # 複製文件到臨時目錄
#                     if not self.copy_file_with_retry(audio_path, temp_path):
#                         raise Exception("無法複製文件到臨時目錄")
                    
#                     # 更新狀態
#                     self.status_var.set(f"正在處理：{audio_path.name}")
#                     self.root.update()

#                     # 轉換音檔
#                     result = self.model_loader.transcribe(str(temp_path))
                    
#                     # 儲存結果
#                     output_path = audio_path.with_suffix('.txt')
#                     with open(output_path, 'w', encoding='utf-8') as f:
#                         f.write(result["text"])

#                     # 更新進度
#                     progress = (i / len(audio_files)) * 100
#                     self.progress_var.set(progress)
                    
#                     # 刪除臨時文件
#                     try:
#                         temp_path.unlink()
#                     except:
#                         pass
                    
#                 except Exception as e:
#                     messagebox.showwarning(
#                         "警告",
#                         f"處理檔案 {audio_path.name} 時發生錯誤：\n{str(e)}\n\n將繼續處理下一個檔案。"
#                     )
#                     logging.error(f"處理檔案 {audio_path.name} 時發生錯誤: {str(e)}")
#                     continue

#             self.status_var.set("轉換完成!")
#             messagebox.showinfo("完成", "所有音檔都已完成轉換!")

#         except Exception as e:
#             messagebox.showerror("錯誤", f"處理過程中發生錯誤：\n{str(e)}")
#             self.status_var.set("處理失敗")
#             logging.error(f"處理過程中發生錯誤: {str(e)}")

#         finally:
#             self.processing = False
#             self.start_button.config(state='normal')
#             self.folder_button.config(state='normal')
#             self.progress_var.set(0)
            
#     def on_closing(self):
#         """關閉視窗時的處理"""
#         try:
#             # 清理臨時目錄
#             if self.temp_dir and os.path.exists(self.temp_dir):
#                 shutil.rmtree(self.temp_dir, ignore_errors=True)
#         finally:
#             self.root.destroy()

# def main():
#     try:
#         root = tk.Tk()
#         app = WhisperGUI(root)
#         root.mainloop()
#     except Exception as e:
#         logging.error(f"程式發生未預期的錯誤: {str(e)}")
#         messagebox.showerror("錯誤", f"程式發生未預期的錯誤：\n{str(e)}")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import logging
import shutil
import tempfile
import time

# 設置日誌記錄
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

try:
    from model_loader import ModelLoader
except ImportError:
    from src.model_loader import ModelLoader

class WhisperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("語音轉文字應用程式")
        self.root.geometry("700x500")
        self.root.configure(bg='#ffffff')  # 背景色為白色

        # 初始化模型載入器
        self.model_loader = ModelLoader()
        
        # 創建臨時目錄
        self.temp_dir = tempfile.mkdtemp(prefix="whisper_")
        logging.info(f"創建臨時目錄: {self.temp_dir}")
        
        self.setup_gui()
        self.load_model()
        
    def setup_gui(self):
        """設置 GUI 元件"""
        # 設置樣式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=10, font=('Helvetica', 11), background="#333333", foreground="#FFFFFF")
        style.configure("TProgressbar", thickness=20, background="#4CAF50")
        style.configure("TLabel", font=('Helvetica', 10), foreground="#333333")
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20", style="TFrame", relief="solid", borderwidth=1)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 選擇檔案按鈕
        self.file_button = ttk.Button(main_frame, text="選擇音檔", command=self.select_files)
        self.file_button.pack(pady=10)

        # 顯示所選檔案路徑
        self.file_path_var = tk.StringVar()
        self.file_path_label = ttk.Label(main_frame, textvariable=self.file_path_var, wraplength=600, anchor="w", justify="left")
        self.file_path_label.pack(pady=10, fill=tk.X)

        # 進度條
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, length=500, mode='determinate', variable=self.progress_var)
        self.progress_bar.pack(pady=20)

        # 狀態標籤
        self.status_var = tk.StringVar(value="準備就緒")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.pack(pady=10)

        # 開始轉換按鈕
        self.start_button = ttk.Button(main_frame, text="開始轉換", command=self.start_conversion)
        self.start_button.pack(pady=10)

        # 初始化處理狀態
        self.processing = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_model(self):
        """載入模型"""
        self.status_var.set("正在載入模型...")
        self.root.update()
        try:
            if self.model_loader.load_model():
                self.status_var.set("模型載入完成")
            else:
                messagebox.showerror("錯誤", "模型載入失敗")
                self.status_var.set("模型載入失敗")
        except Exception as e:
            messagebox.showerror("錯誤", f"載入模型時發生錯誤：\n{str(e)}")
            self.status_var.set("模型載入失敗")

    def select_files(self):
        """選擇音檔文件"""
        try:
            file_paths = filedialog.askopenfilenames(
                title="選擇音檔",
                filetypes=[("音頻文件", "*.mp3 *.wav *.m4a *.flac"), ("所有文件", "*.*")]
            )
            if file_paths:
                self.file_path_var.set("; ".join(file_paths))
                self.selected_files = [Path(path) for path in file_paths]
                self.status_var.set(f"選擇了 {len(self.selected_files)} 個文件")
        except Exception as e:
            messagebox.showerror("錯誤", f"選擇檔案時發生錯誤：\n{str(e)}")

    def start_conversion(self):
        """開始轉換"""
        if not hasattr(self, 'selected_files') or not self.selected_files:
            messagebox.showerror("錯誤", "請先選擇音檔")
            return
        if self.processing:
            return
        conversion_thread = threading.Thread(target=self.convert_files)
        conversion_thread.start()

    def convert_files(self):
        """轉換檔案"""
        try:
            self.processing = True
            self.start_button.config(state='disabled')
            self.file_button.config(state='disabled')

            for i, audio_path in enumerate(self.selected_files, 1):
                if not self.processing:
                    break
                try:
                    temp_filename = f"temp_{time.time()}_{audio_path.name}"
                    temp_path = Path(self.temp_dir) / temp_filename
                    logging.info(f"處理文件: {audio_path}")

                    if not self.copy_file_with_retry(audio_path, temp_path):
                        raise Exception("無法複製文件到臨時目錄")

                    self.status_var.set(f"正在處理：{audio_path.name}")
                    self.root.update()

                    result = self.model_loader.transcribe(str(temp_path))
                    output_path = audio_path.with_suffix('.txt')
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(result["text"])

                    progress = (i / len(self.selected_files)) * 100
                    self.progress_var.set(progress)

                    temp_path.unlink()

                except Exception as e:
                    messagebox.showwarning(
                        "警告",
                        f"處理檔案 {audio_path.name} 時發生錯誤：\n{str(e)}\n\n將繼續處理下一個檔案。"
                    )
                    logging.error(f"處理檔案 {audio_path.name} 時發生錯誤: {str(e)}")

            self.status_var.set("轉換完成!")
            messagebox.showinfo("完成", "所有音檔都已完成轉換!")

        except Exception as e:
            messagebox.showerror("錯誤", f"處理過程中發生錯誤：\n{str(e)}")
            self.status_var.set("處理失敗")
            logging.error(f"處理過程中發生錯誤: {str(e)}")

        finally:
            self.processing = False
            self.start_button.config(state='normal')
            self.file_button.config(state='normal')
            self.progress_var.set(0)

    def copy_file_with_retry(self, src, dst, max_retries=3):
        """複製文件，包含重試機制"""
        for attempt in range(max_retries):
            try:
                shutil.copy2(src, dst)
                if os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(src):
                    return True
            except Exception as e:
                logging.warning(f"複製文件失敗 (嘗試 {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(1)
        return False

    def on_closing(self):
        """關閉視窗時的處理"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        finally:
            self.root.destroy()

def main():
    try:
        root = tk.Tk()
        app = WhisperGUI(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"程式發生未預期的錯誤: {str(e)}")
        messagebox.showerror("錯誤", f"程式發生未預期的錯誤：\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

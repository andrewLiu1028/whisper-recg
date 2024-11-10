import os
import sys
from pathlib import Path
import subprocess
import shutil
import logging

# 設置日誌記錄
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('audio_processing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_ffmpeg_path():
    """獲取 ffmpeg 執行檔路徑"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        ffmpeg_path = os.path.join(base_path, 'ffmpeg.exe')
    else:
        ffmpeg_path = shutil.which('ffmpeg')
        if not ffmpeg_path:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ffmpeg_path = os.path.join(base_path, 'ffmpeg', 'ffmpeg.exe')
    
    if ffmpeg_path and os.path.exists(ffmpeg_path):
        return os.path.normpath(os.path.abspath(ffmpeg_path))
    return None

def check_ffmpeg_available():
    """檢查 ffmpeg 是否可用"""
    try:
        ffmpeg_path = get_ffmpeg_path()
        if not ffmpeg_path:
            logging.error("找不到 ffmpeg 執行檔")
            return False
            
        result = subprocess.run(
            [ffmpeg_path, '-version'],
            capture_output=True,
            text=True,
            errors='ignore'
        )
        return result.returncode == 0
    except Exception as e:
        logging.error(f"檢查 ffmpeg 時發生錯誤: {str(e)}")
        return False

def verify_audio_file(file_path):
    """驗證音頻文件"""
    try:
        # 基本檢查
        if not os.path.exists(file_path):
            return False
            
        # 使用 ffmpeg 檢查文件
        ffmpeg_path = get_ffmpeg_path()
        if not ffmpeg_path:
            return False
            
        result = subprocess.run(
            [ffmpeg_path, '-v', 'error', '-i', file_path, '-f', 'null', '-'],
            capture_output=True,
            text=True,
            errors='ignore'
        )
        
        return not result.stderr
        
    except Exception as e:
        logging.error(f"驗證音頻文件時發生錯誤: {str(e)}")
        return False

def get_supported_audio_files(folder_path):
    """獲取支援的音訊檔案列表"""
    supported_extensions = ('.mp3', '.wav', '.m4a', '.flac')
    valid_files = []
    errors = []
    
    if not os.path.exists(folder_path):
        return [], ["指定的資料夾不存在"]
    
    try:
        files = os.listdir(folder_path)
    except Exception as e:
        return [], [f"無法讀取資料夾: {str(e)}"]
    
    for f in files:
        if f.lower().endswith(supported_extensions):
            full_path = os.path.join(folder_path, f)
            if verify_audio_file(full_path):
                valid_files.append(f)
            else:
                errors.append(f"檔案 {f} 無效或無法讀取")
    
    return valid_files, errors

def get_output_path(audio_path):
    """生成輸出文件路徑"""
    try:
        audio_path = Path(audio_path)
        counter = 0
        base_path = audio_path.parent / f"{audio_path.stem}_transcription"
        output_path = f"{base_path}.txt"
        
        while os.path.exists(output_path):
            counter += 1
            output_path = f"{base_path}_{counter}.txt"
        
        return output_path
    except Exception as e:
        logging.error(f"生成輸出路徑時發生錯誤: {str(e)}")
        raise

def save_transcription(text, output_path):
    """保存轉錄結果"""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    except Exception as e:
        logging.error(f"儲存轉錄結果時發生錯誤: {str(e)}")
        return False

def check_audio_length(file_path):
    """檢查音頻文件長度（秒）"""
    try:
        ffmpeg_path = get_ffmpeg_path()
        if not ffmpeg_path:
            return None
            
        result = subprocess.run(
            [ffmpeg_path, '-i', file_path],
            capture_output=True,
            text=True,
            stderr=subprocess.PIPE
        )
        
        for line in result.stderr.split('\n'):
            if 'Duration' in line:
                try:
                    time_parts = line.split('Duration: ')[1].split(',')[0].split(':')
                    hours = float(time_parts[0])
                    minutes = float(time_parts[1])
                    seconds = float(time_parts[2])
                    return hours * 3600 + minutes * 60 + seconds
                except:
                    return None
    except Exception:
        return None
    
    return None
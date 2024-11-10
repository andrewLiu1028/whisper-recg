import os
import sys
import whisper
import torch
import requests
from pathlib import Path
from tqdm import tqdm

def download_file(url: str, dest_path: Path, chunk_size=1024*1024):
    """下載檔案並顯示進度條"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(dest_path, 'wb') as file, tqdm(
        desc=dest_path.name,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=chunk_size):
            size = file.write(data)
            progress_bar.update(size)

def download_model():
    """下載並儲存 Whisper 模型"""
    print("開始下載 Whisper 模型...")
    
    # 建立 models 目錄
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    try:
        model_name = "large-v3-turbo" #turbo
        model_url = f"https://openaipublic.azureedge.net/main/whisper/{model_name}.pt"
        model_path = models_dir / f"{model_name}.pt"
        
        # 下載模型檔案
        print(f"正在從 {model_url} 下載模型...")
        download_file(model_url, model_path)
        
        # 驗證模型
        print("正在驗證模型...")
        model = whisper.load_model(model_name, download_root=str(models_dir))
        
        print(f"模型已成功下載並驗證: {model_path}")
        
    except Exception as e:
        print(f"下載模型時發生錯誤: {str(e)}")
        if model_path.exists():
            model_path.unlink()  # 如果下載失敗，刪除不完整的文件
        raise

if __name__ == "__main__":
    download_model()
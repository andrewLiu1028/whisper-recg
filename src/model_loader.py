import os
import sys
import warnings
import whisper
import torch
from pathlib import Path
import logging

class ModelLoader:
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 忽略特定警告
        warnings.filterwarnings("ignore", category=FutureWarning)
        warnings.filterwarnings("ignore", category=UserWarning)
        
    def get_model_path(self):
        """獲取模型路徑"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, "models")
    
    def load_model(self, name="large-v3-turbo"):  #turbo
        """載入 Whisper 模型"""
        try:
            # 設定 PYTORCH_HOME 環境變數以指定模型下載位置
            torch.hub.set_dir(self.get_model_path())
            
            # 使用 with 語句塊來暫時禁用警告
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.model = whisper.load_model(
                    name,
                    device=self.device,
                    download_root=self.get_model_path()
                )
            
            return True
        except Exception as e:
            logging.error(f"載入模型時發生錯誤: {str(e)}")
            return False
            
    def transcribe(self, audio_path):
        """轉錄音訊檔案"""
        if self.model is None:
            raise Exception("模型未載入")
        
        try:
            # 確保檔案存在
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"找不到音頻文件: {audio_path}")
            
            # 確保檔案大小正常
            if os.path.getsize(audio_path) == 0:
                raise ValueError(f"音頻文件是空的: {audio_path}")
            
            # 設定轉錄參數
            options = {
                "language": "zh",
                "task": "transcribe"
            }
            
            # 記錄轉錄開始
            logging.info(f"開始轉錄文件: {audio_path}")
            
            # 執行轉錄
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                with torch.no_grad():
                    result = self.model.transcribe(str(audio_path), **options)
            
            # 檢查轉錄結果
            if not result or "text" not in result:
                raise Exception("轉錄結果無效")
                
            # 記錄成功
            logging.info(f"成功轉錄文件: {audio_path}")
            
            return result
            
        except FileNotFoundError as e:
            logging.error(f"找不到文件: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"轉錄過程中發生錯誤: {str(e)}")
            raise
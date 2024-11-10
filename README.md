# 語音轉文字應用程式

這是一個使用 OpenAI Whisper 的語音轉文字應用程式，支援批次處理多個音訊檔案。

## 功能特點

- 使用 Whisper medium 模型進行語音辨識
- 支援多種音訊格式 (MP3, WAV, M4A, FLAC)
- 批次處理整個資料夾的音訊檔案
- 直觀的圖形使用者介面
- 顯示處理進度和狀態
- 支援 GPU 加速（如果可用）

## 安裝說明

1. 安裝 Python 3.8 或更新版本

2. 建立虛擬環境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

4. 下載 Whisper 模型：
```bash
python tools/download_model.py
```

## 開發執行

直接執行主程式：
```bash
python src/gui.py
```

## 打包執行檔

1. 確保已經下載模型：
```bash
python tools/download_model.py
```

2. 執行打包腳本：
```bash
python tools/build.py
```

打包完成後，可以在 `dist/Speech2Text` 目錄找到執行檔。

## 使用說明

1. 啟動應用程式
2. 點擊「選擇音檔資料夾」按鈕選擇要處理的資料夾
3. 點擊「開始轉換」按鈕開始處理
4. 等待處理完成，轉換結果會儲存在原音檔所在的資料夾中

## 系統需求

- Windows 10/11 或 Linux 或 macOS
- 至少 8GB RAM
- 建議有 NVIDIA GPU（支援 CUDA）以獲得更好的效能
- 至少 4GB 硬碟空間

## 注意事項

- 首次啟動時需要一些時間來載入模型
- 使用 GPU 可以大幅提升處理速度
- 轉換長音訊檔案時可能需要較長時間
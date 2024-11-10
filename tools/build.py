import os
import sys
import shutil
from pathlib import Path
import PyInstaller.__main__
import requests
import zipfile
import tempfile
from tqdm import tqdm
import hashlib
import json

class WhisperBuilder:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.models_dir = self.root_dir / "models"
        self.ffmpeg_dir = self.root_dir / "ffmpeg"
        self.model_file = self.models_dir / "large-v3-turbo.pt"
        self.ffmpeg_exe = self.ffmpeg_dir / "ffmpeg.exe"
        self.dist_dir = self.root_dir / "dist"
        self.build_dir = self.root_dir / "build"
        
    def download_with_progress(self, url: str, dest_path: Path, desc: str = "Downloading"):
        """Download file with progress bar"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(dest_path, 'wb') as file, tqdm(
                desc=desc,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    size = file.write(chunk)
                    pbar.update(size)
            return True
        except Exception as e:
            print(f"Download failed: {str(e)}")
            if dest_path.exists():
                dest_path.unlink()
            return False

    def verify_file_hash(self, file_path: Path, expected_hash: str) -> bool:
        """Verify file integrity using SHA256"""
        if not file_path.exists():
            return False
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest() == expected_hash

    def download_ffmpeg(self) -> bool:
        """Download and extract ffmpeg"""
        print("\nDownloading FFmpeg...")
        
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            zip_path = temp_dir / "ffmpeg.zip"
            
            # Download FFmpeg
            if not self.download_with_progress(ffmpeg_url, zip_path, "Downloading FFmpeg"):
                return False
            
            print("Extracting FFmpeg...")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Extract only ffmpeg.exe
                    for item in zip_ref.namelist():
                        if item.endswith('ffmpeg.exe'):
                            zip_ref.extract(item, temp_dir)
                            extracted_ffmpeg = temp_dir / item
                            self.ffmpeg_dir.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(extracted_ffmpeg, self.ffmpeg_exe)
                            print("FFmpeg successfully installed!")
                            return True
                print("FFmpeg.exe not found in zip file!")
                return False
            except Exception as e:
                print(f"Error extracting FFmpeg: {str(e)}")
                return False

    def verify_dependencies(self) -> bool:
        """Verify all required dependencies are present"""
        missing = []
        
        # Check model file
        if not self.model_file.exists():
            missing.append("Whisper model file (medium.pt)")
        
        # Check FFmpeg
        if not self.ffmpeg_exe.exists():
            missing.append("FFmpeg executable")
        
        if missing:
            print("\nMissing dependencies:")
            for item in missing:
                print(f"- {item}")
            return False
        return True

    def cleanup_previous_build(self):
        """Clean up previous build artifacts"""
        print("\nCleaning up previous build...")
        for path in [self.dist_dir, self.build_dir]:
            if path.exists():
                shutil.rmtree(path)

    def build_executable(self):
        """Build the executable using PyInstaller"""
        print("\nBuilding executable...")
        
        main_file = str(self.root_dir / "src" / "gui.py")
        
        # PyInstaller arguments
        args = [
            main_file,
            '--name=Speech2Text',
            '--onefile',
            '--windowed',
            '--clean',
            '--noconfirm',
            
            # Add data files
            f'--add-data={str(self.models_dir)}{os.pathsep}models',
            f'--add-data={str(self.ffmpeg_exe)}{os.pathsep}.',
            f'--paths={str(self.root_dir / "src")}',
            
            # Hidden imports
            '--hidden-import=torch',
            '--hidden-import=numpy',
            '--hidden-import=whisper',
            '--hidden-import=tqdm',
            '--hidden-import=src.model_loader',
            '--hidden-import=src.utils',
            
            # Optimization options
            '--log-level=WARN',
            '--collect-submodules=whisper',
            '--collect-submodules=torch',
            '--collect-all=whisper',
        ]
        
        try:
            PyInstaller.__main__.run(args)
            
            # Verify build success
            exe_path = self.dist_dir / "Speech2Text.exe"
            if not exe_path.exists():
                raise Exception("Executable not found after build")
            
            # Copy to root directory
            final_path = self.root_dir / "Speech2Text.exe"
            shutil.copy2(exe_path, final_path)
            
            print(f"\nBuild successful!")
            print(f"Executable location: {final_path}")
            print(f"Size: {final_path.stat().st_size / (1024*1024):.1f} MB")
            
            return True
            
        except Exception as e:
            print(f"\nBuild failed: {str(e)}")
            return False

def main():
    print("Starting Whisper Application build process...")
    
    builder = WhisperBuilder()
    
    # Clean up previous build
    builder.cleanup_previous_build()
    
    # Verify/download dependencies
    if not builder.verify_dependencies():
        if not builder.ffmpeg_exe.exists():
            if not builder.download_ffmpeg():
                print("Failed to download FFmpeg!")
                sys.exit(1)
        
        if not builder.model_file.exists():
            print("Whisper model not found! Please run download_model.py first.")
            sys.exit(1)
    
    # Build executable
    if builder.build_executable():
        print("\nBuild process completed successfully!")
    else:
        print("\nBuild process failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()


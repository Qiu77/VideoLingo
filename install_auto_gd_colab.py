import os
import sys
import platform
import subprocess
import pkg_resources

from google.colab import drive
from rich.console import Console
from rich.panel import Panel

# 配置 Rich 控制台用于美化输出
console = Console()

def check_and_install_library(library_name, google_drive_path, url=None):
    """
    检查并安装第三方库，并管理安装包
    
    Args:
        library_name (str): 需要安装的库名
        google_drive_path (str): Google Drive 存储路径
    """
    # 连接 Google Drive
    drive.mount('/content/drive', force_remount=True)
    
    # 确保存储路径存在
    os.makedirs(google_drive_path, exist_ok=True)
    
    try:
        # 尝试获取库的分发信息，检查是否已安装
        pkg_resources.get_distribution(library_name)
        console.print(Panel(f"✅ {library_name} 已经安装", style="green"))
        return
    except pkg_resources.DistributionNotFound:
        console.print(Panel(f"🔍 准备安装 {library_name}", style="yellow"))
    
    # 构建 whl 文件路径
    whl_filename = f"{library_name}.whl"
    whl_path = os.path.join(google_drive_path, whl_filename)
    
    # 检查 Google Drive 是否已有安装包
    if os.path.exists(whl_path):
        console.print(Panel(f"📦 发现 {library_name} 安装包，从 Google Drive 安装", style="cyan"))
        subprocess.check_call([sys.executable, "-m", "pip", "install", whl_path])
    else:
        # 下载并安装库
        console.print(Panel(f"📥 开始下载并安装 {library_name}", style="blue"))
        
        try:
            # 下载 whl 文件到 Google Drive
            if url:
                subprocess.check_call([
                    sys.executable, 
                    "-m", "pip", 
                    "download", 
                    "-d", google_drive_path, 
                    "--index-url", url,
                    library_name
                ])

            else:
                subprocess.check_call([
                    sys.executable, 
                    "-m", "pip", 
                    "download", 
                    "-d", google_drive_path, 
                    library_name
                ])
            
            # 查找下载的 whl 文件
            whl_files = [f for f in os.listdir(google_drive_path) if f.endswith('.whl')]
            
            if whl_files:
                whl_file_path = os.path.join(google_drive_path, whl_files[0])
                subprocess.check_call([sys.executable, "-m", "pip", "install", whl_file_path])
                console.print(Panel(f"✅ {library_name} 安装成功", style="green"))
            else:
                # 如果下载失败，直接使用 pip 安装
                subprocess.check_call([sys.executable, "-m", "pip", "install", library_name])
                console.print(Panel(f"⚠️ 使用在线安装方式安装 {library_name}", style="yellow"))
        
        except subprocess.CalledProcessError as e:
            console.print(Panel(f"❌ {library_name} 安装失败: {str(e)}", style="red"))
            raise

def detect_gpu_and_install_torch():
    """
    检测 GPU 并安装对应版本的 PyTorch
    """
    try:
        import torch
        console.print(Panel("🔍 检测到已安装 PyTorch", style="green"))
        return
    except ImportError:
        pass

    try:
        import pynvml
        pynvml.nvmlInit()
        gpu_count = pynvml.nvmlDeviceGetCount()
        
        if gpu_count > 0:
            console.print(Panel("🎮 检测到 NVIDIA GPU", style="cyan"))
            # subprocess.check_call([
            #     sys.executable, 
            #     "-m", "pip", 
            #     "install", 
            #     "torch==2.0.0", 
            #     # "torchvision", 
            #     "torchaudio==2.0.0",
            #     "--index-url", 
            #     "https://download.pytorch.org/whl/cu118"
            # ])

            libraries_to_install = [
                "torch==2.0.0", 
                "torchaudio==2.0.0"
            ]

            for library in libraries_to_install:
                check_and_install_library(library, libraries_path, url="https://download.pytorch.org/whl/cu118")
        else:
            console.print(Panel("💻 未检测到 GPU，安装 CPU 版 PyTorch... Note: it might be slow during whisperX transcription.", style="yellow"))
            # subprocess.check_call([
            #     sys.executable, 
            #     "-m", "pip", 
            #     "install", 
            #     "torch==2.1.2", 
            #     # "torchvision", 
            #     "torchaudio==2.1.2"
            # ])

            libraries_to_install = [
                "torch==2.1.2",  
                "torchaudio==2.1.2"
            ]

            for library in libraries_to_install:
                check_and_install_library(library, libraries_path)

    except Exception as e:
        console.print(Panel(f"❌ PyTorch 安装失败: {str(e)}", style="red"))
        raise
    finally:
        pynvml.nvmlShutdown()

def main():
    """
    主函数，管理库的安装
    """
    # Google Drive 中存储安装包的路径
    libraries_path = "/content/drive/MyDrive/python_libraries"
    
    # 需要安装的库列表
    libraries_to_install = [
        'rich',          # 控制台输出美化
        'numpy',         # 数值计算
        'pandas',        # 数据处理
        'matplotlib',    # 数据可视化
        'requests',      # HTTP 请求
        'pynvml'         # GPU 检测
    ]
    
    # 安装必要的支持库
    console.print(Panel("🚀 开始安装依赖库", style="bold magenta"))
    
    # 逐个安装库
    for library in libraries_to_install:
        check_and_install_library(library, libraries_path)
    
    # 检测并安装 PyTorch
    detect_gpu_and_install_torch()

    # 安装requirements依赖库
    def install_requirements():
        try:
            # 需要安装的库列表
            libraries_to_install = [
                "librosa==0.10.2.post1",
                "pytorch-lightning==2.3.3",
                "lightning==2.3.3",
                "transformers==4.39.3",
                "moviepy==1.0.3",
                "numpy==1.26.4",
                "openai==1.55.3",
                "opencv-python==4.10.0.84",
                "openpyxl==3.1.5",
                "pandas==2.2.3",
                "pydub==0.25.1",
                "PyYAML==6.0.2",
                "replicate==0.33.0",
                "requests==2.32.3",
                "resampy==0.4.3",
                "spacy==3.7.4",
                "streamlit==1.38.0",
                "yt-dlp",
                "json-repair",
                "ruamel.yaml",
                "InquirerPy",
                "autocorrect-py",
                "ctranslate2==4.4.0",
                "edge-tts",
                "syllables",
                "pypinyin",
                "g2p-en"
            ]
            
            # 安装requirements依赖库
            console.print(Panel("🚀 开始安装requirements依赖库", style="bold magenta"))
            
            # 逐个安装库
            for library in libraries_to_install:
                check_and_install_library(library, libraries_path)

        except subprocess.CalledProcessError as e:
            console.print(Panel(t("❌ Failed to install requirements:") + str(e), style="red"))

    
    console.print(Panel("✅ 所有依赖库安装完成", style="bold green"))

if __name__ == "__main__":
    main()

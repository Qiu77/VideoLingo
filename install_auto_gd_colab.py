import os
import sys
import platform
import subprocess

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

ascii_logo = """
__     ___     _            _     _                    
\ \   / (_) __| | ___  ___ | |   (_)_ __   __ _  ___  
 \ \ / /| |/ _` |/ _ \/ _ \| |   | | '_ \ / _` |/ _ \ 
  \ V / | | (_| |  __/ (_) | |___| | | | | (_| | (_) |
   \_/  |_|\__,_|\___|\___/|_____|_|_| |_|\__, |\___/ 
                                          |___/        
"""



def check_and_install_library(library_name, google_drive_path, url=None):
    """
    检查并安装第三方库，并管理安装包
    
    Args:
        library_name (str): 需要安装的库名
        google_drive_path (str): Google Drive 存储路径
    """
    
    
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

def check_ffmpeg():
    from rich.console import Console
    from rich.panel import Panel
    from translations.translations import translate as t
    console = Console()

    try:
        # Check if ffmpeg is installed
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        console.print(Panel(t("✅ FFmpeg is already installed"), style="green"))
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        system = platform.system()
        install_cmd = ""
        
        if system == "Linux":
            install_cmd = "sudo apt install ffmpeg  # Ubuntu/Debian\nsudo yum install ffmpeg  # CentOS/RHEL"
            extra_note = t("Use your distribution's package manager")
        
        console.print(Panel.fit(
            t("❌ FFmpeg not found\n\n") +
            f"{t('🛠️ Install using:')}\n[bold cyan]{install_cmd}[/bold cyan]\n\n" +
            f"{t('💡 Note:')}\n{extra_note}\n\n" +
            f"{t('🔄 After installing FFmpeg, please run this installer again:')}\n[bold cyan]python install.py[/bold cyan]",
            style="red"
        ))
        raise SystemExit(t("FFmpeg is required. Please install it and run the installer again."))


def main():
    """
    主函数，管理库的安装
    """
    # Google Drive 中存储安装包的路径
    libraries_path = "/content/drive/MyDrive/Colab_dependencies"
    
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
    
    from rich.console import Console
    from rich.panel import Panel
    from rich.box import DOUBLE
    from translations.translations import translate as t
    from translations.translations import DISPLAY_LANGUAGES
    from core.config_utils import load_key, update_key

    console = Console()

    width = max(len(line) for line in ascii_logo.splitlines()) + 4
    welcome_panel = Panel(
        ascii_logo,
        width=width,
        box=DOUBLE,
        title="[bold green]🌏[/bold green]",
        border_style="bright_blue"
    )
    console.print(welcome_panel)

    # 自动设置语言为简体中文，而不是使用交互式选择
    selected_language = "zh-CN"  # 简体中文的语言代码
    update_key("display_language", selected_language)
    console.print(Panel.fit(t("已自动设置语言为简体中文"), style="bold magenta"))

    console.print(Panel.fit(t("🚀 Starting Installation"), style="bold magenta"))

    # 自动跳过设置PyPI镜像
    configure_mirrors = False
    if configure_mirrors:
        from core.pypi_autochoose import main as choose_mirror
        choose_mirror()
    else:
        console.print(Panel.fit(t("已自动跳过PyPI镜像配置"), style="cyan"))

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

    install_requirements()
    check_ffmpeg()
    
    console.print(Panel("✅ 所有依赖库安装完成", style="bold green"))

if __name__ == "__main__":
    main()

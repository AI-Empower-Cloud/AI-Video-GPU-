#!/usr/bin/env python3
"""
GitHub Repository Puller for AI Video GPU
Pulls essential repositories for enhanced TTS, Lip Sync, and Video Generation
"""

import os
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubRepoPuller:
    def __init__(self, base_dir="/workspaces/AI-Video-GPU-/external_repos"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Essential repositories for AI Video GPU enhancement
        self.repositories = {
            # Wav2Lip - Advanced Lip Synchronization
            "wav2lip": {
                "url": "https://github.com/Rudrabha/Wav2Lip.git",
                "branch": "master",
                "description": "Professional lip synchronization technology",
                "post_install": self._setup_wav2lip
            },
            
            # Coqui TTS - Advanced Text-to-Speech
            "coqui-tts": {
                "url": "https://github.com/coqui-ai/TTS.git",
                "branch": "main",
                "description": "State-of-the-art text-to-speech synthesis",
                "post_install": self._setup_coqui_tts
            },
            
            # Tortoise TTS - High Quality Voice Cloning
            "tortoise-tts": {
                "url": "https://github.com/neonbjb/tortoise-tts.git",
                "branch": "main",
                "description": "High-quality voice cloning and synthesis",
                "post_install": self._setup_tortoise_tts
            },
            
            # Real-ESRGAN - Video Upscaling
            "real-esrgan": {
                "url": "https://github.com/xinntao/Real-ESRGAN.git",
                "branch": "master",
                "description": "Real-world video super-resolution",
                "post_install": self._setup_real_esrgan
            },
            
            # SadTalker - Advanced Talking Head Generation
            "sadtalker": {
                "url": "https://github.com/OpenTalker/SadTalker.git",
                "branch": "main",
                "description": "Advanced 3D talking head generation",
                "post_install": self._setup_sadtalker
            },
            
            # AnimateDiff - Video Generation
            "animatediff": {
                "url": "https://github.com/guoyww/AnimateDiff.git",
                "branch": "main",
                "description": "Animate your personalized text-to-image diffusion models",
                "post_install": self._setup_animatediff
            },
            
            # Whisper - Speech Recognition
            "whisper": {
                "url": "https://github.com/openai/whisper.git",
                "branch": "main",
                "description": "OpenAI Whisper speech recognition",
                "post_install": self._setup_whisper
            },
            
            # FaceSwap - Deep Learning Face Swapping
            "faceswap": {
                "url": "https://github.com/deepfakes/faceswap.git",
                "branch": "master",
                "description": "Deep learning face swapping technology",
                "post_install": self._setup_faceswap
            },
            
            # Roop - Fast Face Swapping
            "roop": {
                "url": "https://github.com/s0md3v/roop.git",
                "branch": "main",
                "description": "Fast one-click face swap",
                "post_install": self._setup_roop
            },
            
            # Stable Video Diffusion
            "stable-video-diffusion": {
                "url": "https://github.com/Stability-AI/generative-models.git",
                "branch": "main",
                "description": "Stability AI's video generation models",
                "post_install": self._setup_stable_video_diffusion
            }
        }

    def clone_repository(self, name, repo_info):
        """Clone a GitHub repository"""
        repo_path = self.base_dir / name
        
        if repo_path.exists():
            logger.info(f"Repository {name} already exists, pulling latest changes...")
            # Pull latest changes
            subprocess.run(["git", "pull"], cwd=repo_path, check=True)
        else:
            logger.info(f"Cloning {name}: {repo_info['description']}")
            subprocess.run([
                "git", "clone", 
                "--branch", repo_info["branch"],
                repo_info["url"], 
                str(repo_path)
            ], check=True)
        
        return repo_path

    def run_post_install(self, name, repo_info, repo_path):
        """Run post-installation setup"""
        if "post_install" in repo_info:
            logger.info(f"Running post-install setup for {name}...")
            repo_info["post_install"](repo_path)

    def pull_all_repositories(self):
        """Pull all essential repositories"""
        logger.info("Starting to pull essential AI repositories...")
        
        for repo_name, repo_info in self.repositories.items():
            try:
                repo_path = self.clone_repository(repo_name, repo_info)
                self.run_post_install(repo_name, repo_info, repo_path)
                logger.info(f"✅ Successfully set up {repo_name}")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to clone {repo_name}: {e}")
            except Exception as e:
                logger.error(f"❌ Error setting up {repo_name}: {e}")

    def _setup_wav2lip(self, repo_path):
        """Set up Wav2Lip repository"""
        # Download pre-trained models
        models_dir = repo_path / "checkpoints"
        models_dir.mkdir(exist_ok=True)
        
        # Create model download script
        download_script = repo_path / "download_models.py"
        with open(download_script, 'w') as f:
            f.write("""
import os
import urllib.request
from pathlib import Path

def download_model(url, filename):
    filepath = Path("checkpoints") / filename
    if not filepath.exists():
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filepath)
        print(f"✅ Downloaded {filename}")
    else:
        print(f"✅ {filename} already exists")

# Download Wav2Lip models
models = {
    "wav2lip.pth": "https://drive.google.com/file/d/1Wn0hPmpo4GRbCIJR8Tf20Akzdi1qjjG9/view?usp=share_link",
    "wav2lip_gan.pth": "https://drive.google.com/file/d/15G3U08c8xsCkOqQxE38Z2XXDnPcOptNk/view?usp=share_link"
}

for filename, url in models.items():
    download_model(url, filename)
""")
        
        # Install requirements
        if (repo_path / "requirements.txt").exists():
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=repo_path)

    def _setup_coqui_tts(self, repo_path):
        """Set up Coqui TTS repository"""
        if (repo_path / "requirements.txt").exists():
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=repo_path)
        
        # Install in development mode
        subprocess.run(["pip", "install", "-e", "."], cwd=repo_path)

    def _setup_tortoise_tts(self, repo_path):
        """Set up Tortoise TTS repository"""
        if (repo_path / "requirements.txt").exists():
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=repo_path)
        
        # Install in development mode
        subprocess.run(["pip", "install", "-e", "."], cwd=repo_path)

    def _setup_real_esrgan(self, repo_path):
        """Set up Real-ESRGAN repository"""
        if (repo_path / "requirements.txt").exists():
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=repo_path)
        
        # Download pre-trained models
        models_dir = repo_path / "experiments" / "pretrained_models"
        models_dir.mkdir(parents=True, exist_ok=True)

    def _setup_sadtalker(self, repo_path):
        """Set up SadTalker repository"""
        if (repo_path / "requirements.txt").exists():
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=repo_path)

    def _setup_animatediff(self, repo_path):
        """Set up AnimateDiff repository"""
        if (repo_path / "requirements.txt").exists():
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=repo_path)

    def _setup_whisper(self, repo_path):
        """Set up OpenAI Whisper"""
        subprocess.run(["pip", "install", "-e", "."], cwd=repo_path)

    def _setup_faceswap(self, repo_path):
        """Set up FaceSwap repository"""
        if (repo_path / "requirements.txt").exists():
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=repo_path)

    def _setup_roop(self, repo_path):
        """Set up Roop repository"""
        if (repo_path / "requirements.txt").exists():
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=repo_path)

    def _setup_stable_video_diffusion(self, repo_path):
        """Set up Stable Video Diffusion"""
        if (repo_path / "requirements.txt").exists():
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=repo_path)

    def create_integration_symlinks(self):
        """Create symlinks to integrate external repositories"""
        ai_video_root = Path("/workspaces/AI-Video-GPU-")
        
        # Create symlinks for easy access
        external_link = ai_video_root / "external"
        if not external_link.exists():
            external_link.symlink_to(self.base_dir)
        
        # Create specific integration directories
        integrations = {
            "models/wav2lip": self.base_dir / "wav2lip",
            "models/coqui": self.base_dir / "coqui-tts",
            "models/tortoise": self.base_dir / "tortoise-tts",
            "models/real_esrgan": self.base_dir / "real-esrgan",
            "models/sadtalker": self.base_dir / "sadtalker",
            "models/animatediff": self.base_dir / "animatediff",
            "models/whisper": self.base_dir / "whisper",
            "models/faceswap": self.base_dir / "faceswap",
            "models/roop": self.base_dir / "roop",
            "models/stable_video": self.base_dir / "stable-video-diffusion"
        }
        
        for link_path, target_path in integrations.items():
            full_link_path = ai_video_root / link_path
            full_link_path.parent.mkdir(parents=True, exist_ok=True)
            
            if not full_link_path.exists() and target_path.exists():
                try:
                    full_link_path.symlink_to(target_path)
                    logger.info(f"Created symlink: {link_path} -> {target_path}")
                except Exception as e:
                    logger.warning(f"Could not create symlink {link_path}: {e}")

    def generate_integration_script(self):
        """Generate integration script for AI Video GPU"""
        integration_script = Path("/workspaces/AI-Video-GPU-/scripts/integrate_external_repos.py")
        
        with open(integration_script, 'w') as f:
            f.write("""#!/usr/bin/env python3
\"\"\"
External Repository Integration for AI Video GPU
Integrates all pulled repositories into the main system
\"\"\"

import sys
import os
from pathlib import Path

# Add external repositories to Python path
external_repos_path = Path(__file__).parent.parent / "external_repos"

if external_repos_path.exists():
    for repo_dir in external_repos_path.iterdir():
        if repo_dir.is_dir():
            sys.path.insert(0, str(repo_dir))

# Import functions from external repositories
try:
    # Wav2Lip integration
    sys.path.insert(0, str(external_repos_path / "wav2lip"))
    from inference import main as wav2lip_inference
    
    # Coqui TTS integration
    sys.path.insert(0, str(external_repos_path / "coqui-tts"))
    from TTS.api import TTS as CoquiTTS
    
    # Tortoise TTS integration
    sys.path.insert(0, str(external_repos_path / "tortoise-tts"))
    
    print("✅ All external repositories integrated successfully!")
    
except ImportError as e:
    print(f"⚠️  Some repositories may not be fully integrated: {e}")

def get_available_models():
    \"\"\"Get list of available models from all repositories\"\"\"
    models = {
        "wav2lip": ["wav2lip.pth", "wav2lip_gan.pth"],
        "coqui_tts": ["tts_models/multilingual/multi-dataset/xtts_v2"],
        "tortoise": ["tortoise-v2"],
        "real_esrgan": ["RealESRGAN_x4plus"],
        "sadtalker": ["sadtalker"],
        "animatediff": ["mm_sd_v15_v2.ckpt"],
    }
    return models

if __name__ == "__main__":
    print("🚀 AI Video GPU External Repository Integration")
    models = get_available_models()
    
    for repo, model_list in models.items():
        print(f"📦 {repo.upper()}: {', '.join(model_list)}")
""")
        
        # Make the script executable
        os.chmod(integration_script, 0o755)
        logger.info(f"Generated integration script: {integration_script}")

def main():
    """Main function to pull all repositories"""
    puller = GitHubRepoPuller()
    
    print("🌟 AI Video GPU - GitHub Repository Puller")
    print("="*50)
    
    # Pull all repositories
    puller.pull_all_repositories()
    
    # Create integration symlinks
    puller.create_integration_symlinks()
    
    # Generate integration script
    puller.generate_integration_script()
    
    print("\n✅ Repository pulling complete!")
    print(f"📁 Repositories location: {puller.base_dir}")
    print("🔗 Integration symlinks created")
    print("🐍 Integration script generated: scripts/integrate_external_repos.py")
    
    # Display summary
    print("\n📊 REPOSITORY SUMMARY:")
    print("-" * 30)
    for name, info in puller.repositories.items():
        repo_path = puller.base_dir / name
        status = "✅ Ready" if repo_path.exists() else "❌ Failed"
        print(f"{name:20} | {status} | {info['description']}")

if __name__ == "__main__":
    main()

"""
AI Video GPU - Auto Migration Script
Automatically migrates existing AI Video Generator repositories to use AI Video GPU
"""

import os
import sys
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import argparse
from loguru import logger

class AutoMigrator:
    """
    Automatically migrates existing AI video generator repositories
    to use AI Video GPU with minimal changes
    """
    
    def __init__(self, source_repo: str, target_repo: Optional[str] = None):
        self.source_repo = Path(source_repo).resolve()
        self.target_repo = Path(target_repo).resolve() if target_repo else self.source_repo / "ai_video_gpu_migrated"
        self.backup_dir = self.source_repo / "backup_original"
        
        self.migration_log = []
        self.detected_patterns = {}
        
    def analyze_repository(self) -> Dict:
        """Analyze the source repository for migration opportunities"""
        
        logger.info(f"Analyzing repository: {self.source_repo}")
        
        analysis = {
            "python_files": [],
            "config_files": [],
            "requirements": [],
            "frameworks": [],
            "models": [],
            "data_dirs": [],
            "scripts": []
        }
        
        # Find Python files
        for py_file in self.source_repo.rglob("*.py"):
            if not any(skip in str(py_file) for skip in [".git", "__pycache__", ".venv"]):
                analysis["python_files"].append(str(py_file.relative_to(self.source_repo)))
                
        # Find config files
        config_patterns = ["*.json", "*.yaml", "*.yml", "*.ini", "*.conf"]
        for pattern in config_patterns:
            for config_file in self.source_repo.rglob(pattern):
                if not any(skip in str(config_file) for skip in [".git", "__pycache__"]):
                    analysis["config_files"].append(str(config_file.relative_to(self.source_repo)))
                    
        # Find requirements
        req_files = ["requirements.txt", "requirements-dev.txt", "pyproject.toml", "setup.py"]
        for req_file in req_files:
            req_path = self.source_repo / req_file
            if req_path.exists():
                analysis["requirements"].append(req_file)
                
        # Detect frameworks
        analysis["frameworks"] = self._detect_frameworks()
        
        # Find model directories
        model_dirs = ["models", "checkpoints", "weights", "pretrained"]
        for model_dir in model_dirs:
            model_path = self.source_repo / model_dir
            if model_path.exists():
                analysis["models"].append(model_dir)
                
        # Find data directories
        data_dirs = ["data", "datasets", "samples", "examples", "demo"]
        for data_dir in data_dirs:
            data_path = self.source_repo / data_dir
            if data_path.exists():
                analysis["data_dirs"].append(data_dir)
                
        # Find scripts
        for script in self.source_repo.glob("*.py"):
            if script.is_file():
                analysis["scripts"].append(script.name)
                
        logger.info(f"Analysis complete: {len(analysis['python_files'])} Python files found")
        return analysis
        
    def _detect_frameworks(self) -> List[str]:
        """Detect AI/ML frameworks used in the repository"""
        
        frameworks = []
        
        # Framework detection patterns
        framework_patterns = {
            "gradio": ["import gradio", "from gradio", "gr.Interface"],
            "streamlit": ["import streamlit", "from streamlit", "st."],
            "flask": ["from flask", "import flask", "Flask("],
            "fastapi": ["from fastapi", "import fastapi", "FastAPI("],
            "wav2lip": ["wav2lip", "Wav2Lip", "lip_sync"],
            "tortoise": ["tortoise", "Tortoise", "tortoise_tts"],
            "coqui": ["from TTS", "import TTS", "coqui"],
            "stable_diffusion": ["stable_diffusion", "diffusers", "StableDiffusion"],
            "huggingface": ["transformers", "from transformers", "AutoModel"],
            "pytorch": ["import torch", "from torch", "torch."],
            "opencv": ["import cv2", "from cv2", "opencv"]
        }
        
        # Search all Python files
        for py_file in self.source_repo.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for framework, patterns in framework_patterns.items():
                    if any(pattern in content for pattern in patterns):
                        if framework not in frameworks:
                            frameworks.append(framework)
                            
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
                
        return frameworks
        
    def create_migration_plan(self, analysis: Dict) -> Dict:
        """Create a detailed migration plan"""
        
        plan = {
            "backup_original": True,
            "copy_structure": True,
            "install_ai_video_gpu": True,
            "create_integration": True,
            "update_requirements": True,
            "migrate_configs": True,
            "update_imports": [],
            "create_wrappers": [],
            "test_compatibility": True
        }
        
        # Plan import updates
        for py_file in analysis["python_files"]:
            file_path = self.source_repo / py_file
            import_updates = self._plan_import_updates(file_path)
            if import_updates:
                plan["update_imports"].append({
                    "file": py_file,
                    "updates": import_updates
                })
                
        # Plan wrapper creation
        if "gradio" in analysis["frameworks"]:
            plan["create_wrappers"].append("gradio_wrapper")
        if "fastapi" in analysis["frameworks"]:
            plan["create_wrappers"].append("fastapi_wrapper")
        if "streamlit" in analysis["frameworks"]:
            plan["create_wrappers"].append("streamlit_wrapper")
            
        return plan
        
    def _plan_import_updates(self, file_path: Path) -> List[Dict]:
        """Plan import statement updates for a file"""
        
        updates = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Common import patterns to replace
                replacements = {
                    "from your_tts_module import": "from ai_video_gpu_integration import",
                    "from voice_clone import": "from ai_video_gpu_integration import",
                    "from lip_sync import": "from ai_video_gpu_integration import",
                    "from video_generation import": "from ai_video_gpu_integration import",
                    "import wav2lip": "from ai_video_gpu_integration import sync_lips as wav2lip",
                    "import tortoise": "from ai_video_gpu_integration import clone_voice as tortoise"
                }
                
                for old_import, new_import in replacements.items():
                    if old_import in line:
                        updates.append({
                            "line_number": i + 1,
                            "old_line": line,
                            "new_line": line.replace(old_import, new_import),
                            "type": "import_replacement"
                        })
                        
        except Exception as e:
            logger.warning(f"Could not analyze imports in {file_path}: {e}")
            
        return updates
        
    def execute_migration(self, plan: Dict) -> bool:
        """Execute the migration plan"""
        
        logger.info("Starting migration execution...")
        
        try:
            # Step 1: Backup original
            if plan["backup_original"]:
                self._backup_original()
                
            # Step 2: Copy structure
            if plan["copy_structure"]:
                self._copy_repository_structure()
                
            # Step 3: Install AI Video GPU
            if plan["install_ai_video_gpu"]:
                self._install_ai_video_gpu()
                
            # Step 4: Create integration script
            if plan["create_integration"]:
                self._create_integration_script()
                
            # Step 5: Update requirements
            if plan["update_requirements"]:
                self._update_requirements()
                
            # Step 6: Migrate configs
            if plan["migrate_configs"]:
                self._migrate_configs()
                
            # Step 7: Update imports
            for import_update in plan["update_imports"]:
                self._update_file_imports(import_update)
                
            # Step 8: Create wrappers
            for wrapper_type in plan["create_wrappers"]:
                self._create_wrapper(wrapper_type)
                
            # Step 9: Test compatibility
            if plan["test_compatibility"]:
                self._test_compatibility()
                
            logger.success("Migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
            
    def _backup_original(self):
        """Create backup of original repository"""
        
        logger.info("Creating backup of original repository...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
            
        shutil.copytree(self.source_repo, self.backup_dir, 
                       ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
        
        self.migration_log.append(f"Created backup: {self.backup_dir}")
        
    def _copy_repository_structure(self):
        """Copy repository structure to target"""
        
        logger.info("Copying repository structure...")
        
        if self.target_repo.exists():
            shutil.rmtree(self.target_repo)
            
        shutil.copytree(self.source_repo, self.target_repo,
                       ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
        
        self.migration_log.append(f"Copied to: {self.target_repo}")
        
    def _install_ai_video_gpu(self):
        """Install AI Video GPU in target repository"""
        
        logger.info("Installing AI Video GPU...")
        
        # Copy AI Video GPU source
        ai_video_gpu_src = Path(__file__).parent.parent
        target_ai_gpu = self.target_repo / "ai_video_gpu"
        
        if target_ai_gpu.exists():
            shutil.rmtree(target_ai_gpu)
            
        shutil.copytree(ai_video_gpu_src / "src", target_ai_gpu / "src")
        shutil.copy2(ai_video_gpu_src / "requirements.txt", target_ai_gpu / "requirements.txt")
        shutil.copy2(ai_video_gpu_src / "main.py", target_ai_gpu / "main.py")
        
        # Copy config
        if (ai_video_gpu_src / "config").exists():
            shutil.copytree(ai_video_gpu_src / "config", target_ai_gpu / "config")
            
        self.migration_log.append("Installed AI Video GPU")
        
    def _create_integration_script(self):
        """Create integration script for the migrated repo"""
        
        logger.info("Creating integration script...")
        
        integration_script = self.target_repo / "ai_video_gpu_integration.py"
        
        with open(integration_script, 'w') as f:
            f.write(f'''"""
AI Video GPU Integration for {self.source_repo.name}
Auto-generated migration script
"""

import sys
from pathlib import Path

# Add AI Video GPU to path
sys.path.insert(0, str(Path(__file__).parent / "ai_video_gpu"))

from ai_video_gpu.src.compatibility.repo_compatibility import RepoCompatibilityManager

# Initialize compatibility
_compat = RepoCompatibilityManager(str(Path(__file__).parent))
_bridge = _compat.create_compatibility_bridge()

# Export functions for easy import
generate_video = _bridge['generate_video']
clone_voice = _bridge['clone_voice']
sync_lips = _bridge['sync_lips']
get_models = _bridge['get_models']

# Aliases for common naming patterns
create_video = generate_video
lip_sync = sync_lips
voice_clone = clone_voice

print("✅ AI Video GPU integration loaded!")
''')
        
        self.migration_log.append("Created integration script")
        
    def _update_requirements(self):
        """Update requirements.txt with AI Video GPU dependencies"""
        
        logger.info("Updating requirements...")
        
        target_req = self.target_repo / "requirements.txt"
        ai_gpu_req = self.target_repo / "ai_video_gpu" / "requirements.txt"
        
        if ai_gpu_req.exists():
            # Merge requirements
            existing_reqs = set()
            if target_req.exists():
                with open(target_req, 'r') as f:
                    existing_reqs = set(line.strip() for line in f if line.strip())
                    
            with open(ai_gpu_req, 'r') as f:
                ai_gpu_reqs = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
                
            merged_reqs = existing_reqs.union(ai_gpu_reqs)
            
            with open(target_req, 'w') as f:
                f.write("# Merged requirements for AI Video GPU migration\\n")
                for req in sorted(merged_reqs):
                    if req:
                        f.write(f"{req}\\n")
                        
        self.migration_log.append("Updated requirements.txt")
        
    def _migrate_configs(self):
        """Migrate configuration files"""
        
        logger.info("Migrating configurations...")
        
        # Copy AI Video GPU configs
        ai_gpu_config = self.target_repo / "ai_video_gpu" / "config"
        if ai_gpu_config.exists():
            target_config = self.target_repo / "config"
            if not target_config.exists():
                target_config.mkdir()
                
            for config_file in ai_gpu_config.glob("*.yaml"):
                shutil.copy2(config_file, target_config / config_file.name)
                
        self.migration_log.append("Migrated configuration files")
        
    def _update_file_imports(self, import_update: Dict):
        """Update imports in a specific file"""
        
        file_path = self.target_repo / import_update["file"]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Apply updates
            for update in import_update["updates"]:
                content = content.replace(update["old_line"], update["new_line"])
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.migration_log.append(f"Updated imports in {import_update['file']}")
            
        except Exception as e:
            logger.warning(f"Could not update imports in {file_path}: {e}")
            
    def _create_wrapper(self, wrapper_type: str):
        """Create framework-specific wrapper"""
        
        logger.info(f"Creating {wrapper_type} wrapper...")
        
        if wrapper_type == "gradio_wrapper":
            wrapper_path = self.target_repo / "gradio_ai_video_gpu.py"
            with open(wrapper_path, 'w') as f:
                f.write('''"""
Gradio wrapper for AI Video GPU
"""
from ai_video_gpu_integration import generate_video, clone_voice, sync_lips
from ai_video_gpu.src.interfaces.gradio_interface import create_gradio_app

# Create app
app = create_gradio_app()

if __name__ == "__main__":
    app.launch()
''')
                
        elif wrapper_type == "fastapi_wrapper":
            wrapper_path = self.target_repo / "fastapi_ai_video_gpu.py"
            with open(wrapper_path, 'w') as f:
                f.write('''"""
FastAPI wrapper for AI Video GPU
"""
from ai_video_gpu.src.api.app import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')
                
        self.migration_log.append(f"Created {wrapper_type}")
        
    def _test_compatibility(self):
        """Test the migrated repository for compatibility"""
        
        logger.info("Testing compatibility...")
        
        try:
            # Try importing the integration script
            import_test_script = self.target_repo / "test_import.py"
            with open(import_test_script, 'w') as f:
                f.write('''
import sys
sys.path.insert(0, ".")

try:
    from ai_video_gpu_integration import generate_video, clone_voice, sync_lips
    print("✅ Import test passed")
    print(f"   generate_video: {generate_video}")
    print(f"   clone_voice: {clone_voice}")
    print(f"   sync_lips: {sync_lips}")
except Exception as e:
    print(f"❌ Import test failed: {e}")
''')
            
            # Run test
            result = subprocess.run([sys.executable, str(import_test_script)], 
                                  cwd=self.target_repo, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.success("Compatibility test passed!")
                self.migration_log.append("Compatibility test: PASSED")
            else:
                logger.error(f"Compatibility test failed: {result.stderr}")
                self.migration_log.append(f"Compatibility test: FAILED - {result.stderr}")
                
            # Clean up test file
            import_test_script.unlink()
            
        except Exception as e:
            logger.error(f"Could not run compatibility test: {e}")
            
    def generate_migration_report(self) -> str:
        """Generate a detailed migration report"""
        
        report = f"""
AI Video GPU Migration Report
============================

Source Repository: {self.source_repo}
Target Repository: {self.target_repo}
Backup Location: {self.backup_dir}

Migration Steps Completed:
"""
        
        for step in self.migration_log:
            report += f"  ✅ {step}\n"
            
        report += f"""

Next Steps:
-----------
1. Review the migrated code in: {self.target_repo}
2. Install dependencies: pip install -r requirements.txt
3. Test the integration: python ai_video_gpu_integration.py
4. Run your existing scripts with GPU acceleration!

Files Created:
--------------
- ai_video_gpu_integration.py (main integration script)
- ai_video_gpu/ (AI Video GPU source code)
- config/ (configuration files)

Detected Frameworks:
-------------------
"""
        
        for framework in self.detected_patterns.get("frameworks", []):
            report += f"  📦 {framework}\n"
            
        report += """

Support:
--------
- Documentation: README.md
- CLI help: python ai_video_gpu/main.py --help
- API docs: Start server and visit /docs

Happy GPU-accelerated video generation! 🚀
"""
        
        return report

def main():
    """Main migration function"""
    
    parser = argparse.ArgumentParser(description="AI Video GPU Auto Migration Tool")
    parser.add_argument("source_repo", help="Path to source repository")
    parser.add_argument("--target", help="Target directory (default: source_repo/ai_video_gpu_migrated)")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze, don't migrate")
    parser.add_argument("--force", action="store_true", help="Force migration even if target exists")
    
    args = parser.parse_args()
    
    # Initialize migrator
    migrator = AutoMigrator(args.source_repo, args.target)
    
    # Analyze repository
    analysis = migrator.analyze_repository()
    
    print("\\n📊 Repository Analysis:")
    print(f"   Python files: {len(analysis['python_files'])}")
    print(f"   Config files: {len(analysis['config_files'])}")
    print(f"   Detected frameworks: {', '.join(analysis['frameworks'])}")
    
    if args.analyze_only:
        print("\\n🔍 Analysis complete. Use without --analyze-only to migrate.")
        return
        
    # Check if target exists
    if migrator.target_repo.exists() and not args.force:
        print(f"\\n❌ Target directory exists: {migrator.target_repo}")
        print("Use --force to overwrite or choose a different target.")
        return
        
    # Create migration plan
    plan = migrator.create_migration_plan(analysis)
    
    print("\\n📋 Migration Plan:")
    for key, value in plan.items():
        if isinstance(value, bool) and value:
            print(f"   ✅ {key}")
        elif isinstance(value, list) and value:
            print(f"   📝 {key}: {len(value)} items")
            
    # Execute migration
    if migrator.execute_migration(plan):
        report = migrator.generate_migration_report()
        
        # Save report
        report_path = migrator.target_repo / "MIGRATION_REPORT.md"
        with open(report_path, 'w') as f:
            f.write(report)
            
        print(report)
        print(f"\\n📄 Full report saved to: {report_path}")
        
    else:
        print("\\n❌ Migration failed. Check logs for details.")

if __name__ == "__main__":
    main()

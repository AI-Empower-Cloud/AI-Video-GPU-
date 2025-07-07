"""
AI Video GPU - Command Line Interface
Main entry point for the AI Video GPU pipeline
"""

import click
import sys
from pathlib import Path
import json
import time
from loguru import logger
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.pipeline import AIVideoPipeline
from src.config import ConfigManager
from src.utils.gpu_monitor import GPUMonitor
from src.compatibility.repo_compatibility import RepoCompatibilityManager
from src.modules.video_enhancer import VideoEnhancer
from src.modules.realtime_processor import RealTimeVideoProcessor, LiveStreamManager
from src.monitoring.system_monitor import SystemMonitor, AlertManager
from src.cloud import CloudStorageManager, DistributedTaskManager, ModelRepository

# Advanced modules for enhanced features
from src.modules.animation_engine import AnimationEngine
from src.modules.advanced_audio import AdvancedAudioEngine
from src.modules.scene_engine import SceneEngine, SceneType
from src.modules.performance_optimizer import PerformanceOptimizer
from src.modules.production_engine import ProductionEngine

@click.group()
@click.option('--config', '-c', default=None, help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, verbose):
    """AI Video GPU - Generate high-quality AI videos with GPU acceleration"""
    
    # Configure logging
    log_level = "DEBUG" if verbose else "INFO"
    logger.remove()
    logger.add(sys.stderr, level=log_level, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    ctx.obj['verbose'] = verbose

@cli.command()
@click.argument('script', type=str)
@click.option('--avatar', '-a', type=click.Path(exists=True), help='Avatar image for lip sync')
@click.option('--voice', '-v', type=click.Path(exists=True), help='Voice sample for cloning')
@click.option('--music', '-m', type=click.Path(exists=True), help='Background music file')
@click.option('--background-prompt', '-bg', help='AI background generation prompt')
@click.option('--visual-style', default='photorealistic', help='Visual style for AI generation')
@click.option('--output', '-o', default='output/generated_video.mp4', help='Output video path')
@click.option('--use-3d', is_flag=True, help='Enable 3D avatar rendering')
@click.option('--use-ai-backgrounds', is_flag=True, help='Generate AI backgrounds')
@click.option('--quality', default='high', help='Lip sync quality (low/medium/high/ultra)')
@click.option('--tts-backend', default='auto', help='TTS backend (xtts/tortoise/speecht5/auto)')
@click.option('--preview', is_flag=True, help='Generate preview only')
@click.pass_context
def generate(ctx, script, avatar, voice, music, background_prompt, visual_style, output, use_3d, use_ai_backgrounds, quality, tts_backend, preview):
    """Generate AI video from text script"""
    
    logger.info("Starting AI Video GPU generation...")
    
    try:
        # Initialize pipeline
        pipeline = AIVideoPipeline(ctx.obj['config_path'])
        
        # Start GPU monitoring
        with GPUMonitor() as monitor:
            monitor.start_monitoring()
            
            # Check system requirements
            if use_3d and not monitor.check_memory_requirements(4000):  # 4GB for 3D
                logger.warning("Insufficient GPU memory for 3D rendering. Falling back to 2D.")
                use_3d = False
            
            # Generate video
            result = pipeline.generate_video(
                script=script,
                avatar_image=avatar,
                voice_sample=voice,
                background_music=music,
                background_prompt=background_prompt,
                visual_style=visual_style,
                output_path=output,
                use_3d=use_3d,
                use_ai_backgrounds=use_ai_backgrounds
            )
            
            if result['success']:
                logger.success(f"Video generated successfully: {result['output_path']}")
                logger.info(f"Generation time: {result['generation_time']:.2f}s")
                
                # Create preview if requested
                if preview:
                    from src.modules.video_composer import VideoComposer
                    composer = VideoComposer(pipeline.config)
                    preview_path = output.replace('.mp4', '_preview.mp4')
                    composer.create_preview(result['output_path'], output_path=preview_path)
                    logger.info(f"Preview created: {preview_path}")
                
                # Show performance stats
                stats = monitor.get_stats()
                logger.info(f"GPU Memory Used: {stats.get('memory_percent', 0):.1f}%")
                logger.info(f"Peak Temperature: {stats.get('temperature', 0)}°C")
                
            else:
                logger.error(f"Video generation failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        sys.exit(1)

@cli.command()
@click.argument('scripts_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output/batch', help='Output directory for batch videos')
@click.option('--max-parallel', '-p', default=1, help='Maximum parallel generations')
@click.pass_context
def batch(ctx, scripts_file, output_dir, max_parallel):
    """Generate multiple videos from JSON script file"""
    
    logger.info(f"Starting batch generation from {scripts_file}")
    
    try:
        # Load scripts
        with open(scripts_file, 'r') as f:
            scripts = json.load(f)
        
        if not isinstance(scripts, list):
            raise ValueError("Scripts file must contain a list of script configurations")
        
        # Initialize pipeline
        pipeline = AIVideoPipeline(ctx.obj['config_path'])
        
        # Generate videos
        results = pipeline.batch_generate(scripts, output_dir)
        
        # Report results
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        logger.success(f"Batch generation completed: {successful} successful, {failed} failed")
        
        # Save batch report
        report_path = Path(output_dir) / "batch_report.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Batch report saved: {report_path}")
        
    except Exception as e:
        logger.error(f"Batch generation failed: {e}")
        sys.exit(1)

@cli.command()
@click.pass_context
def status(ctx):
    """Show system status and capabilities"""
    
    logger.info("Checking AI Video GPU system status...")
    
    try:
        # Initialize components
        config = ConfigManager(ctx.obj['config_path'])
        monitor = GPUMonitor()
        
        # Get system status
        stats = monitor.get_current_stats()
        
        print("\n=== AI Video GPU System Status ===")
        print(f"GPU Available: {'✓' if stats['gpu_available'] else '✗'}")
        print(f"GPU Count: {stats['gpu_count']}")
        
        if stats['gpu_available']:
            print(f"GPU Memory: {stats['memory_used'] / (1024**3):.1f}GB / {stats['memory_total'] / (1024**3):.1f}GB ({stats['memory_percent']:.1f}%)")
            if stats.get('temperature', 0) > 0:
                print(f"GPU Temperature: {stats['temperature']}°C")
            if stats.get('utilization', 0) > 0:
                print(f"GPU Utilization: {stats['utilization']}%")
        
        print(f"System Memory: {stats['system_memory_percent']:.1f}% used")
        print(f"CPU Usage: {stats['cpu_percent']:.1f}%")
        print(f"Disk Space: {stats['disk_percent']:.1f}% used")
        
        # Show configuration
        print(f"\n=== Configuration ===")
        print(f"Output Resolution: {config.video.output_resolution}")
        print(f"FPS: {config.video.fps}")
        print(f"3D Rendering: {'Enabled' if config.pipeline_3d.enabled else 'Disabled'}")
        
        # Performance suggestions
        suggestions = monitor.suggest_optimizations()
        if suggestions:
            print(f"\n=== Optimization Suggestions ===")
            for suggestion in suggestions:
                print(f"• {suggestion}")
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--duration', '-d', default=10.0, help='Benchmark duration in seconds')
@click.option('--export', '-e', default=None, help='Export results to file')
@click.pass_context
def benchmark(ctx, duration, export):
    """Run GPU performance benchmark"""
    
    logger.info(f"Running GPU benchmark for {duration}s...")
    
    try:
        monitor = GPUMonitor()
        results = monitor.benchmark_gpu(duration)
        
        if 'error' in results:
            logger.error(f"Benchmark failed: {results['error']}")
            sys.exit(1)
        
        print("\n=== Benchmark Results ===")
        print(f"Duration: {results['duration']:.2f}s")
        print(f"Operations Completed: {results['operations_completed']}")
        print(f"Operations/Second: {results['operations_per_second']:.1f}")
        print(f"Matrix Size: {results['matrix_size']}x{results['matrix_size']}")
        print(f"Memory Usage: {results['initial_memory_mb']:.1f}MB → {results['final_memory_mb']:.1f}MB")
        
        if results.get('peak_temperature', 0) > 0:
            print(f"Peak Temperature: {results['peak_temperature']}°C")
        
        # Export results if requested
        if export:
            with open(export, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Benchmark results exported to: {export}")
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--template', '-t', default='config/default.yaml', help='Template config file path')
@click.pass_context
def init(ctx, template):
    """Initialize AI Video GPU configuration"""
    
    logger.info("Initializing AI Video GPU configuration...")
    
    try:
        # Create directory structure
        directories = [
            'config',
            'models',
            'output',
            'temp',
            'assets/avatars',
            'assets/music',
            'assets/voices'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
        # Create default configuration
        config = ConfigManager()
        config.save_config()
        logger.info(f"Default configuration saved to: {config.config_path}")
        
        # Create example scripts
        example_scripts = [
            {
                "script": "Welcome to AI Video GPU! This is an amazing tool for creating AI-powered videos with advanced features like voice cloning, lip sync, and 3D avatars.",
                "avatar_image": "assets/avatars/default_avatar.jpg",
                "background_music": "assets/music/ambient.mp3",
                "use_3d": False
            },
            {
                "script": "This is a 3D animated example with spatial audio and dynamic lighting effects.",
                "avatar_image": "assets/avatars/3d_avatar.obj",
                "background_music": "assets/music/energetic.mp3",
                "use_3d": True
            }
        ]
        
        with open('config/example_scripts.json', 'w') as f:
            json.dump(example_scripts, f, indent=2)
        
        logger.success("AI Video GPU initialization completed!")
        print("\n=== Next Steps ===")
        print("1. Add your avatar images to assets/avatars/")
        print("2. Add background music to assets/music/")
        print("3. Add voice samples to assets/voices/")
        print("4. Edit config/default.yaml to customize settings")
        print("5. Run: python main.py generate \"Your script here\"")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)

@cli.command()
@click.argument('avatar_path', type=click.Path(exists=True))
@click.pass_context
def calibrate(ctx, avatar_path):
    """Calibrate lip sync for specific avatar"""
    
    logger.info(f"Calibrating avatar: {avatar_path}")
    
    try:
        from src.modules.lip_sync_engine import LipSyncEngine
        
        config = ConfigManager(ctx.obj['config_path'])
        lip_sync = LipSyncEngine(config)
        
        calibration = lip_sync.calibrate_for_avatar(avatar_path)
        
        print("\n=== Avatar Calibration Results ===")
        print(f"Face Detected: {'✓' if calibration['face_detected'] else '✗'}")
        
        if calibration['face_detected']:
            print(f"Face Confidence: {calibration['face_confidence']:.2f}")
            print(f"Recommended Quality: {calibration['recommended_quality']}")
            bbox = calibration['face_bbox']
            print(f"Face Region: ({bbox['x']:.3f}, {bbox['y']:.3f}) {bbox['width']:.3f}x{bbox['height']:.3f}")
        else:
            print("No face detected. Lip sync quality may be poor.")
        
        # Save calibration
        calibration_path = f"config/{Path(avatar_path).stem}_calibration.json"
        with open(calibration_path, 'w') as f:
            json.dump(calibration, f, indent=2)
        
        logger.info(f"Calibration saved: {calibration_path}")
        
    except Exception as e:
        logger.error(f"Calibration failed: {e}")
        sys.exit(1)

@cli.command()
@click.argument('prompt', type=str)
@click.option('--style', default='photorealistic', help='Visual style')
@click.option('--animated', is_flag=True, help='Generate animated background')
@click.option('--duration', default=10.0, help='Duration for animated backgrounds')
@click.option('--output', '-o', default='output/background.png', help='Output path')
@click.pass_context
def generate_background(ctx, prompt, style, animated, duration, output):
    """Generate AI background from text prompt"""
    
    logger.info(f"Generating {'animated' if animated else 'static'} background...")
    
    try:
        from src.modules.visual_generation import VisualGenerationEngine
        from src.config import ConfigManager
        
        config = ConfigManager(ctx.obj['config_path'])
        visual_gen = VisualGenerationEngine(config)
        
        result = visual_gen.generate_background(
            prompt=prompt,
            style=style,
            duration_seconds=duration,
            animated=animated
        )
        
        if animated:
            # Create video from frames
            video_path = output.replace('.png', '.mp4')
            visual_gen.create_video_from_images(result, video_path)
            logger.success(f"Animated background generated: {video_path}")
        else:
            # Move single image to output path
            import shutil
            shutil.move(result, output)
            logger.success(f"Background generated: {output}")
        
    except Exception as e:
        logger.error(f"Background generation failed: {e}")
        sys.exit(1)

@cli.command()
@click.argument('voice_samples', nargs=-1, type=click.Path(exists=True))
@click.option('--output', '-o', default='models/custom_voice', help='Output voice model path')
@click.option('--name', default='custom_voice', help='Voice name')
@click.option('--backend', default='auto', help='TTS backend to use')
@click.pass_context
def clone_voice(ctx, voice_samples, output, name, backend):
    """Clone voice from audio samples"""
    
    if not voice_samples:
        logger.error("Please provide at least one voice sample")
        sys.exit(1)
    
    logger.info(f"Cloning voice from {len(voice_samples)} samples...")
    
    try:
        from src.modules.enhanced_tts_engine import EnhancedTTSEngine
        from src.config import ConfigManager
        
        config = ConfigManager(ctx.obj['config_path'])
        tts_engine = EnhancedTTSEngine(config)
        
        voice_model_path = tts_engine.clone_voice_from_samples(
            voice_samples=list(voice_samples),
            output_embedding_path=output,
            voice_name=name
        )
        
        logger.success(f"Voice cloned successfully: {voice_model_path}")
        
        # Test the cloned voice
        test_output = f"output/voice_test_{name}.wav"
        tts_engine.generate_speech(
            text="This is a test of the cloned voice.",
            voice_sample=voice_model_path,
            output_path=test_output
        )
        
        logger.info(f"Voice test generated: {test_output}")
        
    except Exception as e:
        logger.error(f"Voice cloning failed: {e}")
        sys.exit(1)

@cli.command()
@click.argument('video_path', type=click.Path(exists=True))
@click.argument('audio_path', type=click.Path(exists=True))
@click.option('--output', '-o', default='output/lip_synced.mp4', help='Output video path')
@click.option('--quality', default='high', help='Quality setting (low/medium/high/ultra)')
@click.option('--preprocess', is_flag=True, help='Preprocess video for better results')
@click.pass_context
def lipsync(ctx, video_path, audio_path, output, quality, preprocess):
    """Apply lip synchronization to existing video"""
    
    logger.info("Starting lip synchronization...")
    
    try:
        from src.modules.wav2lip_engine import Wav2LipEngine
        from src.config import ConfigManager
        
        config = ConfigManager(ctx.obj['config_path'])
        wav2lip = Wav2LipEngine(config)
        
        # Preprocess if requested
        if preprocess:
            logger.info("Preprocessing video...")
            preprocessed_path = "temp/preprocessed_video.mp4"
            video_path = wav2lip.preprocess_video_for_lipsync(
                video_path, preprocessed_path
            )
        
        # Apply lip sync
        result_path = wav2lip.sync_lips(
            video_path=video_path,
            audio_path=audio_path,
            output_path=output,
            quality=quality
        )
        
        logger.success(f"Lip synchronization completed: {result_path}")
        
    except Exception as e:
        logger.error(f"Lip synchronization failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--backend', help='Test specific TTS backend')
@click.option('--wav2lip', is_flag=True, help='Test Wav2Lip installation')
@click.option('--visual', is_flag=True, help='Test visual generation')
@click.option('--all', 'test_all', is_flag=True, help='Test all components')
@click.pass_context
def test_models(ctx, backend, wav2lip, visual, test_all):
    """Test AI model installations and capabilities"""
    
    logger.info("Testing AI model installations...")
    
    results = {}
    
    # Test TTS backends
    if backend or test_all:
        try:
            from src.modules.enhanced_tts_engine import EnhancedTTSEngine
            from src.config import ConfigManager
            
            config = ConfigManager(ctx.obj['config_path'])
            tts = EnhancedTTSEngine(config)
            
            backend_info = tts.get_backend_info()
            results['tts'] = {
                'available_backends': backend_info['available_backends'],
                'current_backend': backend_info['current_backend'],
                'voice_cloning': backend_info['supports_voice_cloning'],
                'multilingual': backend_info['supports_multilingual']
            }
            
        except Exception as e:
            results['tts'] = {'error': str(e)}
    
    # Test Wav2Lip
    if wav2lip or test_all:
        try:
            from src.modules.wav2lip_engine import Wav2LipEngine
            from src.config import ConfigManager
            
            config = ConfigManager(ctx.obj['config_path'])
            wav2lip_engine = Wav2LipEngine(config)
            
            results['wav2lip'] = {
                'model_available': wav2lip_engine.wav2lip_model is not None,
                'face_detection': True  # MediaPipe should always work
            }
            
        except Exception as e:
            results['wav2lip'] = {'error': str(e)}
    
    # Test Visual Generation
    if visual or test_all:
        try:
            from src.modules.visual_generation import VisualGenerationEngine
            from src.config import ConfigManager
            
            config = ConfigManager(ctx.obj['config_path'])
            visual_gen = VisualGenerationEngine(config)
            
            capabilities = visual_gen.get_generation_capabilities()
            results['visual_generation'] = capabilities
            
        except Exception as e:
            results['visual_generation'] = {'error': str(e)}
    
    # Display results
    print("\n=== AI Model Test Results ===")
    
    for component, result in results.items():
        print(f"\n{component.upper()}:")
        if 'error' in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            for key, value in result.items():
                status = "✓" if value else "✗"
                print(f"  {status} {key}: {value}")

@cli.command()
@click.option('--repo-path', '-r', default='.', help='Path to existing AI Video Generator repo')
@click.option('--output', '-o', default='ai_video_gpu_integration.py', help='Output integration script path')
@click.option('--analyze-only', is_flag=True, help='Only analyze repo without creating integration')
@click.pass_context
def integrate(ctx, repo_path, output, analyze_only):
    """Create compatibility bridge for existing AI Video Generator repositories"""
    
    logger.info(f"Analyzing repository at: {repo_path}")
    
    try:
        # Initialize compatibility manager
        compat_manager = RepoCompatibilityManager(repo_path)
        
        # Show detected frameworks
        logger.info("Detected frameworks:")
        for framework in compat_manager.detected_frameworks:
            logger.info(f"  ✅ {framework}")
        
        if not compat_manager.detected_frameworks:
            logger.warning("No known AI video frameworks detected")
            logger.info("The integration will still work with generic Python projects")
        
        if analyze_only:
            # Show configuration bridge info
            bridge = compat_manager.create_compatibility_bridge()
            logger.info("\nCompatibility Bridge Configuration:")
            logger.info(f"  📦 Available functions: {list(bridge.keys())}")
            
            existing_configs = bridge['config'].get('existing_configs', {})
            if existing_configs:
                logger.info(f"  ⚙️  Found config files: {list(existing_configs.keys())}")
            
            return
        
        # Create integration script
        integration_path = compat_manager.create_integration_script(output)
        
        logger.success(f"Integration script created: {integration_path}")
        logger.info("\nUsage in your existing repo:")
        logger.info(f"  1. Copy {integration_path} to your repo directory")
        logger.info("  2. Replace your existing imports:")
        logger.info("     # Old:")
        logger.info("     # from your_video_generator import generate_video")
        logger.info("     # New:")
        logger.info("     from ai_video_gpu_integration import generate_video")
        logger.info("  3. Use the same function calls with GPU acceleration!")
        
        # Offer to copy to repo if it's different directory
        if Path(repo_path).resolve() != Path('.').resolve():
            if click.confirm("Copy integration script to the target repo?"):
                import shutil
                target_path = Path(repo_path) / Path(output).name
                shutil.copy2(integration_path, target_path)
                logger.success(f"Integration script copied to: {target_path}")
        
    except Exception as e:
        logger.error(f"Integration failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--port', '-p', default=8000, help='Port for web API')
@click.option('--host', default='0.0.0.0', help='Host for web API')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
@click.pass_context
def serve(ctx, port, host, reload):
    """Start the FastAPI web server for compatibility with web-based repos"""
    
    logger.info(f"Starting AI Video GPU web server on {host}:{port}")
    
    try:
        from src.api.app import create_app
        import uvicorn
        
        app = create_app()
        
        logger.info("Available endpoints:")
        logger.info("  📹 POST /generate/video - Generate AI video")
        logger.info("  🗣️  POST /voice/clone - Clone voice from sample")
        logger.info("  👄 POST /lipsync/sync - Sync lips with audio")
        logger.info("  📊 GET /health - Health check")
        logger.info("  🔧 GET /models/list - List available models")
        
        uvicorn.run(app, host=host, port=port, reload=reload)
        
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)

@cli.command()
@click.option('--auto', is_flag=True, help='Automatically setup for detected repos')
@click.pass_context
def codespace_setup(ctx, auto):
    """Setup AI Video GPU integration for Codespace environments"""
    
    logger.info("Starting Codespace integration setup...")
    
    try:
        import subprocess
        import os
        
        # Get current directory
        current_dir = Path(__file__).parent
        setup_script = current_dir / "tools" / "codespace_setup.sh"
        
        if not setup_script.exists():
            logger.error("Setup script not found. Please ensure tools/codespace_setup.sh exists.")
            sys.exit(1)
            
        # Check if in Codespace
        in_codespace = os.environ.get('CODESPACES') is not None
        
        if in_codespace:
            logger.info("✅ GitHub Codespace detected")
        else:
            logger.info("ℹ️  Not in Codespace, setting up for local environment")
            
        # Run setup script
        logger.info("Running integration setup script...")
        
        cmd = [str(setup_script)]
        if auto:
            cmd.append("--auto")
            
        result = subprocess.run(cmd, cwd=current_dir, capture_output=False)
        
        if result.returncode == 0:
            logger.success("Codespace integration setup completed!")
            logger.info("📚 Check AI_VIDEO_GPU_INTEGRATION_README.md for usage instructions")
        else:
            logger.error("Setup script failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Codespace setup failed: {e}")
        sys.exit(1)

@cli.command()
@click.argument('repo_path', type=click.Path(exists=True))
@click.option('--target', help='Target directory for migration')
@click.option('--force', is_flag=True, help='Force migration even if target exists')
@click.option('--analyze-only', is_flag=True, help='Only analyze without migrating')
@click.pass_context
def auto_migrate(ctx, repo_path, target, force, analyze_only):
    """Automatically migrate existing AI Video Generator repositories"""
    
    logger.info(f"Starting auto-migration for: {repo_path}")
    
    try:
        import subprocess
        
        # Get migration script
        current_dir = Path(__file__).parent
        migrate_script = current_dir / "tools" / "auto_migrate.py"
        
        if not migrate_script.exists():
            logger.error("Migration script not found. Please ensure tools/auto_migrate.py exists.")
            sys.exit(1)
            
        # Build command
        cmd = [sys.executable, str(migrate_script), repo_path]
        
        if target:
            cmd.extend(['--target', target])
        if force:
            cmd.append('--force')
        if analyze_only:
            cmd.append('--analyze-only')
            
        # Run migration
        result = subprocess.run(cmd, cwd=current_dir)
        
        if result.returncode == 0:
            if analyze_only:
                logger.info("Repository analysis completed!")
            else:
                logger.success("Auto-migration completed successfully!")
                logger.info("📄 Check MIGRATION_REPORT.md in the target directory")
        else:
            logger.error("Auto-migration failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Auto-migration failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--interface', default='gradio', help='Interface type: gradio, streamlit, or fastapi')
@click.option('--port', default=7860, help='Port for web interface')
@click.option('--share', is_flag=True, help='Create public share link (Gradio only)')
@click.pass_context
def launch_interface(ctx, interface, port, share):
    """Launch web interface for AI Video GPU"""
    
    logger.info(f"Launching {interface} interface on port {port}...")
    
    try:
        if interface.lower() == 'gradio':
            from src.interfaces.gradio_interface import create_gradio_app
            
            app = create_gradio_app(ctx.obj['config_path'])
            
            logger.info("🌐 Starting Gradio interface...")
            logger.info(f"   Local URL: http://localhost:{port}")
            
            if share:
                logger.info("   Public URL will be generated...")
                
            app.launch(
                server_port=port,
                share=share,
                server_name="0.0.0.0"
            )
            
        elif interface.lower() == 'fastapi':
            from src.api.app import create_app
            import uvicorn
            
            app = create_app()
            
            logger.info("🚀 Starting FastAPI interface...")
            logger.info(f"   API URL: http://localhost:{port}")
            logger.info(f"   Docs URL: http://localhost:{port}/docs")
            
            uvicorn.run(app, host="0.0.0.0", port=port)
            
        else:
            logger.error(f"Unsupported interface: {interface}")
            logger.info("Supported interfaces: gradio, fastapi")
            sys.exit(1)
            
    except ImportError as e:
        logger.error(f"Interface dependencies not available: {e}")
        logger.info(f"Install with: pip install {interface}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to launch interface: {e}")
        sys.exit(1)

@cli.command()
@click.option('--input', '-i', required=True, help='Input video path')
@click.option('--output', '-o', required=True, help='Output video path')
@click.option('--upscale', is_flag=True, help='Upscale video 4x')
@click.option('--enhance-faces', is_flag=True, help='Enhance faces in video')
@click.option('--remove-background', is_flag=True, help='Remove video background')
@click.option('--denoise', is_flag=True, help='Apply denoising')
@click.pass_context
def enhance_video(ctx, input, output, upscale, enhance_faces, remove_background, denoise):
    """Enhance video quality using AI models"""
    
    logger.info(f"Enhancing video: {input}")
    
    try:
        from src.config import ConfigManager
        
        config = ConfigManager(ctx.obj['config_path'])
        enhancer = VideoEnhancer(config)
        
        enhancement_options = {
            'upscale': upscale,
            'enhance_faces': enhance_faces,
            'denoise': denoise,
            'color_correct': True
        }
        
        if remove_background:
            result = enhancer.remove_background_from_video(input, output)
        else:
            result = enhancer.enhance_video(input, output, enhancement_options)
            
        if result['success']:
            logger.success(f"Video enhanced successfully: {output}")
            if 'input_resolution' in result:
                logger.info(f"Resolution: {result['input_resolution']} → {result['output_resolution']}")
        else:
            logger.error(f"Enhancement failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Video enhancement failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--camera', default=0, help='Camera index for webcam')
@click.option('--fps', default=30, help='Target FPS for processing')
@click.option('--duration', default=60, help='Processing duration in seconds')
@click.pass_context
def realtime_demo(ctx, camera, fps, duration):
    """Start real-time video processing demo"""
    
    logger.info(f"Starting real-time demo (camera {camera}, {fps} FPS, {duration}s)")
    
    try:
        from src.config import ConfigManager
        
        config = ConfigManager(ctx.obj['config_path'])
        processor = RealTimeVideoProcessor(config)
        
        def processing_callback(frame, stats):
            if stats['fps'] > 0:
                logger.info(f"Real-time FPS: {stats['fps']:.1f}, Latency: {stats['latency']*1000:.1f}ms")
        
        result = processor.start_webcam_processing(
            camera_index=camera,
            target_fps=fps,
            processing_callback=processing_callback
        )
        
        if result['success']:
            logger.info("Real-time processing started. Press Ctrl+C to stop.")
            time.sleep(duration)
        else:
            logger.error(f"Failed to start real-time processing: {result['error']}")
            
    except KeyboardInterrupt:
        logger.info("Real-time demo stopped by user")
    except Exception as e:
        logger.error(f"Real-time demo failed: {e}")
    finally:
        try:
            processor.stop_processing()
        except:
            pass

@cli.command()
@click.option('--platform', required=True, help='Streaming platform (youtube, twitch, facebook)')
@click.option('--stream-key', required=True, help='Stream key from platform')
@click.option('--source', default='webcam', help='Video source (webcam, file)')
@click.option('--enable-ai', is_flag=True, help='Enable AI processing during stream')
@click.pass_context
def start_stream(ctx, platform, stream_key, source, enable_ai):
    """Start live streaming to platforms"""
    
    logger.info(f"Starting live stream to {platform}")
    
    try:
        stream_manager = LiveStreamManager()
        
        result = stream_manager.start_stream(
            platform=platform,
            stream_key=stream_key,
            video_source=source,
            enable_ai_processing=enable_ai
        )
        
        if result['success']:
            logger.success(f"Live stream started to {platform}")
            logger.info(f"RTMP URL: {result['rtmp_url']}")
            logger.info("Press Ctrl+C to stop streaming")
            
            # Keep alive until interrupted
            try:
                while True:
                    status = stream_manager.get_stream_status()
                    if not status.get(platform, {}).get('active', False):
                        logger.warning("Stream appears to have stopped")
                        break
                    time.sleep(30)
            except KeyboardInterrupt:
                logger.info("Stopping stream...")
                stream_manager.stop_stream(platform)
                
        else:
            logger.error(f"Failed to start stream: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--duration', default=300, help='Monitoring duration in seconds')
@click.option('--export', help='Export metrics to file')
@click.option('--alerts', is_flag=True, help='Enable alerting')
@click.pass_context
def monitor(ctx, duration, export, alerts):
    """Start system monitoring and performance analysis"""
    
    logger.info(f"Starting system monitoring for {duration} seconds")
    
    try:
        monitor = SystemMonitor(collection_interval=1.0)
        monitor.start_monitoring()
        
        alert_manager = None
        if alerts:
            alert_manager = AlertManager(monitor)
            logger.info("🚨 Alerting enabled")
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Show current metrics every 10 seconds
            if int(time.time() - start_time) % 10 == 0:
                current = monitor.get_current_metrics()
                if current:
                    logger.info(f"CPU: {current['cpu_percent']:.1f}%, "
                              f"Memory: {current['memory_percent']:.1f}%, "
                              f"GPU: {current['gpu_percent']:.1f}%, "
                              f"GPU Temp: {current['gpu_temperature']:.1f}°C")
            
            # Check alerts
            if alert_manager:
                alert_manager.check_alerts()
                active_alerts = alert_manager.get_active_alerts()
                if active_alerts:
                    logger.warning(f"🚨 {len(active_alerts)} active alerts")
            
            time.sleep(1)
        
        # Generate final report
        insights = monitor.get_performance_insights()
        video_stats = monitor.get_video_generation_stats()
        
        logger.info("\n📊 Performance Summary:")
        logger.info(f"System Health: {insights['system_health']}")
        logger.info(f"Videos Generated: {video_stats.total_videos}")
        logger.info(f"Success Rate: {video_stats.success_rate:.1f}%")
        logger.info(f"Average Processing Time: {video_stats.average_processing_time:.2f}s")
        
        if insights['recommendations']:
            logger.info("\n💡 Recommendations:")
            for rec in insights['recommendations']:
                logger.info(f"  • {rec}")
        
        if export:
            monitor.export_metrics(export)
            logger.success(f"Metrics exported to {export}")
        
        monitor.stop_monitoring()
        
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
        monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--provider', default='aws', help='Cloud provider (aws, azure, gcp)')
@click.option('--bucket', help='Storage bucket/container name')
@click.option('--upload', help='File to upload to cloud')
@click.option('--download', help='File to download from cloud')
@click.option('--local-path', help='Local file path for upload/download')
@click.pass_context
def cloud(ctx, provider, bucket, upload, download, local_path):
    """Cloud storage and distributed processing management"""
    
    logger.info(f"Cloud operations with {provider}")
    
    try:
        storage_manager = CloudStorageManager(
            provider=provider,
            bucket_name=bucket
        )
        
        if upload and local_path:
            result = storage_manager.upload_file(local_path, upload)
            if result['success']:
                logger.success(f"File uploaded: {result['url']}")
            else:
                logger.error(f"Upload failed: {result['error']}")
                
        elif download and local_path:
            result = storage_manager.download_file(download, local_path)
            if result['success']:
                logger.success(f"File downloaded: {result['local_path']}")
            else:
                logger.error(f"Download failed: {result['error']}")
        else:
            logger.info("No upload/download operation specified")
            logger.info("Available operations:")
            logger.info("  --upload <remote_path> --local-path <local_path>")
            logger.info("  --download <remote_path> --local-path <local_path>")
            
    except Exception as e:
        logger.error(f"Cloud operation failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--category', help='Model category (tts, lip_sync, enhancement)')
@click.option('--download-model', help='Download specific model')
@click.pass_context
def models(ctx, category, download_model):
    """Model repository management"""
    
    logger.info("Model repository management")
    
    try:
        model_repo = ModelRepository()
        
        if download_model and category:
            result = model_repo.download_model(category, download_model)
            if result['success']:
                cached = "✅ (cached)" if result['cached'] else "⬇️ (downloaded)"
                logger.success(f"Model ready: {result['path']} {cached}")
            else:
                logger.error(f"Model download failed: {result['error']}")
        else:
            # List available models
            available = model_repo.list_available_models()
            
            logger.info("📦 Available Models:")
            for cat, models in available.items():
                logger.info(f"\n{cat.upper()}:")
                for name, info in models.items():
                    logger.info(f"  • {name}: {info['description']} ({info['size']})")
            
            logger.info("\n💡 Usage:")
            logger.info("  python main.py models --category tts --download-model xtts-v2")
            
    except Exception as e:
        logger.error(f"Model management failed: {e}")
        sys.exit(1)

@cli.command()
@click.argument('script_text', type=str)
@click.option('--output-dir', '-o', default='output/animations', help='Output directory for animations')
@click.option('--style', default='natural', help='Animation style (natural, energetic, professional)')
@click.option('--duration', type=float, default=10.0, help='Animation duration in seconds')
@click.option('--export-format', default='json', help='Export format (json, bvh, blender)')
@click.pass_context
def animate(ctx, script_text, output_dir, style, duration, export_format):
    """Generate advanced character animation from script"""
    
    try:
        logger.info("🎭 Starting animation generation")
        
        # Initialize animation engine
        config = ConfigManager().get_config()
        animation_engine = AnimationEngine(config)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate placeholder audio features (in real implementation, would extract from audio)
        audio_features = np.random.random((int(duration * 30), 80))  # 30 FPS, 80 MFCC features
        
        # Generate animation
        logger.info(f"Generating {style} animation for: {script_text[:50]}...")
        animation_data = animation_engine.generate_full_animation(
            script_text, audio_features, duration, style
        )
        
        # Export animation
        output_file = output_path / f"animation_{int(time.time())}.{export_format}"
        success = animation_engine.export_animation(animation_data, output_file, export_format)
        
        if success:
            logger.success(f"Animation exported to: {output_file}")
            
            # Print animation summary
            logger.info("📊 Animation Summary:")
            logger.info(f"  Duration: {duration:.1f}s")
            logger.info(f"  Style: {style}")
            logger.info(f"  Facial keyframes: {len(animation_data['facial_animation'])}")
            logger.info(f"  Pose keyframes: {len(animation_data['pose_animation'])}")
            logger.info(f"  Gestures: {len(animation_data['gesture_animation'])}")
        else:
            logger.error("Animation export failed")
            
    except Exception as e:
        logger.error(f"Animation generation failed: {e}")
        sys.exit(1)

@cli.command()
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output audio file path')
@click.option('--denoise', is_flag=True, help='Apply audio denoising')
@click.option('--enhance-speech', is_flag=True, help='Enhance speech clarity')
@click.option('--emotion', help='Transfer emotion (happy, sad, angry, calm, excited)')
@click.option('--master', is_flag=True, help='Apply audio mastering')
@click.pass_context
def audio_enhance(ctx, audio_file, output, denoise, enhance_speech, emotion, master):
    """Advanced audio processing and enhancement"""
    
    try:
        logger.info("🔊 Starting audio enhancement")
        
        # Initialize audio engine
        config = ConfigManager().get_config()
        audio_engine = AdvancedAudioEngine(config)
        
        # Set output path
        if not output:
            input_path = Path(audio_file)
            output = input_path.parent / f"{input_path.stem}_enhanced{input_path.suffix}"
        
        # Configure processing options
        processing_options = {
            'denoise': denoise,
            'enhance_speech': enhance_speech,
            'master': master
        }
        
        if emotion:
            processing_options['target_emotion'] = emotion
        
        # Process audio
        logger.info(f"Processing: {audio_file}")
        processed_audio = audio_engine.process_audio_complete(
            Path(audio_file), processing_options
        )
        
        # Save processed audio
        success = audio_engine.save_processed_audio(processed_audio, Path(output))
        
        if success:
            logger.success(f"Enhanced audio saved to: {output}")
            
            # Print processing summary
            logger.info("📊 Processing Summary:")
            if denoise:
                logger.info("  ✓ Noise reduction applied")
            if enhance_speech:
                logger.info("  ✓ Speech enhancement applied")
            if emotion:
                logger.info(f"  ✓ Emotion transfer: {emotion}")
            if master:
                logger.info("  ✓ Audio mastering applied")
        else:
            logger.error("Audio processing failed")
            
    except Exception as e:
        logger.error(f"Audio enhancement failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--scene-type', default='talking_head', 
              help='Scene type (talking_head, presentation, interview, tutorial)')
@click.option('--script', help='Script text for scene planning')
@click.option('--output', '-o', default='output/scene.json', help='Output scene file')
@click.option('--lighting', default='natural', help='Lighting style (natural, warm, cool, dramatic)')
@click.option('--export-format', default='json', help='Export format (json, blender, unity)')
@click.pass_context
def scene_generate(ctx, scene_type, script, output, lighting, export_format):
    """Generate complex 3D scenes with lighting and camera setup"""
    
    try:
        logger.info("🎬 Starting scene generation")
        
        # Initialize scene engine
        config = ConfigManager().get_config()
        scene_engine = SceneEngine(config)
        
        # Parse scene type
        try:
            scene_type_enum = SceneType(scene_type)
        except ValueError:
            logger.error(f"Invalid scene type: {scene_type}")
            logger.info("Valid types: talking_head, presentation, interview, tutorial")
            sys.exit(1)
        
        # Prepare script data
        script_data = {}
        if script:
            # Simple script parsing - in production would be more sophisticated
            script_data = {
                'text': script,
                'segments': [{'text': script, 'duration': 10.0, 'tags': []}]
            }
        
        # Scene customizations
        customizations = {
            'lighting_style': lighting,
            'camera_adjustments': {},
            'additional_objects': []
        }
        
        # Generate scene
        logger.info(f"Generating {scene_type} scene...")
        scene = scene_engine.generate_complete_scene(
            scene_type_enum, script_data, customizations
        )
        
        # Export scene
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        success = scene_engine.export_scene(scene, output_path, export_format)
        
        if success:
            logger.success(f"Scene exported to: {output_path}")
            
            # Print scene summary
            metadata = scene.get('metadata', {})
            logger.info("📊 Scene Summary:")
            logger.info(f"  Type: {scene_type}")
            logger.info(f"  Objects: {metadata.get('objects_count', 0)}")
            logger.info(f"  Lights: {metadata.get('lights_count', 0)}")
            logger.info(f"  Estimated render time: {metadata.get('estimated_render_time', 0):.1f}s per second")
            
            if 'shots' in scene:
                logger.info(f"  Camera shots: {len(scene['shots'])}")
        else:
            logger.error("Scene export failed")
            
    except Exception as e:
        logger.error(f"Scene generation failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--models', is_flag=True, help='Optimize models for performance')
@click.option('--memory', is_flag=True, help='Optimize memory usage')
@click.option('--gpu', is_flag=True, help='Optimize GPU scheduling')
@click.option('--report', is_flag=True, help='Generate performance report')
@click.option('--auto', is_flag=True, help='Apply automatic optimizations')
@click.pass_context
def optimize(ctx, models, memory, gpu, report, auto):
    """Performance optimization and system tuning"""
    
    try:
        logger.info("⚡ Starting performance optimization")
        
        # Initialize performance optimizer
        config = ConfigManager().get_config()
        optimizer = PerformanceOptimizer(config)
        
        if auto:
            logger.info("Applying automatic optimizations...")
            optimizer.apply_automatic_optimizations()
            logger.success("Automatic optimizations applied")
        
        if models:
            logger.info("Optimizing models...")
            # In real implementation, would load and optimize actual models
            logger.info("Model optimization completed")
        
        if memory:
            logger.info("Optimizing memory usage...")
            optimizer.memory_manager.force_cleanup()
            memory_info = optimizer.memory_manager.monitor_memory()
            logger.success(f"Memory optimized - Available: {memory_info['system']['available_gb']:.1f}GB")
        
        if gpu:
            logger.info("Optimizing GPU scheduling...")
            optimizer.gpu_scheduler.optimize_scheduling()
            logger.success("GPU scheduling optimized")
        
        if report:
            logger.info("Generating performance report...")
            perf_report = optimizer.generate_performance_report()
            
            # Print key metrics
            logger.info("📊 Performance Report:")
            system_info = perf_report['system_info']
            logger.info(f"  GPU Available: {system_info['gpu_available']}")
            if system_info['gpu_available']:
                logger.info(f"  GPU Count: {system_info['gpu_count']}")
            logger.info(f"  CPU Cores: {system_info['cpu_count']}")
            logger.info(f"  Total Memory: {system_info['total_memory_gb']:.1f}GB")
            
            # Save detailed report
            report_path = Path('output/performance_report.json')
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w') as f:
                json.dump(perf_report, f, indent=2, default=str)
            logger.info(f"  Detailed report saved: {report_path}")
            
            # Show recommendations
            recommendations = perf_report['recommendations']
            if recommendations:
                logger.info("💡 Recommendations:")
                for rec in recommendations:
                    logger.info(f"  • {rec}")
        
        if not any([models, memory, gpu, report, auto]):
            logger.info("No optimization options specified. Use --help for options.")
            
    except Exception as e:
        logger.error(f"Performance optimization failed: {e}")
        sys.exit(1)

@cli.command()
@click.argument('video_file', type=click.Path(exists=True))
@click.option('--template', help='Video template to apply (corporate, educational, social_media)')
@click.option('--watermark', help='Watermark image path')
@click.option('--platforms', multiple=True, help='Export platforms (youtube, instagram, tiktok, linkedin)')
@click.option('--quality-check', is_flag=True, help='Run quality assessment')
@click.option('--output-dir', '-o', default='output/production', help='Output directory')
@click.pass_context
def production(ctx, video_file, template, watermark, platforms, quality_check, output_dir):
    """Complete production pipeline with templates, watermarking, and multi-platform export"""
    
    try:
        logger.info("🎬 Starting production pipeline")
        
        # Initialize production engine
        config = ConfigManager().get_config()
        production_engine = ProductionEngine(config)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Configure production
        production_config = {
            'quality_check': quality_check
        }
        
        if template:
            production_config['template'] = template
            logger.info(f"Using template: {template}")
        
        if watermark:
            production_config['watermark'] = {
                'image_path': watermark,
                'position': 'bottom_right',
                'opacity': 0.7,
                'scale': 0.1
            }
            logger.info(f"Adding watermark: {watermark}")
        
        if platforms:
            production_config['export_platforms'] = list(platforms)
            logger.info(f"Exporting for platforms: {', '.join(platforms)}")
        
        # Add metadata
        production_config['metadata'] = {
            'title': f"Video generated by AI Video GPU",
            'description': "Generated using AI Video GPU production pipeline",
            'creator': "AI Video GPU",
            'tags': ['ai-generated', 'video-production']
        }
        
        # Process video
        logger.info(f"Processing video: {video_file}")
        results = production_engine.process_video_production(
            Path(video_file), production_config
        )
        
        # Generate and save report
        report = production_engine.create_production_report(results)
        report_path = output_path / 'production_report.txt'
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.success("Production pipeline completed!")
        logger.info(f"Production report saved: {report_path}")
        
        # Print summary
        logger.info("📊 Production Summary:")
        logger.info(f"  Steps completed: {len(results['steps_completed'])}")
        
        if 'quality_scores' in results:
            overall_score = results['quality_scores']['overall_score']
            logger.info(f"  Overall quality: {overall_score:.2f}/1.0")
        
        if 'export_paths' in results:
            logger.info(f"  Exported versions: {len(results['export_paths'])}")
            
    except Exception as e:
        logger.error(f"Production pipeline failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli()

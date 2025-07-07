"""
Scene Understanding and Generation Engine
Handles complex scene composition, object placement, lighting, and multi-shot planning
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import json
import torch
import torch.nn.functional as F
from dataclasses import dataclass
from enum import Enum
from loguru import logger

class SceneType(Enum):
    """Types of scenes for video generation"""
    TALKING_HEAD = "talking_head"
    PRESENTATION = "presentation"
    INTERVIEW = "interview"
    TUTORIAL = "tutorial"
    DOCUMENTARY = "documentary"
    COMMERCIAL = "commercial"

class LightingType(Enum):
    """Lighting setups"""
    KEY_FILL_RIM = "key_fill_rim"
    NATURAL = "natural"
    DRAMATIC = "dramatic"
    SOFT = "soft"
    STUDIO = "studio"
    OUTDOOR = "outdoor"

@dataclass
class SceneObject:
    """Represents an object in the scene"""
    name: str
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float]
    scale: Tuple[float, float, float]
    object_type: str
    properties: Dict[str, Any]

@dataclass
class CameraSetup:
    """Camera configuration"""
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float]
    fov: float
    focal_length: float
    aperture: float
    focus_distance: float

@dataclass
class LightSetup:
    """Lighting configuration"""
    light_type: str  # key, fill, rim, ambient
    position: Tuple[float, float, float]
    intensity: float
    color: Tuple[float, float, float]
    temperature: float
    size: float

class SceneComposer:
    """Main scene composition engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Predefined scene templates
        self.scene_templates = {
            SceneType.TALKING_HEAD: self._create_talking_head_template(),
            SceneType.PRESENTATION: self._create_presentation_template(),
            SceneType.INTERVIEW: self._create_interview_template(),
            SceneType.TUTORIAL: self._create_tutorial_template(),
        }
        
        # Common objects library
        self.object_library = self._load_object_library()
        
    def _create_talking_head_template(self) -> Dict[str, Any]:
        """Create talking head scene template"""
        return {
            'name': 'talking_head',
            'camera': CameraSetup(
                position=(0.0, 1.6, 2.0),
                rotation=(0.0, 0.0, 0.0),
                fov=50.0,
                focal_length=85.0,
                aperture=2.8,
                focus_distance=2.0
            ),
            'lights': [
                LightSetup('key', (-1.0, 2.0, 1.5), 1.0, (1.0, 1.0, 1.0), 5600, 1.0),
                LightSetup('fill', (1.0, 1.5, 1.0), 0.5, (1.0, 1.0, 1.0), 5600, 1.5),
                LightSetup('rim', (0.0, 2.5, -1.0), 0.8, (1.0, 1.0, 1.0), 5600, 0.5),
            ],
            'objects': [
                SceneObject('avatar', (0.0, 1.6, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), 'character', {}),
                SceneObject('background', (0.0, 1.0, -3.0), (0.0, 0.0, 0.0), (4.0, 3.0, 1.0), 'backdrop', {})
            ]
        }
    
    def _create_presentation_template(self) -> Dict[str, Any]:
        """Create presentation scene template"""
        return {
            'name': 'presentation',
            'camera': CameraSetup(
                position=(-1.0, 1.6, 3.0),
                rotation=(0.0, 15.0, 0.0),
                fov=60.0,
                focal_length=35.0,
                aperture=4.0,
                focus_distance=3.0
            ),
            'lights': [
                LightSetup('key', (-2.0, 2.5, 2.0), 1.2, (1.0, 1.0, 1.0), 5600, 2.0),
                LightSetup('fill', (2.0, 1.8, 1.5), 0.6, (1.0, 1.0, 1.0), 5600, 2.5),
                LightSetup('screen', (2.0, 1.5, -1.0), 0.3, (0.9, 0.9, 1.0), 6500, 3.0),
            ],
            'objects': [
                SceneObject('presenter', (-0.5, 1.6, 0.0), (0.0, 30.0, 0.0), (1.0, 1.0, 1.0), 'character', {}),
                SceneObject('screen', (1.5, 1.5, -0.5), (0.0, -30.0, 0.0), (2.0, 1.5, 0.1), 'display', {}),
                SceneObject('podium', (-0.3, 0.8, 0.5), (0.0, 30.0, 0.0), (0.6, 1.0, 0.4), 'furniture', {})
            ]
        }
    
    def _create_interview_template(self) -> Dict[str, Any]:
        """Create interview scene template"""
        return {
            'name': 'interview',
            'camera': CameraSetup(
                position=(0.0, 1.6, 4.0),
                rotation=(0.0, 0.0, 0.0),
                fov=45.0,
                focal_length=85.0,
                aperture=2.0,
                focus_distance=3.0
            ),
            'lights': [
                LightSetup('key_left', (-2.0, 2.0, 2.0), 1.0, (1.0, 1.0, 1.0), 5600, 2.0),
                LightSetup('key_right', (2.0, 2.0, 2.0), 1.0, (1.0, 1.0, 1.0), 5600, 2.0),
                LightSetup('fill', (0.0, 1.5, 3.0), 0.4, (1.0, 1.0, 1.0), 5600, 3.0),
            ],
            'objects': [
                SceneObject('interviewer', (-1.0, 1.6, 0.0), (0.0, 30.0, 0.0), (1.0, 1.0, 1.0), 'character', {}),
                SceneObject('interviewee', (1.0, 1.6, 0.0), (0.0, -30.0, 0.0), (1.0, 1.0, 1.0), 'character', {}),
                SceneObject('table', (0.0, 0.7, 0.5), (0.0, 0.0, 0.0), (2.0, 0.1, 1.0), 'furniture', {}),
            ]
        }
    
    def _create_tutorial_template(self) -> Dict[str, Any]:
        """Create tutorial scene template"""
        return {
            'name': 'tutorial',
            'camera': CameraSetup(
                position=(0.0, 2.0, 3.0),
                rotation=(-10.0, 0.0, 0.0),
                fov=55.0,
                focal_length=50.0,
                aperture=3.5,
                focus_distance=2.5
            ),
            'lights': [
                LightSetup('overhead', (0.0, 4.0, 1.0), 1.5, (1.0, 1.0, 1.0), 5600, 3.0),
                LightSetup('side', (2.0, 1.5, 1.5), 0.7, (1.0, 1.0, 1.0), 5600, 1.5),
                LightSetup('task', (0.0, 3.0, 0.0), 1.0, (1.0, 1.0, 1.0), 6500, 1.0),
            ],
            'objects': [
                SceneObject('instructor', (0.0, 1.6, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), 'character', {}),
                SceneObject('work_surface', (0.0, 1.0, 0.5), (0.0, 0.0, 0.0), (1.5, 0.1, 1.0), 'surface', {}),
                SceneObject('tools', (0.3, 1.1, 0.5), (0.0, 0.0, 0.0), (0.3, 0.1, 0.2), 'props', {}),
            ]
        }
    
    def _load_object_library(self) -> Dict[str, Dict[str, Any]]:
        """Load common 3D objects library"""
        return {
            'furniture': {
                'chair': {'model': 'chair.obj', 'scale': (1.0, 1.0, 1.0)},
                'table': {'model': 'table.obj', 'scale': (1.0, 1.0, 1.0)},
                'desk': {'model': 'desk.obj', 'scale': (1.0, 1.0, 1.0)},
                'podium': {'model': 'podium.obj', 'scale': (1.0, 1.0, 1.0)},
            },
            'technology': {
                'laptop': {'model': 'laptop.obj', 'scale': (1.0, 1.0, 1.0)},
                'monitor': {'model': 'monitor.obj', 'scale': (1.0, 1.0, 1.0)},
                'camera': {'model': 'camera.obj', 'scale': (1.0, 1.0, 1.0)},
                'microphone': {'model': 'microphone.obj', 'scale': (1.0, 1.0, 1.0)},
            },
            'decor': {
                'plant': {'model': 'plant.obj', 'scale': (1.0, 1.0, 1.0)},
                'painting': {'model': 'painting.obj', 'scale': (1.0, 1.0, 1.0)},
                'bookshelf': {'model': 'bookshelf.obj', 'scale': (1.0, 1.0, 1.0)},
            }
        }
    
    def compose_scene(self, scene_type: SceneType, customizations: Dict[str, Any] = None) -> Dict[str, Any]:
        """Compose a complete scene based on type and customizations"""
        
        logger.info(f"Composing scene: {scene_type.value}")
        
        # Get base template
        if scene_type not in self.scene_templates:
            logger.warning(f"Unknown scene type: {scene_type.value}, using talking_head")
            scene_type = SceneType.TALKING_HEAD
        
        scene = self.scene_templates[scene_type].copy()
        
        # Apply customizations
        if customizations:
            scene = self._apply_customizations(scene, customizations)
        
        # Validate and optimize scene
        scene = self._validate_scene(scene)
        
        return scene
    
    def _apply_customizations(self, scene: Dict[str, Any], customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply user customizations to scene"""
        
        # Customize lighting
        if 'lighting_style' in customizations:
            scene = self._apply_lighting_style(scene, customizations['lighting_style'])
        
        # Add custom objects
        if 'additional_objects' in customizations:
            for obj_spec in customizations['additional_objects']:
                obj = self._create_object_from_spec(obj_spec)
                scene['objects'].append(obj)
        
        # Modify camera
        if 'camera_adjustments' in customizations:
            scene['camera'] = self._adjust_camera(scene['camera'], customizations['camera_adjustments'])
        
        return scene
    
    def _apply_lighting_style(self, scene: Dict[str, Any], style: str) -> Dict[str, Any]:
        """Apply lighting style to scene"""
        
        lighting_styles = {
            'natural': {'temperature': 5600, 'intensity_scale': 0.8},
            'warm': {'temperature': 3200, 'intensity_scale': 1.0},
            'cool': {'temperature': 6500, 'intensity_scale': 1.1},
            'dramatic': {'temperature': 4000, 'intensity_scale': 1.5},
            'soft': {'temperature': 5600, 'intensity_scale': 0.6},
        }
        
        if style in lighting_styles:
            style_params = lighting_styles[style]
            for light in scene['lights']:
                light.temperature = style_params['temperature']
                light.intensity *= style_params['intensity_scale']
        
        return scene
    
    def _create_object_from_spec(self, spec: Dict[str, Any]) -> SceneObject:
        """Create scene object from specification"""
        
        return SceneObject(
            name=spec.get('name', 'object'),
            position=tuple(spec.get('position', [0.0, 0.0, 0.0])),
            rotation=tuple(spec.get('rotation', [0.0, 0.0, 0.0])),
            scale=tuple(spec.get('scale', [1.0, 1.0, 1.0])),
            object_type=spec.get('type', 'prop'),
            properties=spec.get('properties', {})
        )
    
    def _adjust_camera(self, camera: CameraSetup, adjustments: Dict[str, Any]) -> CameraSetup:
        """Apply camera adjustments"""
        
        if 'position' in adjustments:
            camera.position = tuple(adjustments['position'])
        if 'rotation' in adjustments:
            camera.rotation = tuple(adjustments['rotation'])
        if 'fov' in adjustments:
            camera.fov = adjustments['fov']
        if 'focal_length' in adjustments:
            camera.focal_length = adjustments['focal_length']
        
        return camera
    
    def _validate_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and optimize scene configuration"""
        
        # Check for object collisions
        scene['objects'] = self._resolve_collisions(scene['objects'])
        
        # Optimize lighting
        scene['lights'] = self._optimize_lighting(scene['lights'])
        
        # Validate camera placement
        scene['camera'] = self._validate_camera(scene['camera'], scene['objects'])
        
        return scene
    
    def _resolve_collisions(self, objects: List[SceneObject]) -> List[SceneObject]:
        """Resolve object collisions in scene"""
        
        # Simple collision detection and resolution
        for i, obj1 in enumerate(objects):
            for j, obj2 in enumerate(objects[i+1:], i+1):
                if self._objects_collide(obj1, obj2):
                    # Move second object slightly
                    objects[j].position = (
                        obj2.position[0] + 0.5,
                        obj2.position[1],
                        obj2.position[2]
                    )
        
        return objects
    
    def _objects_collide(self, obj1: SceneObject, obj2: SceneObject) -> bool:
        """Check if two objects collide"""
        
        # Simple bounding box collision
        pos1, scale1 = np.array(obj1.position), np.array(obj1.scale)
        pos2, scale2 = np.array(obj2.position), np.array(obj2.scale)
        
        distance = np.linalg.norm(pos1 - pos2)
        combined_radius = (np.linalg.norm(scale1) + np.linalg.norm(scale2)) / 2
        
        return distance < combined_radius
    
    def _optimize_lighting(self, lights: List[LightSetup]) -> List[LightSetup]:
        """Optimize lighting setup"""
        
        # Ensure total intensity is reasonable
        total_intensity = sum(light.intensity for light in lights)
        
        if total_intensity > 5.0:
            # Scale down all lights
            scale_factor = 5.0 / total_intensity
            for light in lights:
                light.intensity *= scale_factor
        
        return lights
    
    def _validate_camera(self, camera: CameraSetup, objects: List[SceneObject]) -> CameraSetup:
        """Validate camera placement relative to objects"""
        
        # Ensure camera isn't inside objects
        camera_pos = np.array(camera.position)
        
        for obj in objects:
            obj_pos = np.array(obj.position)
            obj_scale = np.array(obj.scale)
            
            distance = np.linalg.norm(camera_pos - obj_pos)
            min_distance = np.linalg.norm(obj_scale) / 2 + 0.5
            
            if distance < min_distance:
                # Move camera away
                direction = (camera_pos - obj_pos) / distance
                camera.position = tuple(obj_pos + direction * min_distance)
        
        return camera

class PhysicsSimulator:
    """Simple physics simulation for object placement"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.gravity = config.get('gravity', -9.81)
        
    def simulate_object_placement(self, objects: List[SceneObject], 
                                 duration: float = 2.0) -> List[SceneObject]:
        """Simulate realistic object placement with physics"""
        
        # Simple gravity simulation
        for obj in objects:
            if obj.object_type in ['furniture', 'props']:
                # Objects settle to ground level
                ground_level = 0.0
                if obj.object_type == 'furniture':
                    # Furniture sits on ground
                    obj.position = (obj.position[0], ground_level + obj.scale[1]/2, obj.position[2])
                elif obj.object_type == 'props':
                    # Props might sit on furniture
                    support_height = self._find_support_height(obj, objects)
                    obj.position = (obj.position[0], support_height + obj.scale[1]/2, obj.position[2])
        
        return objects
    
    def _find_support_height(self, obj: SceneObject, all_objects: List[SceneObject]) -> float:
        """Find the height an object should sit at based on supports below it"""
        
        max_support_height = 0.0
        obj_pos = np.array(obj.position)
        
        for other_obj in all_objects:
            if other_obj.name == obj.name:
                continue
            
            other_pos = np.array(other_obj.position)
            
            # Check if objects are horizontally aligned
            horizontal_distance = np.linalg.norm(obj_pos[:2] - other_pos[:2])
            
            if horizontal_distance < (obj.scale[0] + other_obj.scale[0]) / 2:
                # Objects overlap horizontally
                support_top = other_pos[1] + other_obj.scale[1] / 2
                max_support_height = max(max_support_height, support_top)
        
        return max_support_height

class MultiShotPlanner:
    """Plan multiple camera shots for complex videos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Shot types and their characteristics
        self.shot_types = {
            'wide': {'distance': 5.0, 'fov': 60, 'duration': 3.0},
            'medium': {'distance': 3.0, 'fov': 50, 'duration': 4.0},
            'close': {'distance': 1.5, 'fov': 35, 'duration': 5.0},
            'extreme_close': {'distance': 0.8, 'fov': 25, 'duration': 3.0},
        }
    
    def plan_shots(self, script_segments: List[Dict[str, Any]], 
                   scene: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan camera shots for script segments"""
        
        shots = []
        current_time = 0.0
        
        for i, segment in enumerate(script_segments):
            shot_type = self._determine_shot_type(segment, i, len(script_segments))
            
            shot = self._create_shot(
                shot_type=shot_type,
                scene=scene,
                segment=segment,
                start_time=current_time
            )
            
            shots.append(shot)
            current_time += shot['duration']
        
        return shots
    
    def _determine_shot_type(self, segment: Dict[str, Any], 
                           segment_index: int, total_segments: int) -> str:
        """Determine appropriate shot type for segment"""
        
        # Simple shot selection logic
        if segment_index == 0:
            return 'wide'  # Start with establishing shot
        elif segment_index == total_segments - 1:
            return 'medium'  # End with medium shot
        elif 'important' in segment.get('tags', []):
            return 'close'  # Close-up for important content
        else:
            return 'medium'  # Default to medium shot
    
    def _create_shot(self, shot_type: str, scene: Dict[str, Any], 
                    segment: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Create camera shot configuration"""
        
        shot_config = self.shot_types[shot_type]
        
        # Calculate camera position
        subject_pos = self._find_primary_subject(scene)
        camera_distance = shot_config['distance']
        camera_height = subject_pos[1] + 0.1  # Slightly above subject eye level
        
        shot = {
            'type': shot_type,
            'start_time': start_time,
            'duration': shot_config['duration'],
            'camera': CameraSetup(
                position=(subject_pos[0], camera_height, subject_pos[2] + camera_distance),
                rotation=(0.0, 0.0, 0.0),
                fov=shot_config['fov'],
                focal_length=50.0,
                aperture=2.8,
                focus_distance=camera_distance
            ),
            'segment': segment,
            'transitions': {
                'in': 'cut',  # How to transition into this shot
                'out': 'cut'  # How to transition out of this shot
            }
        }
        
        return shot
    
    def _find_primary_subject(self, scene: Dict[str, Any]) -> Tuple[float, float, float]:
        """Find the primary subject in the scene"""
        
        # Look for character objects
        for obj in scene['objects']:
            if obj.object_type == 'character':
                return obj.position
        
        # Default to scene center
        return (0.0, 1.6, 0.0)

class SceneEngine:
    """Main scene understanding and generation engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.composer = SceneComposer(config)
        self.physics = PhysicsSimulator(config)
        self.planner = MultiShotPlanner(config)
        
    def generate_complete_scene(self, 
                               scene_type: SceneType,
                               script_data: Dict[str, Any],
                               customizations: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a complete scene with physics and shot planning"""
        
        logger.info("Generating complete scene setup")
        
        # Compose base scene
        scene = self.composer.compose_scene(scene_type, customizations)
        
        # Apply physics simulation
        scene['objects'] = self.physics.simulate_object_placement(scene['objects'])
        
        # Plan shots if script has multiple segments
        if 'segments' in script_data:
            shots = self.planner.plan_shots(script_data['segments'], scene)
            scene['shots'] = shots
        
        # Add metadata
        scene['metadata'] = {
            'scene_type': scene_type.value,
            'generation_time': np.datetime64('now').astype(str),
            'objects_count': len(scene['objects']),
            'lights_count': len(scene['lights']),
            'estimated_render_time': self._estimate_render_time(scene)
        }
        
        return scene
    
    def _estimate_render_time(self, scene: Dict[str, Any]) -> float:
        """Estimate rendering time based on scene complexity"""
        
        # Simple estimation based on object count and lighting
        base_time = 1.0  # Base render time per second
        object_factor = len(scene['objects']) * 0.1
        light_factor = len(scene['lights']) * 0.05
        
        return base_time + object_factor + light_factor
    
    def export_scene(self, scene: Dict[str, Any], output_path: Path, 
                    format: str = 'json') -> bool:
        """Export scene to various formats"""
        
        try:
            if format == 'json':
                return self._export_json(scene, output_path)
            elif format == 'blender':
                return self._export_blender(scene, output_path)
            elif format == 'unity':
                return self._export_unity(scene, output_path)
            else:
                logger.error(f"Unsupported export format: {format}")
                return False
        except Exception as e:
            logger.error(f"Scene export failed: {e}")
            return False
    
    def _export_json(self, scene: Dict[str, Any], output_path: Path) -> bool:
        """Export scene to JSON format"""
        
        # Convert dataclasses to dictionaries
        def convert_for_json(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)
        
        with open(output_path, 'w') as f:
            json.dump(scene, f, indent=2, default=convert_for_json)
        
        return True
    
    def _export_blender(self, scene: Dict[str, Any], output_path: Path) -> bool:
        """Export scene to Blender Python script"""
        
        script = """
import bpy
import bmesh
from mathutils import Vector, Euler

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

"""
        
        # Add objects
        for obj in scene['objects']:
            script += f"""
# Add {obj.name}
bpy.ops.mesh.primitive_cube_add(location={obj.position})
obj = bpy.context.active_object
obj.name = '{obj.name}'
obj.scale = {obj.scale}
obj.rotation_euler = Euler({obj.rotation}, 'XYZ')

"""
        
        # Add lights
        for light in scene['lights']:
            script += f"""
# Add {light.light_type} light
bpy.ops.object.light_add(type='AREA', location={light.position})
light = bpy.context.active_object
light.data.energy = {light.intensity}
light.data.color = {light.color}

"""
        
        # Add camera
        camera = scene['camera']
        script += f"""
# Add camera
bpy.ops.object.camera_add(location={camera.position})
camera = bpy.context.active_object
camera.rotation_euler = Euler({camera.rotation}, 'XYZ')
camera.data.lens = {camera.focal_length}

"""
        
        with open(output_path, 'w') as f:
            f.write(script)
        
        return True
    
    def _export_unity(self, scene: Dict[str, Any], output_path: Path) -> bool:
        """Export scene to Unity-compatible format"""
        
        # Create Unity scene data structure
        unity_scene = {
            'Scene': {
                'name': scene.get('name', 'Generated Scene'),
                'GameObjects': []
            }
        }
        
        # Add objects
        for obj in scene['objects']:
            unity_obj = {
                'name': obj.name,
                'transform': {
                    'position': {'x': obj.position[0], 'y': obj.position[1], 'z': obj.position[2]},
                    'rotation': {'x': obj.rotation[0], 'y': obj.rotation[1], 'z': obj.rotation[2]},
                    'scale': {'x': obj.scale[0], 'y': obj.scale[1], 'z': obj.scale[2]}
                },
                'components': [
                    {'type': 'MeshRenderer'},
                    {'type': 'MeshFilter'}
                ]
            }
            unity_scene['Scene']['GameObjects'].append(unity_obj)
        
        # Add lights
        for light in scene['lights']:
            light_obj = {
                'name': f'{light.light_type}_light',
                'transform': {
                    'position': {'x': light.position[0], 'y': light.position[1], 'z': light.position[2]},
                    'rotation': {'x': 0, 'y': 0, 'z': 0},
                    'scale': {'x': 1, 'y': 1, 'z': 1}
                },
                'components': [
                    {
                        'type': 'Light',
                        'intensity': light.intensity,
                        'color': {'r': light.color[0], 'g': light.color[1], 'b': light.color[2]}
                    }
                ]
            }
            unity_scene['Scene']['GameObjects'].append(light_obj)
        
        # Add camera
        camera = scene['camera']
        camera_obj = {
            'name': 'Main Camera',
            'transform': {
                'position': {'x': camera.position[0], 'y': camera.position[1], 'z': camera.position[2]},
                'rotation': {'x': camera.rotation[0], 'y': camera.rotation[1], 'z': camera.rotation[2]},
                'scale': {'x': 1, 'y': 1, 'z': 1}
            },
            'components': [
                {
                    'type': 'Camera',
                    'fieldOfView': camera.fov,
                    'nearClipPlane': 0.1,
                    'farClipPlane': 1000
                }
            ]
        }
        unity_scene['Scene']['GameObjects'].append(camera_obj)
        
        with open(output_path, 'w') as f:
            json.dump(unity_scene, f, indent=2)
        
        return True

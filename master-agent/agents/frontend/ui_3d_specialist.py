"""
UI 3D Specialist Agent

Expert in creating stunning 3D UI elements using:
- Three.js for WebGL rendering
- React Three Fiber for declarative 3D
- @react-three/drei for helpers
- @react-three/postprocessing for effects
- Performance optimization for smooth 60fps

Capabilities:
- 3D scene composition
- Interactive 3D elements
- Particle systems
- 3D loading animations
- Camera controls and transitions
- Physics-based interactions
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ThreeJSScene:
    """Configuration for Three.js scene"""

    scene_type: str  # "hero", "product", "background", "interactive"
    camera_type: str  # "perspective", "orthographic"
    controls: str  # "orbit", "trackball", "pointer_lock", "none"
    lighting: Dict[str, Any]  # ambient, directional, point, spotlight
    objects: List[Dict[str, Any]]  # 3D objects in scene
    effects: List[str]  # bloom, chromatic_aberration, vignette, etc.
    physics_enabled: bool = False
    performance_mode: str = "balanced"  # "high_quality", "balanced", "performance"


@dataclass
class R3FComponent:
    """React Three Fiber component specification"""

    component_name: str
    scene_config: ThreeJSScene
    interactions: List[Dict[str, Any]]  # click, hover, drag events
    animations: List[Dict[str, Any]]  # rotation, position, scale
    responsive_config: Dict[str, Any]  # mobile, tablet, desktop
    code: str  # Generated React component code


class UI3DSpecialist:
    """
    Expert agent for 3D UI component generation

    Generates production-ready React Three Fiber components with:
    - Optimized Three.js scenes
    - Smooth animations (60fps)
    - Interactive 3D elements
    - Post-processing effects
    - Responsive 3D layouts
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "src" / "components" / "3d"
        self.logger = logging.getLogger(f"{__name__}.UI3DSpecialist")

    def analyze_requirements(self, spec: Dict[str, Any]) -> ThreeJSScene:
        """
        Analyze component requirements and generate scene config

        Args:
            spec: Component specification from design/requirements

        Returns:
            ThreeJSScene configuration
        """
        self.logger.info(f"Analyzing 3D requirements: {spec.get('name', 'unnamed')}")

        # Detect scene type
        scene_type = self._detect_scene_type(spec)

        # Determine optimal camera and controls
        camera_type = "perspective" if scene_type in ["hero", "product"] else "orthographic"
        controls = self._determine_controls(spec, scene_type)

        # Generate lighting configuration
        lighting = self._generate_lighting(scene_type, spec.get("mood", "neutral"))

        # Extract 3D objects
        objects = self._extract_objects(spec)

        # Determine post-processing effects
        effects = self._determine_effects(spec, scene_type)

        # Performance mode based on complexity
        performance_mode = self._assess_performance_mode(objects, effects)

        return ThreeJSScene(
            scene_type=scene_type,
            camera_type=camera_type,
            controls=controls,
            lighting=lighting,
            objects=objects,
            effects=effects,
            physics_enabled=spec.get("physics", False),
            performance_mode=performance_mode
        )

    def generate_component(
        self,
        scene_config: ThreeJSScene,
        component_name: str,
        interactions: Optional[List[Dict[str, Any]]] = None,
        animations: Optional[List[Dict[str, Any]]] = None
    ) -> R3FComponent:
        """
        Generate React Three Fiber component from scene config

        Args:
            scene_config: Three.js scene configuration
            component_name: Name for the component
            interactions: User interaction handlers
            animations: Animation specifications

        Returns:
            R3FComponent with generated code
        """
        self.logger.info(f"Generating R3F component: {component_name}")

        interactions = interactions or []
        animations = animations or []

        # Generate responsive configuration
        responsive_config = self._generate_responsive_config(scene_config)

        # Generate component code
        code = self._generate_r3f_code(
            component_name,
            scene_config,
            interactions,
            animations,
            responsive_config
        )

        return R3FComponent(
            component_name=component_name,
            scene_config=scene_config,
            interactions=interactions,
            animations=animations,
            responsive_config=responsive_config,
            code=code
        )

    def _detect_scene_type(self, spec: Dict[str, Any]) -> str:
        """Detect scene type from specification"""
        keywords = spec.get("description", "").lower()

        if any(word in keywords for word in ["hero", "landing", "header"]):
            return "hero"
        elif any(word in keywords for word in ["product", "showcase", "display"]):
            return "product"
        elif any(word in keywords for word in ["background", "ambient", "backdrop"]):
            return "background"
        else:
            return "interactive"

    def _determine_controls(self, spec: Dict[str, Any], scene_type: str) -> str:
        """Determine appropriate camera controls"""
        if spec.get("user_controlled", False):
            return "orbit"
        elif scene_type == "interactive":
            return "trackball"
        elif scene_type == "background":
            return "none"
        else:
            return "orbit"

    def _generate_lighting(self, scene_type: str, mood: str) -> Dict[str, Any]:
        """Generate lighting configuration based on scene type and mood"""
        lighting_presets = {
            "hero": {
                "ambient": {"intensity": 0.5, "color": "#ffffff"},
                "directional": [
                    {"intensity": 1.0, "position": [5, 5, 5], "color": "#ffffff"}
                ],
                "point": [
                    {"intensity": 0.8, "position": [-5, 5, -5], "color": "#a78bfa"}
                ]
            },
            "product": {
                "ambient": {"intensity": 0.3, "color": "#ffffff"},
                "directional": [
                    {"intensity": 1.2, "position": [10, 10, 5], "color": "#ffffff"},
                    {"intensity": 0.6, "position": [-5, 5, -5], "color": "#60a5fa"}
                ]
            },
            "background": {
                "ambient": {"intensity": 0.8, "color": "#f0f0f0"},
                "directional": [
                    {"intensity": 0.4, "position": [0, 10, 0], "color": "#ffffff"}
                ]
            },
            "interactive": {
                "ambient": {"intensity": 0.6, "color": "#ffffff"},
                "point": [
                    {"intensity": 1.0, "position": [0, 5, 5], "color": "#8b5cf6"}
                ]
            }
        }

        return lighting_presets.get(scene_type, lighting_presets["interactive"])

    def _extract_objects(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract 3D objects from specification"""
        objects = []

        # Parse objects from spec
        for obj in spec.get("objects", []):
            objects.append({
                "type": obj.get("type", "box"),  # box, sphere, torus, custom
                "geometry": obj.get("geometry", {}),
                "material": self._generate_material(obj.get("material", {})),
                "position": obj.get("position", [0, 0, 0]),
                "rotation": obj.get("rotation", [0, 0, 0]),
                "scale": obj.get("scale", [1, 1, 1])
            })

        # If no objects specified, create default based on scene type
        if not objects:
            objects.append(self._create_default_object(spec))

        return objects

    def _generate_material(self, material_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Three.js material configuration"""
        material_type = material_spec.get("type", "standard")

        materials = {
            "standard": {
                "type": "MeshStandardMaterial",
                "color": material_spec.get("color", "#8b5cf6"),
                "metalness": material_spec.get("metalness", 0.5),
                "roughness": material_spec.get("roughness", 0.5),
                "transparent": material_spec.get("transparent", False),
                "opacity": material_spec.get("opacity", 1.0)
            },
            "glass": {
                "type": "MeshPhysicalMaterial",
                "color": material_spec.get("color", "#ffffff"),
                "metalness": 0.0,
                "roughness": 0.1,
                "transparent": True,
                "opacity": 0.2,
                "transmission": 0.9,
                "thickness": 0.5
            },
            "holographic": {
                "type": "MeshStandardMaterial",
                "color": material_spec.get("color", "#a78bfa"),
                "metalness": 1.0,
                "roughness": 0.0,
                "emissive": material_spec.get("color", "#a78bfa"),
                "emissiveIntensity": 0.5
            }
        }

        return materials.get(material_type, materials["standard"])

    def _create_default_object(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create default object based on scene type"""
        return {
            "type": "torus",
            "geometry": {"args": [1, 0.4, 16, 100]},
            "material": self._generate_material({"type": "holographic"}),
            "position": [0, 0, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        }

    def _determine_effects(self, spec: Dict[str, Any], scene_type: str) -> List[str]:
        """Determine post-processing effects"""
        effects = []

        # Base effects by scene type
        if scene_type == "hero":
            effects = ["bloom", "vignette"]
        elif scene_type == "product":
            effects = ["bloom", "depth_of_field"]
        elif scene_type == "interactive":
            effects = ["chromatic_aberration", "bloom"]

        # Add effects from spec
        if spec.get("glow", False):
            if "bloom" not in effects:
                effects.append("bloom")

        if spec.get("chromatic", False):
            if "chromatic_aberration" not in effects:
                effects.append("chromatic_aberration")

        return effects

    def _assess_performance_mode(
        self,
        objects: List[Dict[str, Any]],
        effects: List[str]
    ) -> str:
        """Assess appropriate performance mode"""
        complexity_score = len(objects) * 2 + len(effects) * 3

        if complexity_score < 10:
            return "high_quality"
        elif complexity_score < 20:
            return "balanced"
        else:
            return "performance"

    def _generate_responsive_config(self, scene_config: ThreeJSScene) -> Dict[str, Any]:
        """Generate responsive configuration for different screen sizes"""
        return {
            "mobile": {
                "camera_fov": 75,
                "pixel_ratio": 1,
                "shadow_quality": "low",
                "effects_enabled": False
            },
            "tablet": {
                "camera_fov": 60,
                "pixel_ratio": 1.5,
                "shadow_quality": "medium",
                "effects_enabled": len(scene_config.effects) <= 2
            },
            "desktop": {
                "camera_fov": 50,
                "pixel_ratio": 2,
                "shadow_quality": "high",
                "effects_enabled": True
            }
        }

    def _generate_r3f_code(
        self,
        component_name: str,
        scene_config: ThreeJSScene,
        interactions: List[Dict[str, Any]],
        animations: List[Dict[str, Any]],
        responsive_config: Dict[str, Any]
    ) -> str:
        """Generate React Three Fiber component code"""

        # Generate imports
        imports = self._generate_imports(scene_config)

        # Generate scene JSX
        scene_jsx = self._generate_scene_jsx(scene_config, interactions, animations)

        # Generate responsive logic
        responsive_logic = self._generate_responsive_logic(responsive_config)

        code = f'''import React, {{ useRef, useMemo }} from 'react';
import {{ Canvas, useFrame, useThree }} from '@react-three/fiber';
{imports}

/**
 * {component_name} - Advanced 3D UI Component
 *
 * Generated by UI3DSpecialist
 * Scene Type: {scene_config.scene_type}
 * Performance Mode: {scene_config.performance_mode}
 */

function Scene() {{
  const meshRef = useRef();
  const {{ viewport }} = useThree();

{responsive_logic}

  // Animation loop
  useFrame((state, delta) => {{
    if (meshRef.current) {{
      {self._generate_animation_code(animations)}
    }}
  }});

  return (
    <>
      {self._generate_lighting_jsx(scene_config.lighting)}
      {scene_jsx}
    </>
  );
}}

export default function {component_name}() {{
  return (
    <Canvas
      camera={{{{ position: [0, 0, 5], fov: 50 }}}}
      dpr={{[1, 2]}}
      gl={{{{ antialias: true }}}}
      style={{{{ width: '100%', height: '100vh' }}}}
    >
      <Scene />
      {self._generate_effects_jsx(scene_config.effects)}
    </Canvas>
  );
}}
'''

        return code

    def _generate_imports(self, scene_config: ThreeJSScene) -> str:
        """Generate necessary imports"""
        imports = ["import { OrbitControls } from '@react-three/drei';"]

        if scene_config.effects:
            imports.append("import { EffectComposer, Bloom, ChromaticAberration, Vignette } from '@react-three/postprocessing';")

        if any(obj['type'] == 'custom' for obj in scene_config.objects):
            imports.append("import { useGLTF } from '@react-three/drei';")

        return '\n'.join(imports)

    def _generate_scene_jsx(
        self,
        scene_config: ThreeJSScene,
        interactions: List[Dict[str, Any]],
        animations: List[Dict[str, Any]]
    ) -> str:
        """Generate scene JSX"""
        objects_jsx = []

        for i, obj in enumerate(scene_config.objects):
            position = obj['position']
            rotation = obj['rotation']
            scale = obj['scale']
            material = obj['material']

            # Generate event handlers
            handlers = self._generate_interaction_handlers(interactions, i)

            obj_jsx = f'''      <mesh
        ref={{meshRef}}
        position={{[{position[0]}, {position[1]}, {position[2]}]}}
        rotation={{[{rotation[0]}, {rotation[1]}, {rotation[2]}]}}
        scale={{[{scale[0]}, {scale[1]}, {scale[2]}]}}
        {handlers}
      >
        {self._generate_geometry_jsx(obj)}
        {self._generate_material_jsx(material)}
      </mesh>'''

            objects_jsx.append(obj_jsx)

        return '\n'.join(objects_jsx)

    def _generate_geometry_jsx(self, obj: Dict[str, Any]) -> str:
        """Generate geometry JSX"""
        geometry_type = obj['type']
        args = obj['geometry'].get('args', [1, 1, 1])

        geometry_map = {
            "box": f"<boxGeometry args={{[{', '.join(map(str, args))}]}} />",
            "sphere": f"<sphereGeometry args={{[{', '.join(map(str, args))}]}} />",
            "torus": f"<torusGeometry args={{[{', '.join(map(str, args))}]}} />",
            "plane": f"<planeGeometry args={{[{', '.join(map(str, args))}]}} />"
        }

        return geometry_map.get(geometry_type, geometry_map["box"])

    def _generate_material_jsx(self, material: Dict[str, Any]) -> str:
        """Generate material JSX"""
        mat_type = material['type']
        color = material['color']

        if mat_type == "MeshPhysicalMaterial":
            return f'''<meshPhysicalMaterial
          color="{color}"
          metalness={{{material['metalness']}}}
          roughness={{{material['roughness']}}}
          transparent={{true}}
          opacity={{{material['opacity']}}}
          transmission={{{material.get('transmission', 0)}}}
          thickness={{{material.get('thickness', 0)}}}
        />'''
        else:
            return f'''<meshStandardMaterial
          color="{color}"
          metalness={{{material.get('metalness', 0.5)}}}
          roughness={{{material.get('roughness', 0.5)}}}
          transparent={{{str(material.get('transparent', False)).lower()}}}
          opacity={{{material.get('opacity', 1.0)}}}
        />'''

    def _generate_interaction_handlers(
        self,
        interactions: List[Dict[str, Any]],
        object_index: int
    ) -> str:
        """Generate event handler props"""
        handlers = []

        for interaction in interactions:
            if interaction.get('target') == object_index or interaction.get('target') == 'all':
                event_type = interaction['type']
                handlers.append(f'{event_type}={{(e) => console.log("{event_type} on object {object_index}")}}')

        return ' '.join(handlers)

    def _generate_lighting_jsx(self, lighting: Dict[str, Any]) -> str:
        """Generate lighting JSX"""
        lights = []

        # Ambient light
        if 'ambient' in lighting:
            amb = lighting['ambient']
            lights.append(f'      <ambientLight intensity={{{amb["intensity"]}}} color="{amb["color"]}" />')

        # Directional lights
        for directional in lighting.get('directional', []):
            pos = directional['position']
            lights.append(f'      <directionalLight intensity={{{directional["intensity"]}}} position={{[{pos[0]}, {pos[1]}, {pos[2]}]}} color="{directional["color"]}" />')

        # Point lights
        for point in lighting.get('point', []):
            pos = point['position']
            lights.append(f'      <pointLight intensity={{{point["intensity"]}}} position={{[{pos[0]}, {pos[1]}, {pos[2]}]}} color="{point["color"]}" />')

        return '\n'.join(lights)

    def _generate_animation_code(self, animations: List[Dict[str, Any]]) -> str:
        """Generate animation code for useFrame"""
        if not animations:
            return "meshRef.current.rotation.x += 0.01;\n      meshRef.current.rotation.y += 0.01;"

        anim_lines = []
        for anim in animations:
            if anim['type'] == 'rotation':
                axis = anim.get('axis', 'y')
                speed = anim.get('speed', 0.01)
                anim_lines.append(f"meshRef.current.rotation.{axis} += {speed};")
            elif anim['type'] == 'position':
                anim_lines.append("meshRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.5;")

        return '\n      '.join(anim_lines)

    def _generate_effects_jsx(self, effects: List[str]) -> str:
        """Generate post-processing effects JSX"""
        if not effects:
            return ""

        effect_components = []

        if 'bloom' in effects:
            effect_components.append('<Bloom intensity={1.5} luminanceThreshold={0.9} />')

        if 'chromatic_aberration' in effects:
            effect_components.append('<ChromaticAberration offset={[0.002, 0.002]} />')

        if 'vignette' in effects:
            effect_components.append('<Vignette darkness={0.5} />')

        return f'''      <EffectComposer>
        {chr(10).join(f'        {ec}' for ec in effect_components)}
      </EffectComposer>'''

    def _generate_responsive_logic(self, responsive_config: Dict[str, Any]) -> str:
        """Generate responsive breakpoint logic"""
        return '''  // Responsive configuration
  const isMobile = viewport.width < 768;
  const isTablet = viewport.width >= 768 && viewport.width < 1024;
  const pixelRatio = isMobile ? 1 : isTablet ? 1.5 : 2;'''

    def save_component(self, component: R3FComponent) -> Path:
        """Save generated component to file"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        file_path = self.output_dir / f"{component.component_name}.tsx"

        with open(file_path, 'w') as f:
            f.write(component.code)

        self.logger.info(f"Saved 3D component to {file_path}")

        # Save configuration
        config_path = self.output_dir / f"{component.component_name}.config.json"
        with open(config_path, 'w') as f:
            json.dump({
                "scene_config": {
                    "scene_type": component.scene_config.scene_type,
                    "camera_type": component.scene_config.camera_type,
                    "controls": component.scene_config.controls,
                    "performance_mode": component.scene_config.performance_mode,
                    "effects": component.scene_config.effects
                },
                "responsive_config": component.responsive_config
            }, f, indent=2)

        return file_path

"""
Animation Specialist Agent

Expert in creating buttery-smooth 60fps animations using:
- Framer Motion for React animations
- GSAP for complex timeline animations
- React Spring for physics-based motion
- CSS animations with GPU acceleration
- Scroll-triggered animations
- Micro-interactions and transitions

Capabilities:
- Page transitions
- Scroll animations (parallax, reveal, sticky)
- Interactive hover effects
- Loading animations
- SVG path animations
- Orchestrated multi-element animations
- Performance optimization (will-change, transform3d)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnimationConfig:
    """Configuration for animation"""

    animation_type: str  # "transition", "scroll", "hover", "loading", "timeline"
    trigger: str  # "mount", "scroll", "hover", "click", "viewport"
    duration: float  # seconds
    easing: str  # "easeInOut", "spring", "linear", etc.
    properties: List[str]  # opacity, x, y, scale, rotate, etc.
    stagger: Optional[float] = None  # delay between elements
    repeat: int = 0  # 0 = no repeat, -1 = infinite
    delay: float = 0.0


@dataclass
class AnimationSequence:
    """Timeline-based animation sequence"""

    name: str
    steps: List[Dict[str, Any]]  # {target, animation, timing}
    total_duration: float
    auto_play: bool = True


@dataclass
class ScrollAnimation:
    """Scroll-triggered animation configuration"""

    trigger_element: str  # CSS selector
    start_trigger: str  # "top top", "center center", etc.
    end_trigger: str
    scrub: bool  # Tie animation to scroll position
    pin: bool  # Pin element during animation
    animation_config: AnimationConfig


@dataclass
class AnimatedComponent:
    """Animated React component specification"""

    component_name: str
    animation_library: str  # "framer-motion", "gsap", "react-spring"
    animations: List[AnimationConfig]
    sequences: List[AnimationSequence]
    scroll_animations: List[ScrollAnimation]
    performance_optimizations: List[str]
    code: str


class AnimationSpecialist:
    """
    Expert agent for creating smooth, performant animations

    Generates production-ready animated components with:
    - Framer Motion for declarative animations
    - GSAP for complex timelines
    - Scroll-triggered effects
    - 60fps performance optimizations
    - Responsive animation behavior
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "src" / "components" / "animated"
        self.logger = logging.getLogger(f"{__name__}.AnimationSpecialist")

    def analyze_animation_requirements(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze component spec and determine animation strategy

        Args:
            spec: Component specification with animation requirements

        Returns:
            Dict with animation strategy and configurations
        """
        self.logger.info(f"Analyzing animation requirements for {spec.get('name', 'unnamed')}")

        # Detect animation types needed
        animation_types = self._detect_animation_types(spec)

        # Choose appropriate library
        library = self._choose_animation_library(animation_types, spec)

        # Generate animation configs
        animations = []
        sequences = []
        scroll_animations = []

        for anim_type in animation_types:
            if anim_type.startswith("scroll_"):
                scroll_animations.append(self._create_scroll_animation(spec, anim_type))
            elif anim_type == "timeline":
                sequences.append(self._create_animation_sequence(spec))
            else:
                animations.append(self._create_animation_config(spec, anim_type))

        # Determine performance optimizations
        optimizations = self._determine_optimizations(animations, sequences, scroll_animations)

        return {
            "library": library,
            "animations": animations,
            "sequences": sequences,
            "scroll_animations": scroll_animations,
            "optimizations": optimizations
        }

    def generate_animated_component(
        self,
        component_name: str,
        strategy: Dict[str, Any],
        base_jsx: Optional[str] = None
    ) -> AnimatedComponent:
        """
        Generate animated component code

        Args:
            component_name: Name for component
            strategy: Animation strategy from analyze_animation_requirements
            base_jsx: Optional base component JSX to animate

        Returns:
            AnimatedComponent with generated code
        """
        self.logger.info(f"Generating animated component: {component_name}")

        library = strategy["library"]

        # Generate code based on library
        if library == "framer-motion":
            code = self._generate_framer_motion_code(
                component_name,
                strategy["animations"],
                strategy["optimizations"],
                base_jsx
            )
        elif library == "gsap":
            code = self._generate_gsap_code(
                component_name,
                strategy["sequences"],
                strategy["scroll_animations"],
                strategy["optimizations"],
                base_jsx
            )
        elif library == "react-spring":
            code = self._generate_react_spring_code(
                component_name,
                strategy["animations"],
                strategy["optimizations"],
                base_jsx
            )
        else:
            code = self._generate_css_animation_code(
                component_name,
                strategy["animations"],
                base_jsx
            )

        return AnimatedComponent(
            component_name=component_name,
            animation_library=library,
            animations=strategy["animations"],
            sequences=strategy["sequences"],
            scroll_animations=strategy["scroll_animations"],
            performance_optimizations=strategy["optimizations"],
            code=code
        )

    def _detect_animation_types(self, spec: Dict[str, Any]) -> List[str]:
        """Detect which animation types are needed"""
        types = []

        keywords = spec.get("description", "").lower()

        if any(word in keywords for word in ["scroll", "parallax", "reveal"]):
            types.append("scroll_reveal")

        if any(word in keywords for word in ["hover", "interactive"]):
            types.append("hover")

        if any(word in keywords for word in ["loading", "spinner"]):
            types.append("loading")

        if any(word in keywords for word in ["transition", "page"]):
            types.append("transition")

        if any(word in keywords for word in ["timeline", "sequence", "orchestrated"]):
            types.append("timeline")

        if any(word in keywords for word in ["stagger", "cascade"]):
            types.append("stagger")

        # Default to entrance animation if nothing specified
        if not types:
            types.append("entrance")

        return types

    def _choose_animation_library(
        self,
        animation_types: List[str],
        spec: Dict[str, Any]
    ) -> str:
        """Choose optimal animation library"""

        # Complex timelines → GSAP
        if "timeline" in animation_types or "scroll_" in str(animation_types):
            return "gsap"

        # Physics-based → React Spring
        if spec.get("physics", False) or "spring" in spec.get("easing", ""):
            return "react-spring"

        # Default: Framer Motion (best for React declarative animations)
        return "framer-motion"

    def _create_animation_config(
        self,
        spec: Dict[str, Any],
        anim_type: str
    ) -> AnimationConfig:
        """Create animation configuration for type"""

        configs = {
            "entrance": AnimationConfig(
                animation_type="entrance",
                trigger="mount",
                duration=0.6,
                easing="easeOut",
                properties=["opacity", "y"],
                delay=0.0
            ),
            "hover": AnimationConfig(
                animation_type="hover",
                trigger="hover",
                duration=0.3,
                easing="easeInOut",
                properties=["scale"],
                delay=0.0
            ),
            "loading": AnimationConfig(
                animation_type="loading",
                trigger="mount",
                duration=1.0,
                easing="linear",
                properties=["rotate"],
                repeat=-1,
                delay=0.0
            ),
            "stagger": AnimationConfig(
                animation_type="stagger",
                trigger="mount",
                duration=0.5,
                easing="easeOut",
                properties=["opacity", "y"],
                stagger=0.1,
                delay=0.0
            )
        }

        config = configs.get(anim_type, configs["entrance"])

        # Override with spec values if provided
        if "duration" in spec:
            config.duration = spec["duration"]
        if "easing" in spec:
            config.easing = spec["easing"]

        return config

    def _create_animation_sequence(self, spec: Dict[str, Any]) -> AnimationSequence:
        """Create timeline animation sequence"""

        steps = spec.get("timeline_steps", [
            {"target": ".element1", "animation": {"opacity": 1, "y": 0}, "timing": 0.0},
            {"target": ".element2", "animation": {"opacity": 1, "scale": 1}, "timing": 0.3},
            {"target": ".element3", "animation": {"opacity": 1, "x": 0}, "timing": 0.6}
        ])

        total_duration = max(
            step["timing"] + step.get("duration", 0.5)
            for step in steps
        )

        return AnimationSequence(
            name=spec.get("name", "sequence"),
            steps=steps,
            total_duration=total_duration,
            auto_play=spec.get("auto_play", True)
        )

    def _create_scroll_animation(
        self,
        spec: Dict[str, Any],
        anim_type: str
    ) -> ScrollAnimation:
        """Create scroll-triggered animation"""

        return ScrollAnimation(
            trigger_element=spec.get("trigger_selector", ".scroll-trigger"),
            start_trigger="top 80%",
            end_trigger="bottom 20%",
            scrub=anim_type == "scroll_scrub",
            pin=spec.get("pin", False),
            animation_config=AnimationConfig(
                animation_type="scroll_reveal",
                trigger="scroll",
                duration=1.0,
                easing="power2.out",
                properties=["opacity", "y"],
                delay=0.0
            )
        )

    def _determine_optimizations(
        self,
        animations: List[AnimationConfig],
        sequences: List[AnimationSequence],
        scroll_animations: List[ScrollAnimation]
    ) -> List[str]:
        """Determine performance optimizations needed"""

        optimizations = ["will-change"]  # Always use will-change

        # Check complexity
        total_animations = len(animations) + len(sequences) + len(scroll_animations)

        if total_animations > 5:
            optimizations.append("requestAnimationFrame")

        # Check for transform animations
        all_properties = []
        for anim in animations:
            all_properties.extend(anim.properties)

        if any(prop in all_properties for prop in ["x", "y", "scale", "rotate"]):
            optimizations.append("transform3d")
            optimizations.append("gpu-acceleration")

        # Scroll animations need Intersection Observer
        if scroll_animations:
            optimizations.append("intersection-observer")

        return optimizations

    def _generate_framer_motion_code(
        self,
        component_name: str,
        animations: List[AnimationConfig],
        optimizations: List[str],
        base_jsx: Optional[str]
    ) -> str:
        """Generate Framer Motion component code"""

        imports = "import React from 'react';\nimport { motion, useAnimation, AnimatePresence } from 'framer-motion';"

        # Generate variants
        variants = self._generate_framer_variants(animations)

        # Generate motion component
        if base_jsx:
            motion_jsx = self._wrap_with_motion(base_jsx, animations)
        else:
            motion_jsx = self._generate_default_motion_jsx(animations)

        code = f'''{imports}

/**
 * {component_name} - Animated with Framer Motion
 *
 * Generated by AnimationSpecialist
 * Optimizations: {", ".join(optimizations)}
 */

{variants}

export default function {component_name}() {{
  return (
    <AnimatePresence>
      {motion_jsx}
    </AnimatePresence>
  );
}}
'''

        return code

    def _generate_framer_variants(self, animations: List[AnimationConfig]) -> str:
        """Generate Framer Motion variants"""

        variants_code = []

        for i, anim in enumerate(animations):
            variant_name = f"{anim.animation_type}Variants"

            initial = {}
            animate = {}

            for prop in anim.properties:
                if prop == "opacity":
                    initial["opacity"] = 0
                    animate["opacity"] = 1
                elif prop == "y":
                    initial["y"] = 20
                    animate["y"] = 0
                elif prop == "x":
                    initial["x"] = -20
                    animate["x"] = 0
                elif prop == "scale":
                    initial["scale"] = 0.9
                    animate["scale"] = 1
                elif prop == "rotate":
                    initial["rotate"] = 0
                    animate["rotate"] = 360

            transition = {
                "duration": anim.duration,
                "ease": self._map_easing_to_framer(anim.easing)
            }

            if anim.stagger:
                transition["staggerChildren"] = anim.stagger

            if anim.delay:
                transition["delay"] = anim.delay

            if anim.repeat == -1:
                transition["repeat"] = "Infinity"
                transition["repeatType"] = "loop"

            variants_code.append(f'''const {variant_name} = {{
  initial: {json.dumps(initial)},
  animate: {json.dumps(animate)},
  transition: {json.dumps(transition)}
}};''')

        return '\n\n'.join(variants_code)

    def _map_easing_to_framer(self, easing: str) -> str:
        """Map easing name to Framer Motion format"""

        easing_map = {
            "easeInOut": "easeInOut",
            "easeOut": "easeOut",
            "easeIn": "easeIn",
            "linear": "linear",
            "spring": [0.6, 0.05, 0.01, 0.9]
        }

        return easing_map.get(easing, "easeInOut")

    def _wrap_with_motion(
        self,
        jsx: str,
        animations: List[AnimationConfig]
    ) -> str:
        """Wrap existing JSX with motion components"""

        # Simple wrapper for now
        primary_anim = animations[0] if animations else None

        if primary_anim:
            variant_name = f"{primary_anim.animation_type}Variants"
            return f'''      <motion.div
        variants={{{variant_name}}}
        initial="initial"
        animate="animate"
      >
        {jsx}
      </motion.div>'''
        else:
            return f"      <motion.div>{jsx}</motion.div>"

    def _generate_default_motion_jsx(self, animations: List[AnimationConfig]) -> str:
        """Generate default motion JSX"""

        primary_anim = animations[0] if animations else AnimationConfig(
            animation_type="entrance",
            trigger="mount",
            duration=0.6,
            easing="easeOut",
            properties=["opacity", "y"]
        )

        variant_name = f"{primary_anim.animation_type}Variants"

        return f'''      <motion.div
        variants={{{variant_name}}}
        initial="initial"
        animate="animate"
        style={{{{
          padding: '2rem',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '1rem',
          color: 'white'
        }}}}
      >
        <h2>Animated Component</h2>
        <p>Smooth entrance animation with Framer Motion</p>
      </motion.div>'''

    def _generate_gsap_code(
        self,
        component_name: str,
        sequences: List[AnimationSequence],
        scroll_animations: List[ScrollAnimation],
        optimizations: List[str],
        base_jsx: Optional[str]
    ) -> str:
        """Generate GSAP animation code"""

        imports = '''import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);'''

        # Generate timeline code
        timeline_code = self._generate_gsap_timeline(sequences)

        # Generate scroll trigger code
        scroll_code = self._generate_gsap_scroll_triggers(scroll_animations)

        code = f'''{imports}

/**
 * {component_name} - Animated with GSAP
 *
 * Generated by AnimationSpecialist
 * Features: Timeline animations, Scroll triggers
 * Optimizations: {", ".join(optimizations)}
 */

export default function {component_name}() {{
  const containerRef = useRef(null);

  useEffect(() => {{
    const ctx = gsap.context(() => {{
{timeline_code}

{scroll_code}
    }}, containerRef);

    return () => ctx.revert();
  }}, []);

  return (
    <div ref={{containerRef}} className="animated-container">
      {base_jsx or self._generate_default_gsap_jsx()}
    </div>
  );
}}
'''

        return code

    def _generate_gsap_timeline(self, sequences: List[AnimationSequence]) -> str:
        """Generate GSAP timeline code"""

        if not sequences:
            return "      // No timeline animations"

        timeline_code = []

        for seq in sequences:
            timeline_code.append(f"      // Timeline: {seq.name}")
            timeline_code.append(f"      const tl = gsap.timeline({{ paused: {str(not seq.auto_play).lower()} }});")

            for step in seq.steps:
                target = step["target"]
                props = step["animation"]
                timing = step.get("timing", 0)

                timeline_code.append(
                    f"      tl.to('{target}', {json.dumps(props)}, {timing});"
                )

            timeline_code.append("")

        return '\n'.join(timeline_code)

    def _generate_gsap_scroll_triggers(self, scroll_animations: List[ScrollAnimation]) -> str:
        """Generate GSAP ScrollTrigger code"""

        if not scroll_animations:
            return "      // No scroll animations"

        scroll_code = []

        for scroll_anim in scroll_animations:
            trigger = scroll_anim.trigger_element
            config = scroll_anim.animation_config

            props = {}
            for prop in config.properties:
                if prop == "opacity":
                    props["opacity"] = 1
                elif prop == "y":
                    props["y"] = 0

            scroll_config = {
                "trigger": trigger,
                "start": scroll_anim.start_trigger,
                "end": scroll_anim.end_trigger,
                "scrub": scroll_anim.scrub,
                "pin": scroll_anim.pin
            }

            scroll_code.append(f'''      gsap.from('{trigger}', {{
        ...{json.dumps(props)},
        scrollTrigger: {json.dumps(scroll_config, indent=10)}
      }});''')

        return '\n\n'.join(scroll_code)

    def _generate_default_gsap_jsx(self) -> str:
        """Generate default GSAP JSX"""

        return '''      <div className="element1" style={{ opacity: 0, transform: 'translateY(20px)' }}>
        <h2>GSAP Animated Element 1</h2>
      </div>
      <div className="element2" style={{ opacity: 0, transform: 'scale(0.9)' }}>
        <h2>GSAP Animated Element 2</h2>
      </div>
      <div className="element3" style={{ opacity: 0, transform: 'translateX(-20px)' }}>
        <h2>GSAP Animated Element 3</h2>
      </div>'''

    def _generate_react_spring_code(
        self,
        component_name: str,
        animations: List[AnimationConfig],
        optimizations: List[str],
        base_jsx: Optional[str]
    ) -> str:
        """Generate React Spring animation code"""

        imports = "import React from 'react';\nimport { useSpring, animated, config } from '@react-spring/web';"

        # Generate spring config
        spring_code = self._generate_spring_config(animations)

        code = f'''{imports}

/**
 * {component_name} - Animated with React Spring
 *
 * Generated by AnimationSpecialist
 * Physics-based animations
 * Optimizations: {", ".join(optimizations)}
 */

export default function {component_name}() {{
{spring_code}

  return (
    <animated.div style={{springs}}>
      {base_jsx or self._generate_default_spring_jsx()}
    </animated.div>
  );
}}
'''

        return code

    def _generate_spring_config(self, animations: List[AnimationConfig]) -> str:
        """Generate React Spring configuration"""

        primary_anim = animations[0] if animations else AnimationConfig(
            animation_type="entrance",
            trigger="mount",
            duration=0.6,
            easing="spring",
            properties=["opacity", "y"]
        )

        from_props = {}
        to_props = {}

        for prop in primary_anim.properties:
            if prop == "opacity":
                from_props["opacity"] = 0
                to_props["opacity"] = 1
            elif prop == "y":
                from_props["transform"] = "translateY(20px)"
                to_props["transform"] = "translateY(0px)"
            elif prop == "scale":
                from_props["transform"] = "scale(0.9)"
                to_props["transform"] = "scale(1)"

        return f'''  const springs = useSpring({{
    from: {json.dumps(from_props)},
    to: {json.dumps(to_props)},
    config: config.gentle
  }});'''

    def _generate_default_spring_jsx(self) -> str:
        """Generate default React Spring JSX"""

        return '''      <div style={{ padding: '2rem', background: '#667eea', borderRadius: '1rem', color: 'white' }}>
        <h2>Spring Animated Component</h2>
        <p>Physics-based animation with React Spring</p>
      </div>'''

    def _generate_css_animation_code(
        self,
        component_name: str,
        animations: List[AnimationConfig],
        base_jsx: Optional[str]
    ) -> str:
        """Generate CSS animation code (fallback)"""

        # Generate CSS keyframes
        keyframes = self._generate_css_keyframes(animations)

        # Generate component
        code = f'''import React from 'react';
import './{ component_name}.css';

/**
 * {component_name} - CSS Animations
 *
 * Generated by AnimationSpecialist
 * Lightweight CSS-only animations
 */

export default function {component_name}() {{
  return (
    <div className="css-animated">
      {base_jsx or '<div className="animated-element"><h2>CSS Animated</h2></div>'}
    </div>
  );
}}

/* CSS (save to {component_name}.css) */
/*
{keyframes}
*/
'''

        return code

    def _generate_css_keyframes(self, animations: List[AnimationConfig]) -> str:
        """Generate CSS keyframes"""

        primary_anim = animations[0] if animations else AnimationConfig(
            animation_type="entrance",
            trigger="mount",
            duration=0.6,
            easing="ease-out",
            properties=["opacity", "y"]
        )

        keyframe_name = f"{primary_anim.animation_type}Animation"

        from_props = []
        to_props = []

        for prop in primary_anim.properties:
            if prop == "opacity":
                from_props.append("opacity: 0;")
                to_props.append("opacity: 1;")
            elif prop == "y":
                from_props.append("transform: translateY(20px);")
                to_props.append("transform: translateY(0);")

        return f'''@keyframes {keyframe_name} {{
  from {{
    {chr(10).join('    ' + p for p in from_props)}
  }}
  to {{
    {chr(10).join('    ' + p for p in to_props)}
  }}
}}

.animated-element {{
  animation: {keyframe_name} {primary_anim.duration}s {primary_anim.easing};
}}'''

    def save_component(self, component: AnimatedComponent) -> Path:
        """Save animated component to file"""

        self.output_dir.mkdir(parents=True, exist_ok=True)

        file_path = self.output_dir / f"{component.component_name}.tsx"

        with open(file_path, 'w') as f:
            f.write(component.code)

        self.logger.info(f"Saved animated component to {file_path}")

        # Save configuration
        config_path = self.output_dir / f"{component.component_name}.config.json"
        with open(config_path, 'w') as f:
            json.dump({
                "library": component.animation_library,
                "optimizations": component.performance_optimizations,
                "animations_count": len(component.animations),
                "sequences_count": len(component.sequences),
                "scroll_animations_count": len(component.scroll_animations)
            }, f, indent=2)

        return file_path

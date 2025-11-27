"""
Glassmorphism Designer Agent

Expert in creating stunning glassmorphism UI with:
- Advanced CSS backdrop-filter effects
- Tailwind CSS v4 for utility-first styling
- Dark mode support with automatic theming
- Responsive glass effects
- Performance-optimized blur and transparency
- Color theory for glass tints

Capabilities:
- Glassmorphic cards and panels
- Floating glass navigation
- Glass modals and overlays
- Gradient glass backgrounds
- Frosted glass effects
- Multi-layer glass depth
- Theme-aware glass tints
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import logging
import colorsys

logger = logging.getLogger(__name__)


@dataclass
class GlassEffect:
    """Glass morphism effect configuration"""

    blur: int  # backdrop blur in pixels (4-24)
    opacity: float  # background opacity (0.0-1.0)
    border_opacity: float  # border opacity (0.0-1.0)
    saturation: int  # backdrop saturation (100-200)
    brightness: int  # backdrop brightness (100-150)
    tint_color: str  # rgba color for glass tint
    shadow: str  # box-shadow configuration
    border_gradient: bool  # use gradient border


@dataclass
class GlassComponent:
    """Glassmorphic component specification"""

    component_type: str  # "card", "nav", "modal", "panel", "button"
    glass_effect: GlassEffect
    dark_mode_effect: GlassEffect  # Different effect for dark mode
    responsive_adjustments: Dict[str, GlassEffect]  # breakpoint → effect
    gradient_background: Optional[str] = None
    animation_on_hover: bool = True


@dataclass
class GlassDesignSystem:
    """Complete glassmorphism design system"""

    primary_glass: GlassEffect
    secondary_glass: GlassEffect
    accent_glass: GlassEffect
    color_palette: Dict[str, str]  # Light/dark mode colors
    spacing_system: Dict[str, str]  # Tailwind spacing tokens
    typography: Dict[str, str]  # Font configurations
    components: List[GlassComponent]
    css_code: str
    tailwind_config: str


class GlassmorphismDesigner:
    """
    Expert agent for glassmorphism UI design

    Generates production-ready glassmorphic components with:
    - Advanced backdrop-filter effects
    - Automatic dark mode support
    - Responsive glass adjustments
    - Performance optimizations
    - Tailwind CSS integration
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "src" / "styles"
        self.components_dir = project_root / "src" / "components" / "glass"
        self.logger = logging.getLogger(f"{__name__}.GlassmorphismDesigner")

    def create_design_system(
        self,
        brand_colors: Optional[Dict[str, str]] = None,
        style: str = "modern"  # "modern", "elegant", "bold", "minimal"
    ) -> GlassDesignSystem:
        """
        Create complete glassmorphism design system

        Args:
            brand_colors: Optional brand color palette
            style: Design style preset

        Returns:
            Complete GlassDesignSystem
        """
        self.logger.info(f"Creating glassmorphism design system: {style}")

        # Generate color palette
        color_palette = self._generate_color_palette(brand_colors, style)

        # Create glass effect presets
        primary_glass = self._create_glass_preset("primary", style, color_palette)
        secondary_glass = self._create_glass_preset("secondary", style, color_palette)
        accent_glass = self._create_glass_preset("accent", style, color_palette)

        # Generate spacing and typography
        spacing_system = self._generate_spacing_system()
        typography = self._generate_typography(style)

        # Generate CSS code
        css_code = self._generate_design_system_css(
            primary_glass,
            secondary_glass,
            accent_glass,
            color_palette,
            spacing_system,
            typography
        )

        # Generate Tailwind config
        tailwind_config = self._generate_tailwind_config(
            color_palette,
            spacing_system
        )

        return GlassDesignSystem(
            primary_glass=primary_glass,
            secondary_glass=secondary_glass,
            accent_glass=accent_glass,
            color_palette=color_palette,
            spacing_system=spacing_system,
            typography=typography,
            components=[],
            css_code=css_code,
            tailwind_config=tailwind_config
        )

    def design_component(
        self,
        component_type: str,
        design_system: GlassDesignSystem,
        custom_spec: Optional[Dict[str, Any]] = None
    ) -> GlassComponent:
        """
        Design glassmorphic component

        Args:
            component_type: Type of component (card, nav, modal, etc.)
            design_system: Design system to use
            custom_spec: Optional custom specifications

        Returns:
            GlassComponent specification
        """
        self.logger.info(f"Designing glass component: {component_type}")

        custom_spec = custom_spec or {}

        # Select appropriate glass effect
        glass_effect = self._select_glass_effect(
            component_type,
            design_system,
            custom_spec
        )

        # Create dark mode variant
        dark_mode_effect = self._create_dark_mode_effect(glass_effect)

        # Create responsive variants
        responsive_adjustments = self._create_responsive_variants(glass_effect)

        # Generate gradient background if needed
        gradient_background = None
        if custom_spec.get("gradient", False):
            gradient_background = self._generate_gradient(design_system.color_palette)

        return GlassComponent(
            component_type=component_type,
            glass_effect=glass_effect,
            dark_mode_effect=dark_mode_effect,
            responsive_adjustments=responsive_adjustments,
            gradient_background=gradient_background,
            animation_on_hover=custom_spec.get("hover_animation", True)
        )

    def generate_component_code(
        self,
        component: GlassComponent,
        component_name: str,
        design_system: GlassDesignSystem
    ) -> str:
        """
        Generate React component code with glassmorphism styling

        Args:
            component: GlassComponent specification
            component_name: Name for the component
            design_system: Design system context

        Returns:
            Generated React component code
        """
        self.logger.info(f"Generating code for {component_name}")

        # Generate CSS classes
        css_classes = self._generate_component_css(component, component_name)

        # Generate React component
        jsx_code = self._generate_component_jsx(
            component,
            component_name,
            design_system
        )

        code = f'''import React from 'react';
import './glass.css';

/**
 * {component_name} - Glassmorphic {component.component_type.capitalize()}
 *
 * Generated by GlassmorphismDesigner
 * Features: Advanced backdrop-filter, dark mode support, responsive
 */

{jsx_code}

/* CSS (add to glass.css) */
/*
{css_classes}
*/
'''

        return code

    def _generate_color_palette(
        self,
        brand_colors: Optional[Dict[str, str]],
        style: str
    ) -> Dict[str, str]:
        """Generate complete color palette for light and dark modes"""

        if brand_colors:
            primary = brand_colors.get("primary", "#8b5cf6")
            secondary = brand_colors.get("secondary", "#06b6d4")
        else:
            # Default color schemes by style
            style_colors = {
                "modern": {"primary": "#8b5cf6", "secondary": "#06b6d4"},
                "elegant": {"primary": "#a78bfa", "secondary": "#c084fc"},
                "bold": {"primary": "#f59e0b", "secondary": "#ef4444"},
                "minimal": {"primary": "#6366f1", "secondary": "#8b5cf6"}
            }
            primary = style_colors[style]["primary"]
            secondary = style_colors[style]["secondary"]

        return {
            # Light mode
            "light_bg": "#ffffff",
            "light_surface": "#f9fafb",
            "light_border": "#e5e7eb",
            "light_text": "#111827",
            "light_text_secondary": "#6b7280",
            "light_primary": primary,
            "light_secondary": secondary,

            # Dark mode
            "dark_bg": "#0f172a",
            "dark_surface": "#1e293b",
            "dark_border": "#334155",
            "dark_text": "#f1f5f9",
            "dark_text_secondary": "#94a3b8",
            "dark_primary": self._lighten_color(primary, 0.1),
            "dark_secondary": self._lighten_color(secondary, 0.1),

            # Glass tints
            "glass_tint_light": self._rgba_from_hex(primary, 0.05),
            "glass_tint_dark": self._rgba_from_hex(primary, 0.1),
            "glass_border_light": self._rgba_from_hex("#ffffff", 0.2),
            "glass_border_dark": self._rgba_from_hex("#ffffff", 0.1)
        }

    def _create_glass_preset(
        self,
        preset_type: str,
        style: str,
        color_palette: Dict[str, str]
    ) -> GlassEffect:
        """Create glass effect preset"""

        presets = {
            "primary": {
                "modern": GlassEffect(
                    blur=16,
                    opacity=0.15,
                    border_opacity=0.2,
                    saturation=120,
                    brightness=110,
                    tint_color=color_palette["glass_tint_light"],
                    shadow="0 8px 32px 0 rgba(31, 38, 135, 0.15)",
                    border_gradient=True
                ),
                "elegant": GlassEffect(
                    blur=20,
                    opacity=0.1,
                    border_opacity=0.15,
                    saturation=110,
                    brightness=105,
                    tint_color=color_palette["glass_tint_light"],
                    shadow="0 8px 32px 0 rgba(31, 38, 135, 0.1)",
                    border_gradient=True
                ),
                "bold": GlassEffect(
                    blur=12,
                    opacity=0.2,
                    border_opacity=0.3,
                    saturation=130,
                    brightness=115,
                    tint_color=color_palette["glass_tint_light"],
                    shadow="0 8px 32px 0 rgba(31, 38, 135, 0.2)",
                    border_gradient=False
                ),
                "minimal": GlassEffect(
                    blur=24,
                    opacity=0.08,
                    border_opacity=0.1,
                    saturation=100,
                    brightness=100,
                    tint_color=color_palette["glass_tint_light"],
                    shadow="0 4px 16px 0 rgba(31, 38, 135, 0.08)",
                    border_gradient=False
                )
            },
            "secondary": {
                "modern": GlassEffect(
                    blur=12,
                    opacity=0.1,
                    border_opacity=0.15,
                    saturation=110,
                    brightness=105,
                    tint_color=color_palette["glass_tint_light"],
                    shadow="0 4px 16px 0 rgba(31, 38, 135, 0.1)",
                    border_gradient=False
                )
            },
            "accent": {
                "modern": GlassEffect(
                    blur=8,
                    opacity=0.25,
                    border_opacity=0.3,
                    saturation=140,
                    brightness=120,
                    tint_color=color_palette["glass_tint_light"],
                    shadow="0 8px 24px 0 rgba(139, 92, 246, 0.2)",
                    border_gradient=True
                )
            }
        }

        return presets.get(preset_type, {}).get(style, presets["primary"]["modern"])

    def _create_dark_mode_effect(self, light_effect: GlassEffect) -> GlassEffect:
        """Create dark mode variant of glass effect"""

        return GlassEffect(
            blur=light_effect.blur + 4,  # Slightly more blur in dark mode
            opacity=light_effect.opacity + 0.05,  # Slightly more opacity
            border_opacity=light_effect.border_opacity - 0.05,  # Less border
            saturation=light_effect.saturation - 10,
            brightness=light_effect.brightness - 10,
            tint_color=light_effect.tint_color.replace("0.05", "0.1"),  # Stronger tint
            shadow=light_effect.shadow.replace("0.15", "0.3"),  # Stronger shadow
            border_gradient=light_effect.border_gradient
        )

    def _create_responsive_variants(self, base_effect: GlassEffect) -> Dict[str, GlassEffect]:
        """Create responsive variants for different screen sizes"""

        return {
            "mobile": GlassEffect(
                blur=base_effect.blur - 4,  # Less blur on mobile for performance
                opacity=base_effect.opacity + 0.05,
                border_opacity=base_effect.border_opacity,
                saturation=base_effect.saturation,
                brightness=base_effect.brightness,
                tint_color=base_effect.tint_color,
                shadow=base_effect.shadow.replace("32px", "16px"),
                border_gradient=False  # Disable gradient on mobile
            ),
            "tablet": base_effect,  # Same as base
            "desktop": GlassEffect(
                blur=base_effect.blur + 4,  # More blur on desktop
                opacity=base_effect.opacity - 0.02,
                border_opacity=base_effect.border_opacity,
                saturation=base_effect.saturation + 10,
                brightness=base_effect.brightness + 5,
                tint_color=base_effect.tint_color,
                shadow=base_effect.shadow,
                border_gradient=base_effect.border_gradient
            )
        }

    def _select_glass_effect(
        self,
        component_type: str,
        design_system: GlassDesignSystem,
        custom_spec: Dict[str, Any]
    ) -> GlassEffect:
        """Select appropriate glass effect for component type"""

        effect_map = {
            "card": design_system.primary_glass,
            "panel": design_system.primary_glass,
            "nav": design_system.secondary_glass,
            "modal": design_system.primary_glass,
            "button": design_system.accent_glass,
            "overlay": GlassEffect(
                blur=24,
                opacity=0.4,
                border_opacity=0.0,
                saturation=100,
                brightness=90,
                tint_color="rgba(0, 0, 0, 0.3)",
                shadow="none",
                border_gradient=False
            )
        }

        return effect_map.get(component_type, design_system.primary_glass)

    def _generate_gradient(self, color_palette: Dict[str, str]) -> str:
        """Generate gradient background"""

        primary = color_palette["light_primary"]
        secondary = color_palette["light_secondary"]

        return f"linear-gradient(135deg, {primary} 0%, {secondary} 100%)"

    def _generate_spacing_system(self) -> Dict[str, str]:
        """Generate spacing system"""

        return {
            "xs": "0.5rem",  # 8px
            "sm": "0.75rem",  # 12px
            "md": "1rem",  # 16px
            "lg": "1.5rem",  # 24px
            "xl": "2rem",  # 32px
            "2xl": "3rem",  # 48px
            "3xl": "4rem"  # 64px
        }

    def _generate_typography(self, style: str) -> Dict[str, str]:
        """Generate typography system"""

        typography_systems = {
            "modern": {
                "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
                "heading_weight": "700",
                "body_weight": "400",
                "line_height": "1.6"
            },
            "elegant": {
                "font_family": "'Playfair Display', Georgia, serif",
                "heading_weight": "600",
                "body_weight": "400",
                "line_height": "1.7"
            },
            "bold": {
                "font_family": "'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif",
                "heading_weight": "800",
                "body_weight": "500",
                "line_height": "1.5"
            },
            "minimal": {
                "font_family": "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif",
                "heading_weight": "500",
                "body_weight": "300",
                "line_height": "1.8"
            }
        }

        return typography_systems.get(style, typography_systems["modern"])

    def _generate_design_system_css(
        self,
        primary_glass: GlassEffect,
        secondary_glass: GlassEffect,
        accent_glass: GlassEffect,
        color_palette: Dict[str, str],
        spacing_system: Dict[str, str],
        typography: Dict[str, str]
    ) -> str:
        """Generate complete design system CSS"""

        css = f'''/* Glassmorphism Design System */
/* Generated by GlassmorphismDesigner */

:root {{
  /* Colors - Light Mode */
  --color-bg: {color_palette["light_bg"]};
  --color-surface: {color_palette["light_surface"]};
  --color-border: {color_palette["light_border"]};
  --color-text: {color_palette["light_text"]};
  --color-text-secondary: {color_palette["light_text_secondary"]};
  --color-primary: {color_palette["light_primary"]};
  --color-secondary: {color_palette["light_secondary"]};

  /* Glass Effects */
  --glass-tint: {color_palette["glass_tint_light"]};
  --glass-border: {color_palette["glass_border_light"]};

  /* Typography */
  --font-family: {typography["font_family"]};
  --font-weight-heading: {typography["heading_weight"]};
  --font-weight-body: {typography["body_weight"]};
  --line-height: {typography["line_height"]};
}}

@media (prefers-color-scheme: dark) {{
  :root {{
    --color-bg: {color_palette["dark_bg"]};
    --color-surface: {color_palette["dark_surface"]};
    --color-border: {color_palette["dark_border"]};
    --color-text: {color_palette["dark_text"]};
    --color-text-secondary: {color_palette["dark_text_secondary"]};
    --color-primary: {color_palette["dark_primary"]};
    --color-secondary: {color_palette["dark_secondary"]};
    --glass-tint: {color_palette["glass_tint_dark"]};
    --glass-border: {color_palette["glass_border_dark"]};
  }}
}}

/* Base Glass Effects */
.glass-primary {{
  background: {primary_glass.tint_color};
  backdrop-filter: blur({primary_glass.blur}px) saturate({primary_glass.saturation}%) brightness({primary_glass.brightness}%);
  -webkit-backdrop-filter: blur({primary_glass.blur}px) saturate({primary_glass.saturation}%) brightness({primary_glass.brightness}%);
  border: 1px solid rgba(255, 255, 255, {primary_glass.border_opacity});
  box-shadow: {primary_glass.shadow};
  border-radius: 1rem;
}}

.glass-secondary {{
  background: {secondary_glass.tint_color};
  backdrop-filter: blur({secondary_glass.blur}px) saturate({secondary_glass.saturation}%) brightness({secondary_glass.brightness}%);
  -webkit-backdrop-filter: blur({secondary_glass.blur}px) saturate({secondary_glass.saturation}%) brightness({secondary_glass.brightness}%);
  border: 1px solid rgba(255, 255, 255, {secondary_glass.border_opacity});
  box-shadow: {secondary_glass.shadow};
  border-radius: 0.75rem;
}}

.glass-accent {{
  background: {accent_glass.tint_color};
  backdrop-filter: blur({accent_glass.blur}px) saturate({accent_glass.saturation}%) brightness({accent_glass.brightness}%);
  -webkit-backdrop-filter: blur({accent_glass.blur}px) saturate({accent_glass.saturation}%) brightness({accent_glass.brightness}%);
  border: 1px solid rgba(255, 255, 255, {accent_glass.border_opacity});
  box-shadow: {accent_glass.shadow};
  border-radius: 0.5rem;
}}

/* Hover Effects */
.glass-hover:hover {{
  transform: translateY(-2px);
  box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

/* Gradient Borders */
.glass-gradient-border {{
  position: relative;
  background: linear-gradient(var(--color-surface), var(--color-surface)) padding-box,
              linear-gradient(135deg, rgba(255,255,255,0.4), rgba(255,255,255,0.1)) border-box;
  border: 2px solid transparent;
}}
'''

        return css

    def _generate_tailwind_config(
        self,
        color_palette: Dict[str, str],
        spacing_system: Dict[str, str]
    ) -> str:
        """Generate Tailwind configuration"""

        config = f'''// tailwind.config.js
// Generated by GlassmorphismDesigner

module.exports = {{
  darkMode: 'class',
  theme: {{
    extend: {{
      colors: {{
        primary: {{
          light: '{color_palette["light_primary"]}',
          dark: '{color_palette["dark_primary"]}'
        }},
        secondary: {{
          light: '{color_palette["light_secondary"]}',
          dark: '{color_palette["dark_secondary"]}'
        }}
      }},
      backdropBlur: {{
        'xs': '2px',
        'sm': '4px',
        'md': '12px',
        'lg': '16px',
        'xl': '24px',
        '2xl': '40px'
      }},
      backdropSaturate: {{
        110: '1.1',
        120: '1.2',
        130: '1.3',
        140: '1.4'
      }},
      backdropBrightness: {{
        105: '1.05',
        110: '1.1',
        115: '1.15',
        120: '1.2'
      }}
    }}
  }},
  plugins: [
    require('@tailwindcss/forms'),
  ]
}}
'''

        return config

    def _generate_component_css(
        self,
        component: GlassComponent,
        component_name: str
    ) -> str:
        """Generate CSS for specific component"""

        effect = component.glass_effect
        dark_effect = component.dark_mode_effect

        css = f'''.{component_name} {{
  background: {effect.tint_color};
  backdrop-filter: blur({effect.blur}px) saturate({effect.saturation}%) brightness({effect.brightness}%);
  -webkit-backdrop-filter: blur({effect.blur}px) saturate({effect.saturation}%) brightness({effect.brightness}%);
  border: 1px solid rgba(255, 255, 255, {effect.border_opacity});
  box-shadow: {effect.shadow};
  border-radius: 1rem;
  padding: 1.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}

@media (prefers-color-scheme: dark) {{
  .{component_name} {{
    background: {dark_effect.tint_color};
    backdrop-filter: blur({dark_effect.blur}px) saturate({dark_effect.saturation}%) brightness({dark_effect.brightness}%);
    -webkit-backdrop-filter: blur({dark_effect.blur}px) saturate({dark_effect.saturation}%) brightness({dark_effect.brightness}%);
    border: 1px solid rgba(255, 255, 255, {dark_effect.border_opacity});
    box-shadow: {dark_effect.shadow};
  }}
}}

{self._generate_hover_css(component_name, component.animation_on_hover)}

/* Responsive Adjustments */
@media (max-width: 768px) {{
  .{component_name} {{
    backdrop-filter: blur({component.responsive_adjustments["mobile"].blur}px);
    -webkit-backdrop-filter: blur({component.responsive_adjustments["mobile"].blur}px);
  }}
}}
'''

        if component.gradient_background:
            css += f'''
.{component_name}::before {{
  content: '';
  position: absolute;
  inset: 0;
  background: {component.gradient_background};
  opacity: 0.1;
  border-radius: 1rem;
  z-index: -1;
}}
'''

        return css

    def _generate_hover_css(self, component_name: str, enabled: bool) -> str:
        """Generate hover animation CSS"""

        if not enabled:
            return ""

        return f'''.{component_name}:hover {{
  transform: translateY(-4px);
  box-shadow: 0 16px 48px 0 rgba(31, 38, 135, 0.25);
}}'''

    def _generate_component_jsx(
        self,
        component: GlassComponent,
        component_name: str,
        design_system: GlassDesignSystem
    ) -> str:
        """Generate React component JSX"""

        component_templates = {
            "card": self._generate_card_jsx(component_name),
            "nav": self._generate_nav_jsx(component_name),
            "modal": self._generate_modal_jsx(component_name),
            "panel": self._generate_panel_jsx(component_name),
            "button": self._generate_button_jsx(component_name)
        }

        return component_templates.get(
            component.component_type,
            component_templates["card"]
        )

    def _generate_card_jsx(self, component_name: str) -> str:
        """Generate glass card JSX"""

        return f'''export default function {component_name}({{ children, title }}) {{
  return (
    <div className="{component_name}">
      {{title && <h3 className="text-xl font-semibold mb-4">{{title}}</h3>}}
      {{children}}
    </div>
  );
}}'''

    def _generate_nav_jsx(self, component_name: str) -> str:
        """Generate glass navigation JSX"""

        return f'''export default function {component_name}({{ items }}) {{
  return (
    <nav className="{component_name} fixed top-0 left-0 right-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <ul className="flex items-center space-x-8">
          {{items.map((item, i) => (
            <li key={{i}}>
              <a href={{item.href}} className="hover:text-primary-light transition-colors">
                {{item.label}}
              </a>
            </li>
          ))}}
        </ul>
      </div>
    </nav>
  );
}}'''

    def _generate_modal_jsx(self, component_name: str) -> str:
        """Generate glass modal JSX"""

        return f'''export default function {component_name}({{ isOpen, onClose, children }}) {{
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={{onClose}} />
      <div className="{component_name} relative max-w-2xl w-full max-h-[90vh] overflow-auto">
        <button
          onClick={{onClose}}
          className="absolute top-4 right-4 text-2xl hover:text-primary-light transition-colors"
        >
          ×
        </button>
        {{children}}
      </div>
    </div>
  );
}}'''

    def _generate_panel_jsx(self, component_name: str) -> str:
        """Generate glass panel JSX"""

        return f'''export default function {component_name}({{ children, className = '' }}) {{
  return (
    <div className="{component_name} {{className}}">
      {{children}}
    </div>
  );
}}'''

    def _generate_button_jsx(self, component_name: str) -> str:
        """Generate glass button JSX"""

        return f'''export default function {component_name}({{ children, onClick, variant = 'primary' }}) {{
  return (
    <button
      onClick={{onClick}}
      className="{component_name} px-6 py-3 font-medium cursor-pointer"
    >
      {{children}}
    </button>
  );
}}'''

    def _lighten_color(self, hex_color: str, amount: float) -> str:
        """Lighten a hex color by amount (0.0-1.0)"""

        # Remove #
        hex_color = hex_color.lstrip('#')

        # Convert to RGB
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0

        # Convert to HSL
        h, l, s = colorsys.rgb_to_hls(r, g, b)

        # Increase lightness
        l = min(1.0, l + amount)

        # Convert back to RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)

        # Convert to hex
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    def _rgba_from_hex(self, hex_color: str, alpha: float) -> str:
        """Convert hex color to rgba with alpha"""

        hex_color = hex_color.lstrip('#')

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        return f"rgba({r}, {g}, {b}, {alpha})"

    def save_design_system(self, design_system: GlassDesignSystem) -> Tuple[Path, Path]:
        """Save design system files"""

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Save CSS
        css_path = self.output_dir / "glass.css"
        with open(css_path, 'w') as f:
            f.write(design_system.css_code)

        self.logger.info(f"Saved design system CSS to {css_path}")

        # Save Tailwind config
        config_path = self.project_root / "tailwind.glass.config.js"
        with open(config_path, 'w') as f:
            f.write(design_system.tailwind_config)

        self.logger.info(f"Saved Tailwind config to {config_path}")

        return css_path, config_path

    def save_component(
        self,
        component_code: str,
        component_name: str
    ) -> Path:
        """Save glassmorphic component"""

        self.components_dir.mkdir(parents=True, exist_ok=True)

        file_path = self.components_dir / f"{component_name}.tsx"

        with open(file_path, 'w') as f:
            f.write(component_code)

        self.logger.info(f"Saved glass component to {file_path}")

        return file_path

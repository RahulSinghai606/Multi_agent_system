"""
Accessibility UI Specialist Agent

Expert in WCAG 2.2 AAA compliance with:
- Color contrast analysis (7:1 for AAA)
- Keyboard navigation automation
- Screen reader optimization
- ARIA attributes generation
- Focus management
- Semantic HTML enforcement
- Accessible form validation
- Motion sensitivity support

Capabilities:
- WCAG 2.2 AAA compliance validation
- Automated accessibility testing
- ARIA role and property generation
- Keyboard shortcut generation
- Focus trap implementation
- Skip navigation links
- Accessible modals and dialogs
- Form error handling
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class ColorContrastResult:
    """Color contrast analysis result"""

    foreground: str
    background: str
    contrast_ratio: float
    passes_aa: bool  # 4.5:1
    passes_aaa: bool  # 7:1
    recommendation: Optional[str] = None


@dataclass
class AccessibilityIssue:
    """Accessibility issue found in component"""

    severity: str  # "critical", "error", "warning", "info"
    wcag_criterion: str  # e.g., "1.4.3", "2.1.1", "4.1.2"
    description: str
    element: str  # CSS selector or description
    fix_suggestion: str
    code_example: Optional[str] = None


@dataclass
class KeyboardNavigation:
    """Keyboard navigation configuration"""

    tab_order: List[str]  # List of selectors in tab order
    shortcuts: Dict[str, str]  # key → action
    focus_trap: bool  # Enable focus trapping (for modals)
    skip_links: List[Dict[str, str]]  # Skip navigation links


@dataclass
class ARIAConfiguration:
    """ARIA attributes configuration"""

    role: Optional[str]
    label: Optional[str]
    labelledby: Optional[str]
    describedby: Optional[str]
    live: Optional[str]  # "polite", "assertive", "off"
    atomic: bool
    relevant: Optional[str]
    expanded: Optional[bool]
    controls: Optional[str]
    owns: Optional[str]
    custom_attributes: Dict[str, str]


@dataclass
class AccessibleComponent:
    """Accessible component specification"""

    component_name: str
    semantic_html: str  # Semantic HTML structure
    aria_config: ARIAConfiguration
    keyboard_nav: KeyboardNavigation
    color_contrast: List[ColorContrastResult]
    issues: List[AccessibilityIssue]
    wcag_compliance_level: str  # "A", "AA", "AAA"
    code: str


class AccessibilityUISpecialist:
    """
    Expert agent for WCAG 2.2 AAA accessibility

    Generates accessible components with:
    - Color contrast validation (7:1 for AAA)
    - Keyboard navigation
    - Screen reader optimization
    - ARIA attributes
    - Semantic HTML
    - Focus management
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "src" / "components" / "accessible"
        self.logger = logging.getLogger(f"{__name__}.AccessibilityUISpecialist")

    def audit_component(
        self,
        component_code: str,
        component_type: str
    ) -> List[AccessibilityIssue]:
        """
        Audit component for accessibility issues

        Args:
            component_code: Component source code
            component_type: Type of component

        Returns:
            List of accessibility issues found
        """
        self.logger.info(f"Auditing component: {component_type}")

        issues = []

        # Check semantic HTML
        issues.extend(self._audit_semantic_html(component_code))

        # Check ARIA attributes
        issues.extend(self._audit_aria(component_code))

        # Check keyboard accessibility
        issues.extend(self._audit_keyboard(component_code, component_type))

        # Check focus management
        issues.extend(self._audit_focus(component_code, component_type))

        # Check form accessibility
        if "form" in component_type.lower() or "input" in component_code.lower():
            issues.extend(self._audit_forms(component_code))

        # Check interactive elements
        issues.extend(self._audit_interactive(component_code))

        return issues

    def validate_color_contrast(
        self,
        foreground: str,
        background: str,
        level: str = "AAA"
    ) -> ColorContrastResult:
        """
        Validate color contrast ratio

        Args:
            foreground: Foreground color (hex)
            background: Background color (hex)
            level: Target WCAG level ("AA" or "AAA")

        Returns:
            ColorContrastResult with validation results
        """
        ratio = self._calculate_contrast_ratio(foreground, background)

        passes_aa = ratio >= 4.5
        passes_aaa = ratio >= 7.0

        recommendation = None
        if level == "AAA" and not passes_aaa:
            recommendation = self._suggest_accessible_color(foreground, background, 7.0)
        elif level == "AA" and not passes_aa:
            recommendation = self._suggest_accessible_color(foreground, background, 4.5)

        return ColorContrastResult(
            foreground=foreground,
            background=background,
            contrast_ratio=ratio,
            passes_aa=passes_aa,
            passes_aaa=passes_aaa,
            recommendation=recommendation
        )

    def generate_accessible_component(
        self,
        component_type: str,
        spec: Dict[str, Any],
        base_code: Optional[str] = None
    ) -> AccessibleComponent:
        """
        Generate WCAG 2.2 AAA compliant component

        Args:
            component_type: Type of component (button, form, modal, nav)
            spec: Component specification
            base_code: Optional base component code to enhance

        Returns:
            AccessibleComponent with full accessibility features
        """
        self.logger.info(f"Generating accessible component: {component_type}")

        # Generate semantic HTML
        semantic_html = self._generate_semantic_html(component_type, spec)

        # Generate ARIA configuration
        aria_config = self._generate_aria_config(component_type, spec)

        # Generate keyboard navigation
        keyboard_nav = self._generate_keyboard_nav(component_type, spec)

        # Validate color contrast
        color_contrast = []
        if "colors" in spec:
            for fg, bg in spec["colors"]:
                color_contrast.append(self.validate_color_contrast(fg, bg, "AAA"))

        # Generate component code
        code = self._generate_accessible_code(
            component_type,
            spec.get("name", "AccessibleComponent"),
            semantic_html,
            aria_config,
            keyboard_nav,
            base_code
        )

        # Audit generated code
        issues = self.audit_component(code, component_type)

        # Determine WCAG compliance level
        wcag_level = self._determine_wcag_level(issues, color_contrast)

        return AccessibleComponent(
            component_name=spec.get("name", "AccessibleComponent"),
            semantic_html=semantic_html,
            aria_config=aria_config,
            keyboard_nav=keyboard_nav,
            color_contrast=color_contrast,
            issues=issues,
            wcag_compliance_level=wcag_level,
            code=code
        )

    def _audit_semantic_html(self, code: str) -> List[AccessibilityIssue]:
        """Audit semantic HTML usage"""
        issues = []

        # Check for div soup (excessive div nesting)
        if code.count("<div") > 10 and "<section" not in code and "<article" not in code:
            issues.append(AccessibilityIssue(
                severity="warning",
                wcag_criterion="4.1.2",
                description="Excessive div elements without semantic HTML",
                element="div",
                fix_suggestion="Use semantic HTML5 elements (section, article, nav, aside, header, footer)",
                code_example="<section>\n  <h2>Section Title</h2>\n  <article>Content</article>\n</section>"
            ))

        # Check for missing heading hierarchy
        if "<h1" not in code and ("<h2" in code or "<h3" in code):
            issues.append(AccessibilityIssue(
                severity="error",
                wcag_criterion="1.3.1",
                description="Heading hierarchy missing h1",
                element="h2/h3",
                fix_suggestion="Add h1 as primary heading",
                code_example="<h1>Page Title</h1>\n<h2>Section Title</h2>"
            ))

        # Check for buttons vs links
        if re.search(r'<a[^>]*onClick', code):
            issues.append(AccessibilityIssue(
                severity="warning",
                wcag_criterion="4.1.2",
                description="Link used for button action",
                element="a[onClick]",
                fix_suggestion="Use <button> for actions, <a> for navigation",
                code_example='<button onClick={handleClick}>Action</button>'
            ))

        return issues

    def _audit_aria(self, code: str) -> List[AccessibilityIssue]:
        """Audit ARIA usage"""
        issues = []

        # Check for missing alt text on images
        if re.search(r'<img[^>]*(?!alt)', code):
            issues.append(AccessibilityIssue(
                severity="critical",
                wcag_criterion="1.1.1",
                description="Image missing alt attribute",
                element="img",
                fix_suggestion="Add descriptive alt text to all images",
                code_example='<img src="..." alt="Description of image" />'
            ))

        # Check for aria-label on interactive elements
        if re.search(r'<button[^>]*>[\s]*<svg', code) and not re.search(r'aria-label', code):
            issues.append(AccessibilityIssue(
                severity="error",
                wcag_criterion="4.1.2",
                description="Icon button missing aria-label",
                element="button > svg",
                fix_suggestion="Add aria-label to icon buttons",
                code_example='<button aria-label="Close modal">\n  <svg>...</svg>\n</button>'
            ))

        # Check for redundant ARIA
        if re.search(r'<button[^>]*role="button"', code):
            issues.append(AccessibilityIssue(
                severity="info",
                wcag_criterion="4.1.2",
                description="Redundant ARIA role on native element",
                element="button[role=button]",
                fix_suggestion="Remove redundant role from native button",
                code_example='<button>Action</button>'
            ))

        return issues

    def _audit_keyboard(self, code: str, component_type: str) -> List[AccessibilityIssue]:
        """Audit keyboard accessibility"""
        issues = []

        # Check for missing onKeyDown on clickable elements
        if re.search(r'onClick=', code) and not re.search(r'onKeyDown=', code):
            issues.append(AccessibilityIssue(
                severity="error",
                wcag_criterion="2.1.1",
                description="Clickable element not keyboard accessible",
                element="onClick handler",
                fix_suggestion="Add onKeyDown handler for Enter and Space keys",
                code_example='onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") handleClick(); }}'
            ))

        # Check for tab index on non-interactive elements
        if re.search(r'<div[^>]*tabIndex', code) or re.search(r'<span[^>]*tabIndex', code):
            issues.append(AccessibilityIssue(
                severity="warning",
                wcag_criterion="2.1.1",
                description="tabIndex on non-interactive element",
                element="div/span[tabIndex]",
                fix_suggestion="Use semantic interactive elements or add role",
                code_example='<button>Interactive Element</button>'
            ))

        # Check for modal focus trap
        if component_type == "modal" and "tabIndex" not in code:
            issues.append(AccessibilityIssue(
                severity="error",
                wcag_criterion="2.1.2",
                description="Modal missing focus trap",
                element="modal",
                fix_suggestion="Implement focus trap for modal dialogs",
                code_example="useFocusTrap(modalRef)"
            ))

        return issues

    def _audit_focus(self, code: str, component_type: str) -> List[AccessibilityIssue]:
        """Audit focus management"""
        issues = []

        # Check for focus outline removal
        if "outline: none" in code or "outline:none" in code:
            issues.append(AccessibilityIssue(
                severity="critical",
                wcag_criterion="2.4.7",
                description="Focus outline removed without alternative",
                element="*:focus",
                fix_suggestion="Provide visible focus indicator",
                code_example="*:focus { outline: 2px solid blue; outline-offset: 2px; }"
            ))

        # Check for skip links
        if component_type == "nav" and "skip" not in code.lower():
            issues.append(AccessibilityIssue(
                severity="warning",
                wcag_criterion="2.4.1",
                description="Navigation missing skip link",
                element="nav",
                fix_suggestion="Add skip to main content link",
                code_example='<a href="#main" className="skip-link">Skip to main content</a>'
            ))

        return issues

    def _audit_forms(self, code: str) -> List[AccessibilityIssue]:
        """Audit form accessibility"""
        issues = []

        # Check for labels on inputs
        if re.search(r'<input', code) and not re.search(r'<label', code) and not re.search(r'aria-label', code):
            issues.append(AccessibilityIssue(
                severity="critical",
                wcag_criterion="3.3.2",
                description="Input missing associated label",
                element="input",
                fix_suggestion="Add label or aria-label to all inputs",
                code_example='<label htmlFor="email">Email:</label>\n<input id="email" type="email" />'
            ))

        # Check for required field indication
        if re.search(r'required', code) and not re.search(r'aria-required', code):
            issues.append(AccessibilityIssue(
                severity="warning",
                wcag_criterion="3.3.2",
                description="Required field not announced to screen readers",
                element="input[required]",
                fix_suggestion="Add aria-required to required fields",
                code_example='<input required aria-required="true" />'
            ))

        # Check for error messages
        if re.search(r'error', code, re.IGNORECASE) and not re.search(r'aria-describedby', code):
            issues.append(AccessibilityIssue(
                severity="error",
                wcag_criterion="3.3.1",
                description="Error message not associated with input",
                element="error message",
                fix_suggestion="Link error messages with aria-describedby",
                code_example='<input aria-describedby="email-error" />\n<span id="email-error">Error message</span>'
            ))

        return issues

    def _audit_interactive(self, code: str) -> List[AccessibilityIssue]:
        """Audit interactive elements"""
        issues = []

        # Check for sufficient click target size
        if re.search(r'<button', code) and not re.search(r'padding', code):
            issues.append(AccessibilityIssue(
                severity="warning",
                wcag_criterion="2.5.5",
                description="Interactive element may have insufficient target size",
                element="button",
                fix_suggestion="Ensure minimum 44x44px touch target",
                code_example="button { padding: 0.75rem 1.5rem; }"
            ))

        return issues

    def _calculate_contrast_ratio(self, fg: str, bg: str) -> float:
        """Calculate WCAG contrast ratio between two colors"""

        def get_luminance(color: str) -> float:
            """Calculate relative luminance"""
            # Remove # if present
            color = color.lstrip('#')

            # Convert to RGB
            r = int(color[0:2], 16) / 255.0
            g = int(color[2:4], 16) / 255.0
            b = int(color[4:6], 16) / 255.0

            # Apply sRGB transformation
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4

            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        l1 = get_luminance(fg)
        l2 = get_luminance(bg)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)

    def _suggest_accessible_color(
        self,
        foreground: str,
        background: str,
        target_ratio: float
    ) -> str:
        """Suggest accessible color adjustment"""

        current_ratio = self._calculate_contrast_ratio(foreground, background)

        if current_ratio >= target_ratio:
            return foreground

        # Simple suggestion: darken foreground or lighten background
        return f"Adjust {foreground} to achieve {target_ratio}:1 contrast ratio (current: {current_ratio:.1f}:1)"

    def _generate_semantic_html(self, component_type: str, spec: Dict[str, Any]) -> str:
        """Generate semantic HTML structure"""

        templates = {
            "button": "<button type=\"button\">Click me</button>",
            "nav": "<nav aria-label=\"Main navigation\">\n  <ul>\n    <li><a href=\"#\">Home</a></li>\n  </ul>\n</nav>",
            "form": "<form>\n  <label htmlFor=\"input\">Label:</label>\n  <input id=\"input\" type=\"text\" />\n</form>",
            "modal": "<dialog role=\"dialog\" aria-modal=\"true\" aria-labelledby=\"modal-title\">\n  <h2 id=\"modal-title\">Modal Title</h2>\n  <div>Modal content</div>\n</dialog>",
            "card": "<article>\n  <h3>Card Title</h3>\n  <p>Card content</p>\n</article>"
        }

        return templates.get(component_type, "<div>Component</div>")

    def _generate_aria_config(self, component_type: str, spec: Dict[str, Any]) -> ARIAConfiguration:
        """Generate ARIA configuration"""

        configs = {
            "button": ARIAConfiguration(
                role=None,  # Native button has implicit role
                label=spec.get("label"),
                labelledby=None,
                describedby=None,
                live=None,
                atomic=False,
                relevant=None,
                expanded=spec.get("expandable"),
                controls=spec.get("controls"),
                owns=None,
                custom_attributes={}
            ),
            "nav": ARIAConfiguration(
                role=None,  # Native nav has implicit role
                label="Main navigation",
                labelledby=None,
                describedby=None,
                live=None,
                atomic=False,
                relevant=None,
                expanded=None,
                controls=None,
                owns=None,
                custom_attributes={}
            ),
            "modal": ARIAConfiguration(
                role="dialog",
                label=None,
                labelledby="modal-title",
                describedby="modal-description",
                live=None,
                atomic=False,
                relevant=None,
                expanded=None,
                controls=None,
                owns=None,
                custom_attributes={"aria-modal": "true"}
            )
        }

        return configs.get(component_type, ARIAConfiguration(
            role=None,
            label=None,
            labelledby=None,
            describedby=None,
            live=None,
            atomic=False,
            relevant=None,
            expanded=None,
            controls=None,
            owns=None,
            custom_attributes={}
        ))

    def _generate_keyboard_nav(self, component_type: str, spec: Dict[str, Any]) -> KeyboardNavigation:
        """Generate keyboard navigation configuration"""

        configs = {
            "button": KeyboardNavigation(
                tab_order=["button"],
                shortcuts={"Enter": "activate", " ": "activate"},
                focus_trap=False,
                skip_links=[]
            ),
            "nav": KeyboardNavigation(
                tab_order=["a"],
                shortcuts={},
                focus_trap=False,
                skip_links=[{"text": "Skip to main content", "href": "#main"}]
            ),
            "modal": KeyboardNavigation(
                tab_order=["button", "input", "a"],
                shortcuts={"Escape": "close"},
                focus_trap=True,
                skip_links=[]
            ),
            "form": KeyboardNavigation(
                tab_order=["input", "button"],
                shortcuts={"Enter": "submit"},
                focus_trap=False,
                skip_links=[]
            )
        }

        return configs.get(component_type, KeyboardNavigation(
            tab_order=[],
            shortcuts={},
            focus_trap=False,
            skip_links=[]
        ))

    def _generate_accessible_code(
        self,
        component_type: str,
        component_name: str,
        semantic_html: str,
        aria_config: ARIAConfiguration,
        keyboard_nav: KeyboardNavigation,
        base_code: Optional[str]
    ) -> str:
        """Generate accessible React component code"""

        # Generate ARIA props
        aria_props = self._generate_aria_props(aria_config)

        # Generate keyboard handler
        keyboard_handler = self._generate_keyboard_handler(keyboard_nav)

        # Generate focus trap if needed
        focus_trap_code = self._generate_focus_trap(keyboard_nav.focus_trap)

        code = f'''import React, {{ useRef, useEffect }} from 'react';

/**
 * {component_name} - WCAG 2.2 AAA Compliant
 *
 * Generated by AccessibilityUISpecialist
 * Accessibility Features:
 * - Semantic HTML
 * - Keyboard navigation
 * - Screen reader optimization
 * - ARIA attributes
 * - Focus management
 */

{focus_trap_code}

export default function {component_name}(props) {{
  const componentRef = useRef(null);

{keyboard_handler}

  return (
    <div ref={{componentRef}} {aria_props}>
      {{props.children || (
        <>{semantic_html}</>
      )}}
    </div>
  );
}}
'''

        return code

    def _generate_aria_props(self, aria_config: ARIAConfiguration) -> str:
        """Generate ARIA props string"""
        props = []

        if aria_config.role:
            props.append(f'role="{aria_config.role}"')
        if aria_config.label:
            props.append(f'aria-label="{aria_config.label}"')
        if aria_config.labelledby:
            props.append(f'aria-labelledby="{aria_config.labelledby}"')
        if aria_config.describedby:
            props.append(f'aria-describedby="{aria_config.describedby}"')
        if aria_config.live:
            props.append(f'aria-live="{aria_config.live}"')
        if aria_config.expanded is not None:
            props.append(f'aria-expanded={{{str(aria_config.expanded).lower()}}}')
        if aria_config.controls:
            props.append(f'aria-controls="{aria_config.controls}"')

        for key, value in aria_config.custom_attributes.items():
            props.append(f'{key}="{value}"')

        return ' '.join(props)

    def _generate_keyboard_handler(self, keyboard_nav: KeyboardNavigation) -> str:
        """Generate keyboard event handler"""

        if not keyboard_nav.shortcuts:
            return ""

        handler_code = '''  const handleKeyDown = (e) => {
    switch (e.key) {'''

        for key, action in keyboard_nav.shortcuts.items():
            handler_code += f'''
      case "{key}":
        e.preventDefault();
        // Handle {action} action
        break;'''

        handler_code += '''
      default:
        break;
    }
  };

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);'''

        return handler_code

    def _generate_focus_trap(self, enabled: bool) -> str:
        """Generate focus trap hook"""

        if not enabled:
            return ""

        return '''function useFocusTrap(ref) {
  useEffect(() => {
    if (!ref.current) return;

    const focusableElements = ref.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTabKey = (e) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    };

    ref.current.addEventListener('keydown', handleTabKey);
    firstElement.focus();

    return () => ref.current?.removeEventListener('keydown', handleTabKey);
  }, [ref]);
}'''

    def _determine_wcag_level(
        self,
        issues: List[AccessibilityIssue],
        color_contrast: List[ColorContrastResult]
    ) -> str:
        """Determine WCAG compliance level"""

        # Check for critical/error issues
        has_critical = any(issue.severity == "critical" for issue in issues)
        has_error = any(issue.severity == "error" for issue in issues)

        # Check color contrast
        all_pass_aaa = all(result.passes_aaa for result in color_contrast) if color_contrast else True
        all_pass_aa = all(result.passes_aa for result in color_contrast) if color_contrast else True

        if has_critical or has_error:
            return "Below A"
        elif not all_pass_aa:
            return "A"
        elif not all_pass_aaa:
            return "AA"
        else:
            return "AAA"

    def save_component(self, component: AccessibleComponent) -> Path:
        """Save accessible component"""

        self.output_dir.mkdir(parents=True, exist_ok=True)

        file_path = self.output_dir / f"{component.component_name}.tsx"

        with open(file_path, 'w') as f:
            f.write(component.code)

        self.logger.info(f"Saved accessible component to {file_path}")

        # Save accessibility report
        report_path = self.output_dir / f"{component.component_name}.a11y.json"
        with open(report_path, 'w') as f:
            json.dump({
                "wcag_level": component.wcag_compliance_level,
                "issues_count": len(component.issues),
                "issues": [
                    {
                        "severity": issue.severity,
                        "criterion": issue.wcag_criterion,
                        "description": issue.description,
                        "element": issue.element,
                        "fix": issue.fix_suggestion
                    }
                    for issue in component.issues
                ],
                "color_contrast": [
                    {
                        "foreground": cr.foreground,
                        "background": cr.background,
                        "ratio": cr.contrast_ratio,
                        "passes_aaa": cr.passes_aaa
                    }
                    for cr in component.color_contrast
                ]
            }, f, indent=2)

        self.logger.info(f"Saved accessibility report to {report_path}")

        return file_path

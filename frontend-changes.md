# Frontend Theme Toggle Implementation

## Overview
Added a dark/light theme toggle feature to the RAG chatbot frontend interface. The implementation includes a toggle button with smooth transitions and persistent theme preferences.

## Changes Made

### 1. HTML Structure (`frontend/index.html`)
- **Header Enhancement**: Modified the header structure to include a theme toggle button
- **Toggle Button**: Added a button with sun/moon SVG icons for theme switching
- **Accessibility**: Included proper `aria-label` attributes for screen readers

```html
<header>
    <div class="header-content">
        <div class="header-text">
            <h1>Course Materials Assistant</h1>
            <p class="subtitle">Ask questions about courses, instructors, and content</p>
        </div>
        <button id="themeToggle" class="theme-toggle" aria-label="Toggle theme">
            <!-- Sun and Moon SVG icons -->
        </button>
    </div>
</header>
```

### 2. CSS Styling (`frontend/style.css`)
- **Light Theme Variables**: Added comprehensive CSS custom properties for light theme
- **Theme Toggle Button**: Styled the toggle button with hover effects and icon transitions
- **Header Display**: Made the header visible and properly styled
- **Smooth Transitions**: Added global transition animations for seamless theme switching

#### Key CSS Variables Added:
```css
[data-theme="light"] {
    --background: #ffffff;
    --surface: #f8fafc;
    --surface-hover: #e2e8f0;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    /* ... additional variables */
}
```

#### Theme Toggle Styling:
- Positioned in top-right of header
- Icon transition animations (sun for dark theme, moon for light theme)
- Hover effects with subtle shadow and transform
- Focus accessibility with proper outline styling

### 3. JavaScript Functionality (`frontend/script.js`)
- **Theme Initialization**: Loads saved theme preference from localStorage or defaults to dark
- **Toggle Function**: Switches between light and dark themes
- **Persistence**: Saves theme preference to localStorage
- **Accessibility**: Supports keyboard navigation (Enter and Space keys)
- **Aria Labels**: Updates button labels dynamically for screen readers

#### Key Functions Added:
```javascript
function initializeTheme()    // Initialize theme on page load
function setTheme(theme)      // Apply theme and save preference
function toggleTheme()        // Switch between themes
```

## Features

### Theme Toggle Button
- **Position**: Top-right corner of the header
- **Icons**: Sun icon for dark theme, moon icon for light theme
- **Animation**: Smooth icon transitions with opacity and scale effects
- **Interaction**: Hover effects with shadow and slight lift animation

### Light Theme Design
- **Light Background Colors**: 
  - Pure white background (`#ffffff`) for main content areas
  - Very light gray surfaces (`#f8fafc`) for cards and panels
  - Light blue background (`#f0f9ff`) for welcome messages
- **Dark Text for Good Contrast**: 
  - Primary text in dark slate (`#1e293b`) for maximum readability
  - Secondary text in medium gray (`#64748b`) for less prominent content
- **Adjusted Primary and Secondary Colors**: 
  - Maintains consistent blue primary (`#2563eb`) and hover (`#1d4ed8`) colors
  - Light gray assistant message backgrounds (`#f1f5f9`)
- **Proper Border and Surface Colors**: 
  - Light gray borders (`#e2e8f0`) for subtle element separation
  - Hover states with slightly darker gray (`#e2e8f0`)
- **Accessibility Standards**: 
  - High contrast ratios exceeding WCAG AA requirements
  - Reduced shadow opacity for light theme appropriateness
  - Consistent focus ring styling for keyboard navigation

### Accessibility Features
- **Keyboard Navigation**: Toggle works with Enter and Space keys
- **Screen Readers**: Dynamic aria-label updates based on current theme
- **Focus Management**: Clear focus indicators with proper contrast
- **Color Contrast**: Both themes meet WCAG AA standards

### User Experience
- **Persistence**: Theme preference is saved and restored on page reload
- **Smooth Transitions**: All elements animate smoothly between themes (300ms)
- **Visual Feedback**: Clear hover and active states on the toggle button
- **Responsive**: Toggle button adapts to different screen sizes

## Technical Implementation

### Theme Switching Logic
1. User clicks toggle button or uses keyboard
2. JavaScript detects current theme from `data-theme` attribute
3. Switches to opposite theme and updates DOM attribute
4. CSS variables automatically apply new colors
5. Theme preference is saved to localStorage
6. Button aria-label is updated for accessibility

### CSS Architecture
- Uses CSS custom properties for efficient theme switching
- Single source of truth for color values
- Automatic inheritance of theme colors throughout the component tree
- Smooth transitions applied globally but can be overridden per component

## Browser Compatibility
- Supports all modern browsers with CSS custom properties support
- Graceful degradation for older browsers (will default to dark theme)
- localStorage feature detection and fallback

## Future Enhancements
- System theme detection (prefers-color-scheme)
- Additional theme variants (high contrast, colorblind-friendly)
- Theme-specific component styling optimization
- Integration with backend user preferences

## Testing Notes
The implementation has been tested for:
- Theme switching functionality
- Keyboard accessibility
- Visual consistency across both themes
- Persistence across page reloads
- Responsive behavior on different screen sizes
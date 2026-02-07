# Dark Mode Quick Reference

## 🎨 Color Palette

### Backgrounds
```
Main Background:      #0e1117  ███████  (Dark gray-black)
Secondary Background: #1a1d29  ███████  (Cards, containers)
Tertiary Background:  #262730  ███████  (Input fields)
```

### Text
```
Primary Text:    #fafafa  ███████  (Off-white)
Secondary Text:  #b0b3b8  ███████  (Gray)
```

### Accents
```
Blue (Primary):   #4a9eff  ███████  (Links, focus)
Purple:           #8b5cf6  ███████  (Gradients)
Green (Success):  #10b981  ███████  (Resolved, safe)
Red (Error):      #ef4444  ███████  (Critical, high risk)
Orange (Warning): #f59e0b  ███████  (Pending, medium risk)
```

### Borders
```
Border Color: #2d3139  ███████  (Subtle borders)
```

## 🎯 Component Colors

### Status Badges
| Status | Color | Hex |
|--------|-------|-----|
| Pending | 🟡 Orange | #f59e0b |
| In Progress | 🔵 Blue | #4a9eff |
| Responded | 🟣 Purple | #8b5cf6 |
| Resolved | 🟢 Green | #10b981 |

### Priority Levels
| Priority | Color | Hex |
|----------|-------|-----|
| CRITICAL | 🔴 Red | #ef4444 |
| HIGH | 🟠 Orange | #f59e0b |
| MEDIUM | 🔵 Blue | #4a9eff |
| LOW | ⚪ Gray | #6b7280 |

### Risk Scores
| Risk Level | Color | Hex |
|------------|-------|-----|
| Low (0-49) | 🟢 Green | #10b981 |
| Medium (50-74) | 🟡 Orange | #f59e0b |
| High (75-100) | 🔴 Red | #ef4444 |

## 📦 Component Styling

### Cards
```css
Background: #1a1d29
Border: 1px solid #2d3139
Border-Left: 4px solid #4a9eff
Border-Radius: 12px
Shadow: 0 4px 8px rgba(0,0,0,0.3)
```

### Buttons
```css
Normal:
  Background: #262730
  Color: #fafafa
  Border: 1px solid #2d3139
  
Primary:
  Background: linear-gradient(135deg, #4a9eff 0%, #8b5cf6 100%)
  Color: white
  Border: none
  
Hover:
  Transform: translateY(-2px)
  Shadow: 0 6px 12px rgba(0,0,0,0.4)
```

### Input Fields
```css
Background: #262730
Color: #fafafa
Border: 1px solid #2d3139
Border-Radius: 8px

Focus:
  Border-Color: #4a9eff
  Shadow: 0 0 0 1px #4a9eff
```

### Headers
```css
Background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Color: white
Border-Radius: 12px
Shadow: 0 8px 16px rgba(0,0,0,0.4)
Border: 1px solid rgba(255,255,255,0.1)
```

## 🎭 Role-Based Themes

### Admin Theme
```
Header Gradient: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)
Title: "🔧 HarmLens Admin Panel"
Accent: Purple (#a855f7)
```

### Moderator Theme
```
Header Gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Title: "🛡️ HarmLens"
Accent: Blue (#4a9eff)
```

## 📊 Visual Hierarchy

### Level 1: Headers
- Gradient backgrounds
- Large text (2.5rem)
- Text shadow
- High contrast

### Level 2: Cards
- Secondary background
- Border accents
- Medium shadow
- Clear separation

### Level 3: Content
- Tertiary background
- Subtle borders
- Light shadow
- Grouped information

### Level 4: Details
- Transparent backgrounds
- No borders
- Secondary text color
- Supporting information

## 🔍 Accessibility

### Contrast Ratios
```
Text on Primary BG:    #fafafa on #0e1117 = 15.8:1 ✅ (AAA)
Text on Secondary BG:  #fafafa on #1a1d29 = 13.2:1 ✅ (AAA)
Text on Tertiary BG:   #fafafa on #262730 = 11.5:1 ✅ (AAA)
Secondary Text:        #b0b3b8 on #0e1117 = 9.1:1  ✅ (AAA)
```

### Color Blind Safe
- ✅ Red-Green: Uses blue as primary accent
- ✅ Blue-Yellow: High contrast maintained
- ✅ Monochrome: Brightness differences clear

## 🎨 Gradients

### Primary Gradient (Moderator)
```css
linear-gradient(135deg, #667eea 0%, #764ba2 100%)
```
Blue → Purple

### Admin Gradient
```css
linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)
```
Purple → Light Purple

### Button Gradient
```css
linear-gradient(135deg, #4a9eff 0%, #8b5cf6 100%)
```
Blue → Purple

### Sidebar Gradient
```css
linear-gradient(180deg, #1a1d29 0%, #0e1117 100%)
```
Light Dark → Dark

## 💡 Usage Examples

### Info Box
```html
<div class="info-box">
  Background: rgba(74, 158, 255, 0.1)
  Border-Left: 4px solid #4a9eff
  Border: 1px solid rgba(74, 158, 255, 0.2)
</div>
```

### Success Box
```html
<div class="success-box">
  Background: rgba(16, 185, 129, 0.1)
  Border-Left: 4px solid #10b981
  Border: 1px solid rgba(16, 185, 129, 0.2)
</div>
```

### Warning Box
```html
<div class="warning-box">
  Background: rgba(245, 158, 11, 0.1)
  Border-Left: 4px solid #f59e0b
  Border: 1px solid rgba(245, 158, 11, 0.2)
</div>
```

### Error Box
```html
<div class="error-box">
  Background: rgba(239, 68, 68, 0.1)
  Border-Left: 4px solid #ef4444
  Border: 1px solid rgba(239, 68, 68, 0.2)
</div>
```

## 🔧 Customization

### Change Primary Accent
Edit `.streamlit/config.toml`:
```toml
primaryColor = "#4a9eff"  # Change to your color
```

### Change Background
```toml
backgroundColor = "#0e1117"  # Darker or lighter
```

### Change Card Background
```toml
secondaryBackgroundColor = "#1a1d29"  # Adjust contrast
```

## 📱 Responsive Breakpoints

```css
Mobile:  < 768px   (Single column)
Tablet:  768-1024px (Two columns)
Desktop: > 1024px   (Three+ columns)
```

## ⚡ Performance

- **CSS Only**: No JavaScript overhead
- **Hardware Accelerated**: Transform and opacity
- **Optimized Selectors**: Minimal specificity
- **Cached**: Browser caches styles

## 🎯 Best Practices

### DO ✅
- Use CSS variables for consistency
- Maintain high contrast ratios
- Test on multiple devices
- Keep animations subtle
- Use semantic colors

### DON'T ❌
- Use pure black (#000000)
- Overuse animations
- Ignore accessibility
- Mix too many colors
- Forget hover states

---

**Quick Reference** | **Version 1.0.0** | **February 7, 2026**

# User Story: Correlation Matrix Frontend UI Components

**Story ID:** CM-003  
**Epic:** Correlation Matrix Feature  
**Status:** Draft  
**Priority:** High  
**Estimated Effort:** 0.5 day  
**Depends On:** None (can be done in parallel with backend)

---

## Story

**As a** frontend developer  
**I want** to add UI components for correlation matrix chart type selection  
**So that** users can discover and configure correlation visualizations

---

## Acceptance Criteria

- [ ] "Correlation Matrix" button added to chart type selector
- [ ] Button has 🔢 icon and "Correlation Matrix" label
- [ ] Button styling matches existing chart type buttons
- [ ] Column checkbox selector wrapper created
- [ ] Multi-select checkbox list for numeric columns implemented
- [ ] Helper text displays column selection requirements (2-10)
- [ ] Sampling configuration section added (collapsed by default)
- [ ] Loading skeleton component created
- [ ] Sampling notice component created
- [ ] All components are responsive (mobile, tablet, desktop)
- [ ] Touch target sizes meet accessibility standards (44×44px minimum)

---

## Technical Implementation

### HTML Updates (`static/index.html`)

```html
<!-- Add to chart type selector -->
<div id="chart-type-selector" class="chart-type-selector">
    <!-- Existing buttons... -->
    <button class="chart-type-button" data-chart="correlation">
        <span class="icon">🔢</span>
        <span class="label">Correlation Matrix</span>
    </button>
</div>

<!-- NEW: Correlation column selector -->
<div id="correlation-columns-wrapper" class="correlation-columns-wrapper" style="display: none;">
    <label for="correlation-column-list">Select Numeric Columns (2-10):</label>
    <div class="column-checkbox-list" id="correlation-column-list">
        <!-- Dynamically populated checkboxes -->
    </div>
    <small class="helper-text">
        Select at least 2 columns. Maximum 10 recommended for readability.
    </small>
    <div id="column-selection-status" role="status" aria-live="polite"></div>
    
    <!-- Advanced sampling configuration (collapsed) -->
    <details class="sampling-config" style="margin-top: 10px;">
        <summary>Advanced: Sampling Configuration</summary>
        <div class="sampling-controls">
            <label for="max-rows-input">Max Rows (0 = no limit):</label>
            <input type="number" id="max-rows-input" value="10000" min="0" step="1000">
            <small class="help-text">
                Default: 10,000 rows (recommended for datasets >1M rows).<br>
                Set to 0 to process full dataset (slower for large data).
            </small>
        </div>
    </details>
</div>

<!-- NEW: Sampling notice -->
<div id="sampling-notice" class="sampling-notice" role="status" aria-live="polite" style="display: none;">
    <span class="icon">ℹ</span>
    <span class="text" id="sampling-notice-text"></span>
</div>

<!-- NEW: Screen reader announcer -->
<div id="screen-reader-announcer" role="status" aria-live="polite" class="sr-only"></div>
```

### CSS Styling (`static/styles.css`)

```css
/* ============================================
   CORRELATION MATRIX STYLES
   ============================================ */

/* Chart type button */
.chart-type-button[data-chart="correlation"] {
    padding: 12px 20px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 14px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    min-width: 160px;
}

.chart-type-button[data-chart="correlation"]:hover {
    border-color: #0066CC;
    background: #f0f7ff;
    transform: translateY(-2px);
    box-shadow: 0 2px 8px rgba(0, 102, 204, 0.15);
}

.chart-type-button[data-chart="correlation"]:focus {
    outline: 2px solid #0066CC;
    outline-offset: 2px;
}

.chart-type-button[data-chart="correlation"].active {
    border-color: #0066CC;
    background: #e3f2fd;
    font-weight: 600;
}

.chart-type-button .icon {
    font-size: 28px;
    line-height: 1;
}

.chart-type-button .label {
    font-size: 14px;
    text-align: center;
    line-height: 1.3;
}

/* Column selector wrapper */
.correlation-columns-wrapper {
    margin: 20px 0;
    padding: 16px;
    background: #fafafa;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}

.correlation-columns-wrapper label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    font-size: 14px;
    color: #333;
}

/* Column checkbox list */
.column-checkbox-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
    margin: 12px 0;
    padding: 12px;
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    max-height: 300px;
    overflow-y: auto;
}

.column-checkbox {
    display: flex;
    align-items: center;
    padding: 8px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
    min-height: 44px;
}

.column-checkbox:hover {
    background: #f5f5f5;
}

.column-checkbox input[type="checkbox"] {
    width: 20px;
    height: 20px;
    margin-right: 8px;
    cursor: pointer;
    accent-color: #0066CC;
}

.column-checkbox input[type="checkbox"]:focus {
    outline: 2px solid #0066CC;
    outline-offset: 2px;
}

.column-checkbox span {
    font-size: 14px;
    color: #333;
    user-select: none;
}

.column-checkbox input[type="checkbox"]:checked + span {
    font-weight: 500;
    color: #0066CC;
}

.helper-text {
    display: block;
    margin-top: 8px;
    font-size: 12px;
    color: #757575;
    font-style: italic;
}

/* Sampling configuration */
.sampling-config {
    margin-top: 12px;
    padding: 8px;
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
}

.sampling-config summary {
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    color: #0066CC;
    padding: 4px;
}

.sampling-config summary:hover {
    color: #004499;
}

.sampling-controls {
    margin-top: 12px;
    padding: 8px;
}

.sampling-controls label {
    display: block;
    margin-bottom: 4px;
    font-size: 13px;
}

.sampling-controls input[type="number"] {
    width: 150px;
    padding: 6px 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
}

.sampling-controls .help-text {
    display: block;
    margin-top: 8px;
    font-size: 12px;
    color: #666;
    line-height: 1.4;
}

/* Sampling notice */
.sampling-notice {
    margin-top: 12px;
    padding: 12px 16px;
    background: #e3f2fd;
    border-left: 4px solid #2196F3;
    border-radius: 4px;
    font-size: 13px;
    color: #0d47a1;
    display: flex;
    align-items: center;
    gap: 8px;
}

.sampling-notice .icon {
    font-size: 16px;
    flex-shrink: 0;
}

.sampling-notice .text {
    flex: 1;
    line-height: 1.4;
}

/* Loading skeleton */
.skeleton-loader {
    width: 100%;
    height: 400px;
    background: #f5f5f5;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 20px;
    gap: 8px;
    position: relative;
    overflow: hidden;
}

.skeleton-loader::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.3),
        transparent
    );
    animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
    to {
        left: 100%;
    }
}

.skeleton-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 4px;
    height: 300px;
}

.skeleton-cell {
    background: #e0e0e0;
    border-radius: 2px;
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}

.skeleton-cell:nth-child(odd) {
    animation-delay: 0.1s;
}

.loading-text {
    text-align: center;
    margin-top: 16px;
    font-size: 14px;
    color: #757575;
    font-weight: 500;
}

/* Screen reader only */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}

/* ============================================
   RESPONSIVE DESIGN
   ============================================ */

/* Mobile (< 768px) */
@media (max-width: 767px) {
    .chart-type-button[data-chart="correlation"] {
        min-width: 140px;
        padding: 10px 16px;
    }
    
    .column-checkbox-list {
        grid-template-columns: 1fr;
        max-height: 250px;
    }
    
    .sampling-controls input[type="number"] {
        width: 100%;
    }
}

/* Tablet (768-1023px) */
@media (min-width: 768px) and (max-width: 1023px) {
    .column-checkbox-list {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* High contrast mode */
@media (prefers-contrast: high) {
    .column-checkbox input[type="checkbox"] {
        border: 2px solid #000;
    }
    
    .chart-container {
        border: 2px solid #000;
    }
}
```

---

## Accessibility Requirements

### ARIA Labels

- Chart type button: `aria-label="Select Correlation Matrix chart type"`
- Column selector fieldset: `aria-labelledby` pointing to label
- Selection status: `role="status" aria-live="polite"`
- Sampling notice: `role="status" aria-live="polite"`
- Screen reader announcer: `role="status" aria-live="polite"`

### Keyboard Navigation

- Tab sequence: Visualizations tab → Chart type button → Checkboxes → Advanced toggle
- Space: Toggle checkbox or expand details
- Enter: Activate button
- Arrow keys: Navigate between checkboxes (future enhancement)

### Touch Targets

- Minimum 44×44px touch targets for all interactive elements
- Larger touch areas via padding beyond visual boundaries

---

## Testing Requirements

### Visual Testing

1. **Chart Type Button**
   - Verify icon displays correctly
   - Test hover state changes
   - Test focus indicator visibility
   - Test active state styling

2. **Column Selector**
   - Verify grid layout on desktop
   - Verify single column on mobile
   - Test scrolling with 20+ columns
   - Test checkbox state changes

3. **Responsive Design**
   - Test on mobile (375px width)
   - Test on tablet (768px width)
   - Test on desktop (1024px+ width)
   - Test landscape/portrait orientations

### Accessibility Testing

1. **Screen Reader** (NVDA/JAWS)
   - Button announced correctly
   - Checkboxes announced with state
   - Status updates announced
   - Navigation logical

2. **Keyboard Navigation**
   - All elements reachable via Tab
   - Focus indicators visible
   - Space/Enter work correctly

3. **Color Contrast**
   - All text meets 4.5:1 ratio
   - Test with color blindness simulators

---

## Definition of Done

- [ ] All HTML components added
- [ ] All CSS styles implemented
- [ ] Responsive breakpoints working
- [ ] Accessibility requirements met
- [ ] Visual testing complete
- [ ] Keyboard navigation verified
- [ ] Screen reader tested
- [ ] Code reviewed
- [ ] No linting errors

---

## Notes

- Components are styled consistently with existing visualization UI
- Smart defaults reduce user friction
- Advanced options hidden but accessible for power users
- Mobile-first responsive design approach

# 🎯 Quick Reference: User Experience Features

## Toast Notifications

### JavaScript API
```javascript
toast.success('Operation successful!');           // Green, 5 sec
toast.error('Something went wrong!');             // Red, 7 sec
toast.warning('Please check your input!');        // Orange, 6 sec
toast.info('Just so you know...');                // Blue, 5 sec

// Custom duration
toast.success('Saved!', 'Success', 3000);         // 3 seconds
```

### Python Flask
```python
flash('✅ Successfully saved!', 'success')
flash('❌ Operation failed!', 'error')
flash('⚠️ Please fix errors', 'warning')
flash('ℹ️ Data auto-saved', 'info')
```

---

## Loading Indicators

```javascript
// Full page overlay
LoadingOverlay.show('Processing...');
// ... do work ...
LoadingOverlay.hide();

// Button loading
const btn = document.getElementById('myBtn');
setButtonLoading(btn, true);   // Show spinner
// ... do work ...
setButtonLoading(btn, false);  // Hide spinner
```

---

## Confirmation Dialogs

```javascript
// Warning (yellow)
const ok = await confirmModal.confirm('Are you sure?');
if (ok) { /* proceed */ }

// Danger (red)
const ok = await confirmModal.danger(
    'This will delete the item permanently',
    'Confirm Deletion'
);
if (ok) { /* delete */ }

// Custom
const ok = await confirmModal.show({
    title: 'Custom Action',
    message: 'Detailed message here',
    type: 'warning',          // or 'danger'
    confirmText: 'Yes, Do It',
    cancelText: 'Cancel',
    icon: '🔔'
});
```

---

## Form Validation

```javascript
// Auto-enabled on all forms
// Manual usage:
const validator = new FormValidator(formElement);

// Validate entire form
if (validator.validateForm()) {
    // Submit
}

// Validate single field
validator.validateField(inputElement);
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl + S | Save/Submit form |
| Esc | Close modal |
| Shift + ? | Show shortcuts menu |
| Ctrl + K | Focus search |

### Add Custom Shortcuts
```javascript
keyboard.register(
    'n',                        // Key
    () => { /* action */ },     // Callback
    'Create new item',          // Description
    true                        // Requires Ctrl?
);
```

---

## Python Validation Helpers

```python
from utils.feedback import (
    validate_number,
    validate_email,
    validate_phone,
    validate_date,
    format_success_message,
    get_user_friendly_error
)

# Validate number
is_valid, result = validate_number(
    value,
    field_name='Quantity',
    min_val=1,
    max_val=1000,
    allow_decimal=False
)
if not is_valid:
    flash(result, 'warning')  # result is error message
    return redirect(...)
quantity = result  # result is converted number

# Validate email
is_valid, error = validate_email(email)
if not is_valid:
    flash(error, 'warning')

# Validate phone
is_valid, error = validate_phone(phone)
if not is_valid:
    flash(error, 'warning')

# Validate date
is_valid, date_obj = validate_date(
    date_str,
    field_name='Purchase Date',
    allow_future=False,
    allow_past=True
)

# Format success message
msg = format_success_message('created', 'Asset XYZ')
flash(msg, 'success')
# Output: ✅ Successfully created Asset XYZ!

# Get user-friendly error
try:
    # ... operation ...
except Exception as e:
    error = get_user_friendly_error(e, 'Asset Name')
    flash(error, 'error')
```

---

## HTML Helpers

### Auto-confirmation on delete
```html
<button data-confirm="Are you sure you want to delete this asset?">
    Delete Asset
</button>

<a href="/delete/123" data-confirm="This action cannot be undone">
    Delete
</a>
```

### Disable form loading state
```html
<form data-no-loading>
    <!-- This form won't show loading spinner on submit -->
</form>
```

### Disable auto-validation
```html
<form novalidate>
    <!-- This form won't auto-validate -->
</form>
```

---

## Common Patterns

### Save with feedback
```python
@app.route('/save', methods=['POST'])
def save():
    try:
        # Validate
        name = request.form.get('name', '').strip()
        if not name:
            flash('⚠️ Name is required', 'warning')
            return redirect(url_for('form'))
        
        is_valid, qty = validate_number(
            request.form.get('quantity'),
            'Quantity',
            min_val=1,
            allow_decimal=False
        )
        if not is_valid:
            flash(qty, 'warning')  # qty is error message
            return redirect(url_for('form'))
        
        # Save
        save_to_db(name, qty)
        
        # Success
        flash(f'✅ Successfully saved {name}! Quantity: {qty}', 'success')
        return redirect(url_for('list'))
        
    except Exception as e:
        error = get_user_friendly_error(e, 'Asset')
        flash(error, 'error')
        return redirect(url_for('form'))
```

### Async operation with loading
```javascript
async function performAction() {
    LoadingOverlay.show('Processing...');
    
    try {
        const response = await fetch('/api/action', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {'Content-Type': 'application/json'}
        });
        
        LoadingOverlay.hide();
        
        if (response.ok) {
            toast.success('Action completed successfully!');
            window.location.reload();
        } else {
            const error = await response.json();
            toast.error(error.message || 'Action failed');
        }
    } catch (error) {
        LoadingOverlay.hide();
        toast.error('Network error. Please try again.');
    }
}
```

### Form with validation
```html
<form id="myForm" method="POST">
    <div class="form-group">
        <label for="email">Email *</label>
        <input type="email" 
               id="email" 
               name="email" 
               class="form-control" 
               required>
    </div>
    
    <div class="form-group">
        <label for="quantity">Quantity *</label>
        <input type="number" 
               id="quantity" 
               name="quantity" 
               class="form-control" 
               min="1" 
               required>
    </div>
    
    <button type="submit" class="btn btn-primary">
        Save
    </button>
</form>

<script>
// Auto-validated by FormValidator class
// On submit, button shows loading state automatically
</script>
```

---

## Error Message Examples

### Good Error Messages ✅
```
⚠️ Quantity must be a whole number (e.g., 1, 5, 10).
⚠️ Email must be a valid email format (e.g., user@example.com).
⚠️ Price must be a positive number (e.g., 100.00 or 1500.50).
❌ Asset "Laptop-001" already exists. Please use a different identifier.
❌ Cannot delete this item because it's referenced by other records.
```

### Bad Error Messages ❌
```
ValueError: invalid literal
Duplicate entry
Foreign key constraint failed
Required field
Invalid input
```

---

## CSS Classes

### Form validation states
```html
<input class="form-control is-valid">   <!-- Green border + ✓ -->
<input class="form-control is-invalid"> <!-- Red border + ✕ -->

<div class="form-feedback valid">
    ✓ Looks good!
</div>
<div class="form-feedback invalid">
    ✕ Error message here
</div>
```

### Toast container
```html
<!-- Auto-created by notifications.js -->
<div class="toast-container">
    <div class="toast success">...</div>
    <div class="toast error">...</div>
</div>
```

---

## Demo & Documentation

- **Demo Page:** http://207.246.126.171:5000/ux-demo
- **Full Documentation:** `/USER_EXPERIENCE_FEATURES.md`
- **Implementation Details:** `/UX_IMPLEMENTATION_SUMMARY.md`
- **Code Files:**
  - CSS: `/src/static/css/notifications.css`
  - JS: `/src/static/js/notifications.js`
  - Python: `/src/utils/feedback.py`

---

## Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers
- ✅ Tablets

---

## Troubleshooting

**Toast not showing?**
1. Clear browser cache (Ctrl+Shift+R)
2. Check console for errors
3. Verify notifications.js is loaded

**Keyboard shortcuts not working?**
1. Click outside input fields
2. Press Shift+? to verify shortcuts
3. Check if JavaScript is enabled

**Form validation not triggering?**
1. Remove `novalidate` from form
2. Add proper `type` attributes to inputs
3. Check console for errors

---

## Pro Tips

1. **Use emojis** in messages for visual clarity
2. **Be specific** in error messages with examples
3. **Show progress** for operations > 1 second
4. **Confirm destructive** actions (delete, etc.)
5. **Provide defaults** to reduce user typing
6. **Test on mobile** - all features are responsive
7. **Use keyboard shortcuts** for faster workflow

---

**Quick Access:**
- Press `?` badge in bottom-right for shortcuts
- Press `Shift + ?` for full shortcuts menu
- Visit `/ux-demo` to test all features

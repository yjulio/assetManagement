# Asset Entry Form PDF

The system looks for the **NEW ASSET ENTRY FORM** PDF in this order:

1. **Project root:** `static/asset_entry_form.pdf` (recommended)
2. **This folder:** `src/static/forms/asset_entry_form.pdf`

Copy your form PDF to one of those locations and name it **`asset_entry_form.pdf`**.

**Routes:**
- **Filled form:** View an asset → "Download Asset Entry Form (PDF)" (or PDF button on Assets list). URL: `/view-asset/<name>/export-entry-form-pdf`
- **Blank template:** `/asset-entry-form-template` — view or download the blank form.

To map different PDF field names, edit `src/utils/pdf_form_fill.py` (see `FIELD_MAPPING`). Run `python3 -m utils.pdf_form_fill` from `src/` to list the template's field names.

"""
Fill the official Asset Entry Form PDF with asset data and return PDF bytes.
Template locations checked in order:
  1. static/asset_entry_form.pdf (project root)
  2. src/static/forms/asset_entry_form.pdf
"""
import os


# Map our asset keys to possible PDF form field names (try in order).
# Update FIELD_MAPPING if your PDF uses different field names (run list_pdf_fields() to see).
FIELD_MAPPING = [
    ("name", ["Asset Name", "asset_name", "Name", "AssetName", "ASSET NAME"]),
    ("quantity", ["Quantity", "quantity", "Qty", "QTY", "QUANTITY"]),
    ("price", ["Price", "price", "Purchase Price", "Cost", "PRICE", "Amount"]),
    ("description", ["Description", "description", "DESCRIPTION", "Remarks"]),
    ("category", ["Category", "category", "CATEGORY", "Type"]),
    ("supplier", ["Supplier", "supplier", "SUPPLIER", "Vendor"]),
    ("department", ["Department", "department", "DEPARTMENT", "Cost Center"]),
    ("location", ["Location", "location", "LOCATION", "Place"]),
    ("model", ["Model", "model", "MODEL"]),
    ("brand", ["Brand", "brand", "BRAND", "Make"]),
    ("serial_number", ["Serial Number", "serial_number", "Serial No", "SERIAL", "Serial Number"]),
    ("purchase_date", ["Purchase Date", "purchase_date", "Date Acquired", "PURCHASE DATE", "Date"]),
    ("responsible_officer", ["Responsible Officer", "responsible_officer", "Officer", "RESPONSIBLE OFFICER", "Custodian"]),
    ("lpo_number", ["LPO Number", "lpo_number", "LPO", "LPO No", "Order Number"]),
    ("asset_tag", ["Asset Tag", "asset_tag", "Tag", "ASSET TAG", "Tag Number"]),
    ("asset_condition", ["Condition", "asset_condition", "ASSET CONDITION", "Status"]),
    ("depreciation_method", ["Depreciation Method", "depreciation_method", "Depreciation"]),
    ("useful_life_years", ["Useful Life (Years)", "useful_life_years", "Useful Life", "Life (Years)"]),
    ("salvage_value", ["Salvage Value", "salvage_value", "Salvage", "Residual Value"]),
]


def _asset_to_flat_dict(asset_name, asset):
    """Build a flat dict of our field names -> string values."""
    d = {"name": asset_name}
    for key in [
        "quantity", "price", "description", "category", "supplier", "department", "location",
        "model", "brand", "serial_number", "purchase_date", "responsible_officer", "lpo_number",
        "asset_tag", "asset_condition", "depreciation_method", "useful_life_years", "salvage_value"
    ]:
        val = asset.get(key)
        if val is None:
            val = ""
        d[key] = str(val).strip() if val else ""
    return d


def _build_pdf_field_values(asset_name, asset):
    """Build dict of our_key -> value (used to fill by matching to actual PDF field names)."""
    return _asset_to_flat_dict(asset_name, asset)


def _match_pdf_fields(actual_pdf_field_names, flat_asset):
    """Build dict of actual PDF field name -> value for each field that we can match."""
    result = {}
    for our_key, possible_pdf_names in FIELD_MAPPING:
        value = flat_asset.get(our_key, "")
        if possible_pdf_names and (value or our_key == "name"):
            for pdf_name in possible_pdf_names:
                if pdf_name in actual_pdf_field_names:
                    result[pdf_name] = value or flat_asset.get(our_key, "")
    # Also try case-insensitive match for any actual field not yet matched
    for actual_name in actual_pdf_field_names:
        if actual_name in result:
            continue
        actual_lower = actual_name.strip().lower()
        for our_key, possible_pdf_names in FIELD_MAPPING:
            for pdf_name in possible_pdf_names:
                if pdf_name.strip().lower() == actual_lower:
                    result[actual_name] = str(flat_asset.get(our_key, "") or "")
                    break
    return result


def get_template_path(root_path):
    """
    Return path to asset entry form PDF. Checks (in order):
      1. static/asset_entry_form.pdf (project root, one level above root_path if root_path is src/)
      2. root_path/static/forms/asset_entry_form.pdf
    """
    # Project root: parent of src/ when app runs from src
    project_root = os.path.abspath(os.path.join(root_path, ".."))
    candidates = [
        os.path.join(project_root, "static", "asset_entry_form.pdf"),
        os.path.join(root_path, "static", "forms", "asset_entry_form.pdf"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return candidates[-1]  # so error message points to last tried location


def list_pdf_fields(template_path):
    """List all form field names in the PDF (for debugging / building FIELD_MAPPING)."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(template_path)
        fields = reader.get_fields()
        if not fields:
            return []
        names = []
        for name in fields:
            names.append(name)
        return sorted(names)
    except Exception as e:
        return ["Error: " + str(e)]


def fill_asset_entry_form_pdf(asset_name, asset, template_path):
    """
    Fill the PDF form with asset data. Returns (pdf_bytes, None) or (None, error_message).
    """
    if not os.path.isfile(template_path):
        return None, "Template PDF not found. Place asset_entry_form.pdf in project static/ or src/static/forms/"
    try:
        from PyPDF2 import PdfReader, PdfWriter
        reader = PdfReader(template_path)
        writer = PdfWriter()
        writer.set_need_appearances_writer(True)  # so filled values are visible
        # Clone pages
        for page in reader.pages:
            writer.add_page(page)
        flat_asset = _asset_to_flat_dict(asset_name, asset)
        actual_fields = reader.get_fields()
        if actual_fields:
            actual_names = list(actual_fields.keys())
            final_values = _match_pdf_fields(actual_names, flat_asset)
            for page in writer.pages:
                writer.update_page_form_field_values(page, final_values)
        output = __import__("io").BytesIO()
        writer.write(output)
        output.seek(0)
        return output.read(), None
    except Exception as e:
        return None, str(e)


if __name__ == "__main__":
    """Run: python -m utils.pdf_form_fill from src/ to list form field names in the template PDF."""
    import sys
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template = get_template_path(src_dir)
    if not os.path.isfile(template):
        print("Template not found:", template)
        print("Place asset_entry_form.pdf in project static/ or src/static/forms/")
        sys.exit(1)
    print("PDF form field names in template:", template)
    for name in list_pdf_fields(template):
        print(" ", name)

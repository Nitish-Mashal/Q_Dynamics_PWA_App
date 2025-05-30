import frappe
import os

file_urls = {
    "manifest.json": "/files/manifest.json",
    "logo-512.png": "/files/logo-512.png",
    "logo-192.png": "/files/logo-192.png",
    "logo.svg": "/files/logo.svg",
}

manifest_link = '<link rel="manifest" href="/files/manifest.json">'


def upload_file(file_name, file_url):
    full_path = frappe.get_app_path("qdynamics_pwa_app", "public", "files", file_name)

    if not os.path.exists(full_path):
        frappe.throw(f"File not found: {full_path}")

    # Delete existing file if any
    existing = frappe.db.get_all("File", filters={"file_url": file_url})
    for file in existing:
        frappe.delete_doc("File", file.name, force=True)

    # Upload file
    with open(full_path, "rb") as f:
        frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "is_private": 0,
            "content": f.read(),
        }).insert(ignore_permissions=True)


def toggle_pwa_settings(apply=True):
    ws = frappe.get_single("Website Settings")
    head_html = ws.head_html or ""

    if apply:
        # On install
        for file_name, file_url in file_urls.items():
            upload_file(file_name, file_url)

        if manifest_link not in head_html:
            ws.head_html = f"{head_html}\n{manifest_link}".strip()

    else:
        # On uninstall
        for file_url in file_urls.values():
            existing = frappe.db.get_all("File", filters={"file_url": file_url})
            for file in existing:
                frappe.delete_doc("File", file.name, force=True)

        if manifest_link in head_html:
            ws.head_html = head_html.replace(manifest_link, "").strip()

    ws.save()
    frappe.db.commit()


# Install hook
def toggle_pwa_settings_install():
    toggle_pwa_settings(apply=True)

# Uninstall hook
def toggle_pwa_settings_uninstall():
    toggle_pwa_settings(apply=False)

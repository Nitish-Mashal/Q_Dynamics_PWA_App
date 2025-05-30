import frappe
import os

def handle_pwa_assets():
    """Handles install/uninstall for PWA assets based on context."""
    is_uninstall = frappe.flags.in_uninstall

    filenames = [
        "manifest.json",
        "logo-512.png",
        "logo-192.png",
        "logo.svg"
    ]
    manifest_link = '<link rel="manifest" href="/files/manifest.json">'

    if is_uninstall:
        # 🔻 Uninstall mode
        for fname in filenames:
            file_docname = frappe.db.exists("File", {"file_name": fname})
            if file_docname:
                frappe.delete_doc("File", file_docname, ignore_permissions=True)

        # Remove <link rel="manifest"> from Website Settings
        settings = frappe.get_single("Website Settings")
        head_html = settings.head_html or ""
        if manifest_link in head_html:
            settings.head_html = head_html.replace(manifest_link, "").strip()
            settings.save()
    else:
        # 🔺 Install mode
        public_path = frappe.get_app_path("qdynamics_pwa_app", "public")

        for fname in filenames:
            full_path = os.path.join(public_path, fname)
            if os.path.exists(full_path):
                with open(full_path, "rb") as f:
                    content = f.read()

                if not frappe.db.exists("File", {"file_name": fname}):
                    file_doc = frappe.get_doc({
                        "doctype": "File",
                        "file_name": fname,
                        "is_private": 0,
                        "content": content
                    })
                    file_doc.insert(ignore_permissions=True)

        # Add <link rel="manifest"> to Website Settings
        settings = frappe.get_single("Website Settings")
        head_html = settings.head_html or ""
        if manifest_link not in head_html:
            settings.head_html = (head_html + "\n" + manifest_link).strip()
            settings.save()

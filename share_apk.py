#!/usr/bin/env python3
"""Generate QR code and shareable link for APK download"""
import qrcode
import socket

def get_local_ip():
    """Get the local IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# Get local IP
local_ip = get_local_ip()
apk_url = f"http://{local_ip}:8080/bmk.apk"

print(f"\n{'='*60}")
print(f"BMK APK Download Link")
print(f"{'='*60}\n")
print(f"Local Network URL: {apk_url}")
print(f"\nPublic URL: https://bmk-public.sushantkhatri.com.np/download_app")
print(f"\n{'='*60}\n")

# Generate QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(apk_url)
qr.make(fit=True)

# Print QR in terminal
qr.print_ascii(invert=True)

print(f"\n{'='*60}")
print("Scan the QR code above with your phone to download the APK")
print(f"{'='*60}\n")

# Save QR as image
import os
img = qr.make_image(fill_color="black", back_color="white")
qr_path = os.path.join(os.path.dirname(__file__), "files", "bmk_download_qr.png")
img.save(qr_path)
print(f"✓ QR code saved to: {qr_path}\n")

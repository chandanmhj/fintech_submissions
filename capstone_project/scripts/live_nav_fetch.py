"""Optional mfapi.in live NAV scaffold."""
import requests
def fetch_latest_nav(amfi_code):
 r=requests.get(f"https://api.mfapi.in/mf/{amfi_code}/latest",timeout=30); r.raise_for_status(); return r.json()

import sys
import os
sys.path.append(os.path.dirname(__file__))
from scan_patterns import parse_pe, pattern_to_regex

def search_sub():
    exe_path = "/Users/plusone/Documents/My Games/FFXIV/game/ffxiv_dx11.exe"
    data, sections = parse_pe(exe_path)
    sec = sections[".text"]
    sec_data = data[sec["rptr"]:sec["rptr"] + sec["rsize"]]
    
    # 48 8B 4E 18 48 8B 01
    pat = "48 8B 4E 18 48 8B 01"
    rx = pattern_to_regex(pat)
    matches = list(rx.finditer(sec_data))
    print(f"Matches for {pat}: {len(matches)}")
    for m in matches:
        va = sec["vaddr"] + m.start() + sec["image_base"]
        pre_bytes = sec_data[max(0, m.start()-10):m.start()]
        pre_hex = " ".join(f"{b:02X}" for b in pre_bytes)
        print(f"  VA=0x{va:X}, Pre: {pre_hex}")

if __name__ == "__main__":
    search_sub()

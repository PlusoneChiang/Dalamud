import sys
import os
import re
sys.path.append(os.path.dirname(__file__))
from scan_patterns import parse_pe, pattern_to_regex

def find_keyboard_state():
    exe_path = "/Users/plusone/Documents/My Games/FFXIV/game/ffxiv_dx11.exe"
    data, sections = parse_pe(exe_path)
    sec = sections[".text"]
    sec_data = data[sec["rptr"]:sec["rptr"] + sec["rsize"]]

    # KeyboardState instruction: lea rcx, ds:[rax*4 + ...] -> 48 8D 0C 85 or similar
    rx_kb = pattern_to_regex("48 8D 0C 85")
    matches = list(rx_kb.finditer(sec_data))
    print(f"Matches for 48 8D 0C 85: {len(matches)}")
    for m in matches:
        va = sec["vaddr"] + m.start() + sec["image_base"]
        b = sec_data[m.start():m.start()+16]
        hex_b = " ".join(f"{x:02X}" for x in b)
        print(f"  VA=0x{va:X}: {hex_b}")

if __name__ == "__main__":
    find_keyboard_state()

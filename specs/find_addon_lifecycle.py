import sys
import os
import re
sys.path.append(os.path.dirname(__file__))
from scan_patterns import parse_pe, pattern_to_regex

def check_addon_lifecycle():
    exe_path = "/Users/plusone/Documents/My Games/FFXIV/game/ffxiv_dx11.exe"
    data, sections = parse_pe(exe_path)
    sec = sections[".text"]
    sec_data = data[sec["rptr"]:sec["rptr"] + sec["rsize"]]

    # Let's search for sub-bytes of AddonDraw, AddonUpdate, AddonOnRequestedUpdate
    # AddonDraw: FF 90 ?? ?? ?? ?? 83 EB 01 79
    # AddonUpdate: 40 88 AF ?? ?? ?? ?? 45 33 D2
    # AddonOnRequestedUpdate: FF 90 A0 01 00 00

    print("Checking AddonDraw sub-pattern...")
    m1 = list(pattern_to_regex("83 EB 01 79 C4 48 81 EF").finditer(sec_data))
    print(f"AddonDraw sub-pattern matches: {len(m1)}")
    for m in m1:
        va = sec["vaddr"] + m.start() + sec["image_base"]
        print(f"  VA=0x{va:X}")

    print("Checking AddonUpdate sub-pattern...")
    m2 = list(pattern_to_regex("45 33 D2 48 8B 0D").finditer(sec_data))
    print(f"AddonUpdate sub-pattern matches: {len(m2)}")
    for m in m2:
        va = sec["vaddr"] + m.start() + sec["image_base"]
        print(f"  VA=0x{va:X}")

    print("Checking AddonOnRequestedUpdate sub-pattern...")
    m3 = list(pattern_to_regex("FF 90 A0 01 00 00").finditer(sec_data))
    print(f"AddonOnRequestedUpdate matches: {len(m3)}")
    for m in m3:
        va = sec["vaddr"] + m.start() + sec["image_base"]
        print(f"  VA=0x{va:X}")

if __name__ == "__main__":
    check_addon_lifecycle()

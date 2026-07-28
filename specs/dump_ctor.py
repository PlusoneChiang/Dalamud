import sys
import struct
import re
import os
sys.path.append(os.path.dirname(__file__))
from scan_patterns import parse_pe, pattern_to_regex

def dump_around_vtable():
    exe_path = "/Users/plusone/Documents/My Games/FFXIV/game/ffxiv_dx11.exe"
    data, sections = parse_pe(exe_path)
    
    # RaptureAtkModule VTable pattern
    pat = "48 8D 05 ?? ?? ?? ?? 48 89 8F ?? ?? ?? ?? 48 89 07"
    sec = sections[".text"]
    sec_data = data[sec["rptr"]:sec["rptr"] + sec["rsize"]]
    
    rx = pattern_to_regex(pat)
    matches = list(rx.finditer(sec_data))
    
    if not matches:
        print("No match found")
        return
        
    m = matches[0]
    file_offset = sec["rptr"] + m.start()
    va = sec["vaddr"] + m.start() + sec["image_base"]
    
    print(f"RaptureAtkModule ctor pattern match at VA=0x{va:X}, FileOffset=0x{file_offset:X}")
    
    # Print 500 bytes starting slightly before
    start = max(0, file_offset - 0x50)
    end = min(len(data), file_offset + 0x300)
    
    chunk = data[start:end]
    print("\nHex dump around RaptureAtkModule ctor:")
    for i in range(0, len(chunk), 16):
        cur_va = sec["vaddr"] + (start + i - sec["rptr"]) + sec["image_base"]
        hex_str = " ".join(f"{b:02X}" for b in chunk[i:i+16])
        print(f"0x{cur_va:X}: {hex_str}")

if __name__ == "__main__":
    dump_around_vtable()

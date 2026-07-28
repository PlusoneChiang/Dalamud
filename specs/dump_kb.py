import sys
import os
sys.path.append(os.path.dirname(__file__))
from scan_patterns import parse_pe

def check_kb_around():
    exe_path = "/Users/plusone/Documents/My Games/FFXIV/game/ffxiv_dx11.exe"
    data, sections = parse_pe(exe_path)
    sec = sections[".text"]
    sec_data = data[sec["rptr"]:sec["rptr"] + sec["rsize"]]
    
    # 0x1405B6DE7 offset
    rva = 0x1405B6DE7 - sec["image_base"]
    file_off = sec["rptr"] + (rva - sec["vaddr"])
    
    chunk = sec_data[file_off-30 : file_off+50]
    print(f"Hex dump around KeyboardState (VA=0x1405B6DE7):")
    for i in range(0, len(chunk), 16):
        cur_va = sec["vaddr"] + (file_off - 30 + i - sec["rptr"]) + sec["image_base"]
        hex_str = " ".join(f"{b:02X}" for b in chunk[i:i+16])
        print(f"0x{cur_va:X}: {hex_str}")

if __name__ == "__main__":
    check_kb_around()

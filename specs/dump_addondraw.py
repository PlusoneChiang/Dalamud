import sys
import os
sys.path.append(os.path.dirname(__file__))
from scan_patterns import parse_pe

def dump_addon_draw():
    exe_path = "/Users/plusone/Documents/My Games/FFXIV/game/ffxiv_dx11.exe"
    data, sections = parse_pe(exe_path)
    sec = sections[".text"]
    sec_data = data[sec["rptr"]:sec["rptr"] + sec["rsize"]]
    
    rva = 0x14064AAB7 - sec["image_base"]
    file_off = sec["rptr"] + (rva - sec["vaddr"])
    
    chunk = sec_data[file_off-30 : file_off+70]
    print(f"Hex dump around AddonDraw (VA=0x14064AAB7):")
    for i in range(0, len(chunk), 16):
        cur_va = sec["vaddr"] + (file_off - 30 + i - sec["rptr"]) + sec["image_base"]
        hex_str = " ".join(f"{b:02X}" for b in chunk[i:i+16])
        print(f"0x{cur_va:X}: {hex_str}")

if __name__ == "__main__":
    dump_addon_draw()

import sys
import struct
import os
sys.path.append(os.path.dirname(__file__))
from scan_patterns import parse_pe, pattern_to_regex

def find_atkmodule_offsets():
    exe_path = "/Users/plusone/Documents/My Games/FFXIV/game/ffxiv_dx11.exe"
    data, sections = parse_pe(exe_path)
    sec = sections[".text"]
    sec_data = data[sec["rptr"]:sec["rptr"] + sec["rsize"]]
    
    # AtkModule VTable pattern: AtkModule ctor often has string references or vtable initialization
    # Let's search for 0x72D8 or 0x72E8 or 0x72B8 (TextService)
    # E.g. lea rcx, [rax + 0x72D8] -> 48 8D 8B D8 72 00 00
    
    print("Searching for AtkTextInput offset in AtkModule...")
    rx_72d8 = pattern_to_regex("48 8D ?? D8 72 00 00") # 0x72D8
    rx_72e8 = pattern_to_regex("48 8D ?? E8 72 00 00") # 0x72E8
    
    matches_d8 = list(rx_72d8.finditer(sec_data))
    matches_e8 = list(rx_72e8.finditer(sec_data))
    
    print(f"Matches for 0x72D8: {len(matches_d8)}")
    for m in matches_d8[:5]:
        va = sec["vaddr"] + m.start() + sec["image_base"]
        bytes_hex = " ".join(f"{b:02X}" for b in sec_data[m.start():m.start()+12])
        print(f"  VA=0x{va:X}: {bytes_hex}")
        
    print(f"Matches for 0x72E8: {len(matches_e8)}")
    for m in matches_e8[:5]:
        va = sec["vaddr"] + m.start() + sec["image_base"]
        bytes_hex = " ".join(f"{b:02X}" for b in sec_data[m.start():m.start()+12])
        print(f"  VA=0x{va:X}: {bytes_hex}")

if __name__ == "__main__":
    find_atkmodule_offsets()

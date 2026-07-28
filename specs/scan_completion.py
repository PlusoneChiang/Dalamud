import sys
import os
sys.path.append(os.path.dirname(__file__))
from scan_patterns import parse_pe, pattern_to_regex

def check_open_completion():
    exe_path = "/Users/plusone/Documents/My Games/FFXIV/game/ffxiv_dx11.exe"
    data, sections = parse_pe(exe_path)
    sec = sections[".text"]
    sec_data = data[sec["rptr"]:sec["rptr"] + sec["rsize"]]
    
    # TC API12 pattern
    pat_tc = "40 57 48 81 EC ?? ?? ?? ?? 48 33 C4 48 89 84 24 ?? ?? ?? ?? 66 83 B9 ?? ?? ?? ??"
    # Standard API13 pattern
    pat_std = "E8 ?? ?? ?? ?? E9 ?? ?? ?? ?? 48 8B 4E 18 48 8B 01"
    
    m_tc = list(pattern_to_regex(pat_tc).finditer(sec_data))
    m_std = list(pattern_to_regex(pat_std).finditer(sec_data))
    
    print(f"TC OpenCompletion pattern matches: {len(m_tc)}")
    for m in m_tc[:5]:
        va = sec["vaddr"] + m.start() + sec["image_base"]
        print(f"  VA=0x{va:X}")
        
    print(f"Std OpenCompletion pattern matches: {len(m_std)}")
    for m in m_std[:5]:
        va = sec["vaddr"] + m.start() + sec["image_base"]
        print(f"  VA=0x{va:X}")

if __name__ == "__main__":
    check_open_completion()

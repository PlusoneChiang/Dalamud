import sys
import struct
import re

def parse_pe(path):
    with open(path, "rb") as f:
        data = f.read()

    # MZ header check
    if data[:2] != b"MZ":
        raise ValueError("Not a valid PE file")

    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if data[e_lfanew:e_lfanew+4] != b"PE\x00\x00":
        raise ValueError("Invalid PE signature")

    num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    opt_header_size = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    sect_offset = e_lfanew + 24 + opt_header_size

    image_base = struct.unpack_from("<Q", data, e_lfanew + 48)[0] # 64-bit

    sections = {}
    for i in range(num_sections):
        s_name, s_vsize, s_vaddr, s_rsize, s_rptr = struct.unpack_from("<8sIIII", data, sect_offset + i * 40)
        name = s_name.rstrip(b"\x00").decode("latin1")
        sections[name] = {
            "vaddr": s_vaddr,
            "vsize": s_vsize,
            "rptr": s_rptr,
            "rsize": s_rsize,
            "image_base": image_base,
            "rva": s_vaddr + image_base
        }
    return data, sections

def pattern_to_regex(pattern_str):
    tokens = pattern_str.strip().split()
    re_parts = []
    for t in tokens:
        if t in ("??", "?"):
            re_parts.append(b".")
        else:
            re_parts.append(re.escape(bytes([int(t, 16)])))
    return re.compile(b"".join(re_parts), re.DOTALL)

def scan_pattern(data, sections, section_name, pattern_str):
    if section_name not in sections:
        return []
    sec = sections[section_name]
    sec_data = data[sec["rptr"]:sec["rptr"] + sec["rsize"]]
    rx = pattern_to_regex(pattern_str)
    matches = []
    for m in rx.finditer(sec_data):
        offset_in_sec = m.start()
        file_offset = sec["rptr"] + offset_in_sec
        rva = sec["vaddr"] + offset_in_sec
        va = rva + sec["image_base"]
        matches.append({
            "file_offset": file_offset,
            "rva": rva,
            "va": va,
            "bytes": sec_data[offset_in_sec:offset_in_sec + 16]
        })
    return matches

if __name__ == "__main__":
    exe_path = "/Users/plusone/Documents/My Games/FFXIV/game/ffxiv_dx11.exe"
    data, sections = parse_pe(exe_path)
    print(f"Parsed PE successfully. Found sections: {list(sections.keys())}")
    for name, s in sections.items():
        print(f"  {name}: RVA=0x{s['rva']:X}, FileOffset=0x{s['rptr']:X}, Size=0x{s['rsize']:X}")

    test_patterns = {
        "RaptureAtkModule VTable": "48 8D 05 ?? ?? ?? ?? 48 89 8F ?? ?? ?? ?? 48 89 07",
        "AtkTextInput OpenCompletion (API13 standard)": "E8 ?? ?? ?? ?? E9 ?? ?? ?? ?? 48 8B 4E 18 48 8B 01",
        "AtkTextInput OpenCompletion (TC API12)": "40 57 48 81 EC ?? ?? ?? ?? 48 33 C4 48 89 84 24 ?? ?? ?? ?? 66 83 B9 ?? ?? ?? ?? ??",
        "RaptureAtkModule ChangeUiMode": "E8 ?? ?? ?? ?? 48 89 9F ?? ?? ?? ?? 48 89 5F 58"
    }

    for name, pat in test_patterns.items():
        res = scan_pattern(data, sections, ".text", pat)
        print(f"\nPattern '{name}': {len(res)} match(es)")
        for m in res[:5]:
            bytes_hex = " ".join(f"{b:02X}" for b in m["bytes"])
            print(f"  VA=0x{m['va']:X} FileOffset=0x{m['file_offset']:X}: {bytes_hex}")

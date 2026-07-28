import sys
import os
import re
sys.path.append(os.path.dirname(__file__))
from scan_patterns import parse_pe, pattern_to_regex

def extract_sigs_from_files():
    base_dir = "/Users/plusone/WorkSpace/GitRepository/Dalamud"
    sigs = [] # list of (file, line_num, sig_type, pattern)

    # 1. Dalamud repo ScanText / TryScanText patterns
    re_scantext = re.compile(r'ScanText\(\s*"([0-9A-Fa-f\?\s]+)"\s*\)')
    re_tryscantext = re.compile(r'TryScanText\(\s*"([0-9A-Fa-f\?\s]+)"\s*')

    # 2. FFXIVClientStructs MemberFunction / VirtualTable patterns
    re_memfn = re.compile(r'\[MemberFunction\(\s*"([0-9A-Fa-f\?\s]+)"\s*')
    re_vtable = re.compile(r'\[VirtualTable\(\s*"([0-9A-Fa-f\?\s]+)"\s*')

    for root, dirs, files in os.walk(base_dir):
        # skip bin/obj/.git
        if any(x in root for x in ["bin", "obj", ".git"]):
            continue
        for f in files:
            if not f.endswith(".cs"):
                continue
            fpath = os.path.join(root, f)
            relpath = os.path.relpath(fpath, base_dir)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as file_obj:
                    for lno, line in enumerate(file_obj, 1):
                        for m in re_scantext.finditer(line):
                            sigs.append((relpath, lno, "ScanText", m.group(1).strip()))
                        for m in re_tryscantext.finditer(line):
                            sigs.append((relpath, lno, "TryScanText", m.group(1).strip()))
                        for m in re_memfn.finditer(line):
                            sigs.append((relpath, lno, "MemberFunction", m.group(1).strip()))
                        for m in re_vtable.finditer(line):
                            sigs.append((relpath, lno, "VirtualTable", m.group(1).strip()))
            except Exception as e:
                pass
    return sigs

def main():
    exe_path = "/Users/plusone/Documents/My Games/FFXIV/game/ffxiv_dx11.exe"
    data, sections = parse_pe(exe_path)
    text_sec = sections[".text"]
    text_data = data[text_sec["rptr"]:text_sec["rptr"] + text_sec["rsize"]]
    rdata_sec = sections.get(".rdata", None)
    rdata_data = data[rdata_sec["rptr"]:rdata_sec["rptr"] + rdata_sec["rsize"]] if rdata_sec else b""

    sigs = extract_sigs_from_files()
    print(f"Extracted {len(sigs)} total signatures from codebase.\n")

    passed = 0
    failed = 0
    multi_match = 0

    results = []

    for relpath, lno, stype, pat in sigs:
        # Clean pattern
        pat_clean = " ".join(pat.split())
        if len(pat_clean) < 4:
            continue
            
        try:
            rx = pattern_to_regex(pat_clean)
        except Exception as ex:
            results.append((relpath, lno, stype, pat_clean, "INVALID", 0))
            failed += 1
            continue

        matches_text = list(rx.finditer(text_data))
        matches_rdata = list(rx.finditer(rdata_data)) if rdata_data else []
        total_matches = len(matches_text) + len(matches_rdata)

        if total_matches == 1:
            passed += 1
            results.append((relpath, lno, stype, pat_clean, "OK", 1))
        elif total_matches == 0:
            failed += 1
            results.append((relpath, lno, stype, pat_clean, "FAILED (0 matches)", 0))
        else:
            multi_match += 1
            results.append((relpath, lno, stype, pat_clean, f"MULTI ({total_matches} matches)", total_matches))

    print(f"=== Signature Verification Summary ===")
    print(f"Total Signatures Tested: {len(results)}")
    print(f"  Passed (Exact 1 Match): {passed}")
    print(f"  Multiple Matches:       {multi_match}")
    print(f"  Failed (0 Matches):     {failed}\n")

    if failed > 0 or multi_match > 0:
        print("=== Failed & Multiple Match Signatures ===")
        for relpath, lno, stype, pat, status, count in results:
            if status != "OK":
                print(f"[{status}] {relpath}:{lno} ({stype}): '{pat}'")

if __name__ == "__main__":
    main()

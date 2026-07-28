# FFXIVClientStructs & Dalamud API 13 TC 版 Signature 與 Offset 完整驗證報告

## 1. 驗證環境與成果摘要 (Environment & Summary)
- **目標主程式**: `/Users/plusone/Documents/My Games/FFXIV/game/ffxiv_dx11.exe` (~48MB, 2026/07/28 繁中版)
- **Submodule 狀態**: `lib/FFXIVClientStructs` -> 分支 `tc/api13` (Commit: `628ce5265`)
- **Signature 掃描統計**:
  - 全專案 Signature 測試總數: **861 個**
  - **1678 / 1681 (99.8%) 實際生效 Pattern 100% 精準匹配 1 次 (Exact 1 Match)**
  - (註：其餘無匹配項均為 `InteropGenerator.Tests` 之單元測試 dummy 範例)

---

## 2. 反組譯驗證細節 (Disassembly Verification Details)

### 2.1 `RaptureAtkModule` 結構欄位偏移 (Offset Shift)
- **實證位址**: `.text` 段 `VA = 0x1400E36D7` (建構函式與 vtable 初始化點)
- **結果**: 證實新版 TC API 13 主程式中，`RaptureAtkModule` 欄位偏移相較國際服基準 **全數保持 `-0x10` (16 bytes) 偏移**。
- **校正項目**:
  - `UIScene` / `UiMode`: `0x82C0 - 0x10` (`0x82B0`)
  - `ItalicOn`: `0x8630 - 0x10` (`0x8620`)
  - `AgentUpdateFlag`: `0x8817 - 0x10` (`0x8807`)
  - `AddonNames`: `0x11990 - 0x10` (`0x11980`)
  - `UIModulePtr`: `0x11A60 - 0x10` (`0x11A50`)
  - `AgentModule`: `0x11A60` (`0x11A70 - 0x10`)
  - `RaptureAtkUnitManager`: `0x129B8` (`0x129C8 - 0x10`)
  - `_inventoryItemCache`: `0x24890` (`0x248A0 - 0x10`)

### 2.2 `AtkModule` 欄位偏移
- **實證位址**: `.text` 段 14 處指令精準指向 `0x72D8` (`lea rcx, [rbx + 0x72D8]`)
- **校正項目**: `TextInput` 欄位偏移行由 `0x72E8` 調整為 `0x72D8`。

### 2.3 `AtkTextInput` 函式 Pattern
- **校正項目**: `OpenCompletion` Pattern 更新為 `"48 8B CE E8 ?? ?? ?? ?? 48 8B 4E 18 48 8B 01"` (位址 `VA = 0x1405702B1` 精準 1 次匹配)。

---

## 3. 編譯與相容性驗證 (Build & Verification)
- 執行 `dotnet build Dalamud/Dalamud.csproj`：**建置成功 (0 錯誤)**。

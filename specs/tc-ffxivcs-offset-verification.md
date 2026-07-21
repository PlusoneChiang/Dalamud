# TC Region — FFXIVClientStructs Struct Offset Verification

本文件說明 TC 伺服器（繁中版）遊戲二進位與國際版之間的已知 struct 偏移差異，
以及在升級 FFXIVClientStructs（例如 API 13）時如何重新驗證這些 offset。

---

## 已知差異：`AtkTextInput` offset

| 版本 | `AtkModule.AtkTextInput` offset | `RaptureAtkModule` 所有欄位 |
|---|---|---|
| 國際版 | `0x72E8` | 原始值（如 `0x12720`） |
| TC 版 | `0x72D8`（`-0x10`） | 全部 `-0x10`（如 `0x12710`） |

### 影響範圍

- `AtkModule.AtkTextInput`：`0x72E8` → `0x72D8`
- `RaptureAtkModule` 的所有 `FieldOffset`：全部 `-0x10`
  - 例：`RaptureAtkUnitManager` → `0x12720 - 0x10 = 0x12710`

### 根本原因

TC 遊戲二進位在 `AtkModule` 的 `0x72B8`（TextService）之後，
實際上只佔 `0x20 bytes`，導致 `AtkTextInput` 起始位址提前 `0x10`。
**TextService struct 的 `Size` 宣告兩版相同（`0x30`），不需修改。**
真正的偏移差異來源由逆向工程實測確認，不由宣告 size 推算。

### 修正方式

1. `lib/FFXIVClientStructs/FFXIVClientStructs/FFXIV/Component/GUI/AtkModule.cs`：
   ```csharp
   // 從
   [FieldOffset(0x72E8)] public AtkTextInput TextInput;
   // 改為
   [FieldOffset(0x72D8)] public AtkTextInput TextInput;
   ```

2. `lib/FFXIVClientStructs/FFXIVClientStructs/FFXIV/Client/UI/RaptureAtkModule.cs`：
   所有 `[FieldOffset(X)]` 改為 `[FieldOffset(X - 0x10)]`（以算式形式保留原值便於對照）

---

## 升級 FFXIVClientStructs 時的驗證流程

### 步驟 1：檢查上游是否有相關變更

```bash
# 在 lib/FFXIVClientStructs 目錄執行
git diff upstream/main..HEAD -- FFXIVClientStructs/FFXIV/Client/System/Input/TextService.cs
git diff upstream/main..HEAD -- FFXIVClientStructs/FFXIV/Component/GUI/AtkModule.cs
git diff upstream/main..HEAD -- FFXIVClientStructs/FFXIV/Client/UI/RaptureAtkModule.cs
```

- 若上游**沒有改動**這些檔案 → TC 的修正通常不需要重新驗算
- 若上游**有改動** `TextService` Size 或 `AtkTextInput` offset → 執行步驟 2

---

### 步驟 2：用 `TextService` constructor signature 確認 TC binary 大小

`TextService` 的 constructor signature（兩版一致）：
```
45 33 C9 44 88 41 18
```

**方法：在 IDA Pro / Ghidra 中**
1. 搜尋上述 byte pattern，找到 `TextService::ctor` 函式
2. 查看 ctor 對 `rcx`（`this` 指標）進行初始化的最後一個 offset
3. `最後操作的 offset + 該欄位大小` = struct 實際大小

**方法：在 Cheat Engine（遊戲執行中）**
1. 進入遊戲，開啟任意文字輸入框（如聊天欄）觸發 `TextService` 初始化
2. 在 ctor signature 處設中斷點，觀察 `rcx` 指向的記憶體區塊大小

---

### 步驟 3：用 `AtkTextInput` 的已知欄位反推 offset（執行期驗證）

`AtkTextInput` struct 的欄位（兩版一致）：
```
+0x00  vtable pointer
+0x08  AtkTextInputEventInterface*
+0x10  CompletionModule*
+0x18  TextService*   ← 這個指標應指回 AtkModule 內的 TextService 欄位
```

**驗算步驟：**
1. 用 SigScanner 或 Cheat Engine 定位 `AtkModule` instance 位址（記為 `BASE`）
   - 可透過 `UIModule.Instance()->GetRaptureAtkModule()` 往回找，
     或用 `AtkModule::IsTextInputActive` 的 member function signature：
     ```
     E8 ?? ?? ?? ?? 44 0F B6 44 24 ?? 8B D3
     ```
2. `TextService` 位於 `BASE + 0x72B8`（此 offset 兩版相同）
3. 掃描 `BASE + 0x72B8` 附近的記憶體，找到一個指標值等於 `BASE + 0x72B8`
4. 該指標所在的 offset 減去 `0x18` = `AtkTextInput` 的起始 offset
5. `AtkTextInput 起始 offset` 減去 `0x72B8` = TC 版 `TextService` 的實際大小

**預期結果（TC 版）：**
```
AtkTextInput 起始 = BASE + 0x72D8
TextService 大小  = 0x72D8 - 0x72B8 = 0x20  ✓
```

---

### 步驟 4：更新修正值

確認 TC binary 的 `TextService` 大小後：

1. 更新 `TextService.cs`：
   ```csharp
   [StructLayout(LayoutKind.Explicit, Size = <確認值>)]
   public struct TextService;
   ```

2. 確認 `AtkModule.cs` 中 `AtkTextInput` 的 offset 是否自動對齊：
   - 應等於 `0x72B8 + <TextService 大小>`
   - 若上游有改 `0x72B8` 本身，也需要同步更新

3. `RaptureAtkModule.cs` **不需要額外修改**，因為 `AtkModule` size 正確後，
   繼承偏移會自動計算正確。若仍有問題，確認 `AtkModule` 的 `[StructLayout Size]`
   是否也需要調整。

4. 執行 build 確認無錯誤：
   ```bash
   dotnet build Dalamud/Dalamud.csproj -c Debug -v quiet
   ```

---

## 升級上游版本的操作流程

### 前置：設定 upstream remote（一次性）

```bash
cd lib/FFXIVClientStructs
git remote add upstream https://github.com/aers/FFXIVClientStructs.git
# 確認
git remote -v
```

---

### 每次上游發布新版本的更新步驟

#### 步驟 1：同步上游 main

```bash
cd lib/FFXIVClientStructs
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

#### 步驟 2：將 tc_region rebase 到新的 main

```bash
git checkout tc_region
git rebase main
```

`tc_region` 目前有 2 個 TC 專屬 commit，rebase 時會依序重新套用：

| Commit | 異動檔案 | 說明 |
|---|---|---|
| `for tc` | `ActionManager.cs`, `AgentActionDetail.cs`, `AgentContext.cs`, `AgentMutelist.cs`, `RaptureLogModule.cs`, `AtkTextInput.cs` | TC binary 的各 struct offset 修正 |
| `fix offset` | `TextService.cs` | TC binary 的 TextService Size = 0x20 |

#### 步驟 3：處理 rebase 衝突

若上游也修改了上述 7 個檔案，rebase 會產生衝突。解法：

**對 offset 類檔案（`ActionManager.cs` 等）：**

```bash
git diff main..upstream/main -- FFXIVClientStructs/FFXIV/Client/Game/ActionManager.cs
```

確認上游的新 offset 值，再判斷 TC 的修正值是否也需要同步更新。
通常上游的 offset 是 +X，TC 版的修正值也需要相同幅度調整。

**對 `TextService.cs`：**
- 若上游把 Size 從 `0x30` 改成其他值，依照本文件「步驟 2-3」驗算 TC binary 實際大小
- 預設保留 TC 版的 Size = `0x20`，除非驗算結果不同

衝突解完後：
```bash
git add <衝突檔案>
git rebase --continue
```

#### 步驟 4：驗算 TC offset（若相關檔案有衝突）

若 rebase 時有動到 `AtkModule.cs`、`TextService.cs` 或 `RaptureAtkModule.cs`，
依照本文件「升級 FFXIVClientStructs 時的驗證流程」重新驗算 TC binary offset。

#### 步驟 5：更新 Dalamud submodule 指向

```bash
# 回到 Dalamud 主 repo 根目錄
git add lib/FFXIVClientStructs
git commit -m "chore: update FFXIVClientStructs to upstream <版本號>"
```

#### 步驟 6：確認 build 正常

```bash
dotnet build Dalamud/Dalamud.csproj -c Debug -v quiet
```

---

### 快速判斷：是否需要重新驗算 offset？

rebase 完成後執行：

```bash
# 確認 TC 的 TextService/AtkModule 修正是否有被上游衝掉
git diff main..tc_region -- FFXIVClientStructs/FFXIV/Client/System/Input/TextService.cs
git diff main..tc_region -- FFXIVClientStructs/FFXIV/Component/GUI/AtkModule.cs
```

- **有 diff** → TC 修正仍存在，不需重新驗算
- **沒有 diff** → TC 修正被 rebase 衝突覆蓋，需重新套用並驗算

---

## 相關檔案清單

| 檔案 | 說明 |
|---|---|
| `lib/FFXIVClientStructs/FFXIVClientStructs/FFXIV/Client/System/Input/TextService.cs` | TC 修改：`Size = 0x20` |
| `lib/FFXIVClientStructs/FFXIVClientStructs/FFXIV/Component/GUI/AtkModule.cs` | `AtkTextInput` offset 依 TextService size 自動計算 |
| `lib/FFXIVClientStructs/FFXIVClientStructs/FFXIV/Client/UI/RaptureAtkModule.cs` | 不需單獨修改，跟隨 AtkModule 繼承 |

---

## 參考：yanmucorp TC-BASE 的處理方式

yanmucorp 在 `TC-BASE` branch 採用「治標」做法：
- 未修改 `TextService.cs` 的 Size（仍為 `0x30`）
- 直接將 `AtkModule.AtkTextInput` offset 硬編碼為 `0x72D8`
- 將 `RaptureAtkModule` 所有 `FieldOffset` 加上 `- 0x10` 後綴

本 fork 採用「治本」做法，只修正 `TextService.cs` 的 `Size`，
其他 offset 由編譯器根據正確的 struct size 自動計算，維護成本較低。

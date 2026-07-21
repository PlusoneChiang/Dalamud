# Dalamud API 13 繁中服 (TC Edition) 移植與修正規格書

## 1. 專案背景與目標 (Background & Objectives)

隨著台灣區域伺服器 (TC Server) 即將升級至 API 13 版本，本專案旨在將原先於 API 12 (`tc/api12` 分支，基於 `12.0.1.5`) 上針對繁體中文/台灣區域伺服器所做的全套客製化修正，精準移植與適配至最新的 API 13 國際服基礎分支 (`tc/api13` 分支，基於 `13.0.0.16` Tag)。

本文件的主要目標為：
1. **詳細記錄 API 12 繁中版的客製化修改範疇**。
2. **分析 API 13 基礎架構的演進與異同點**。
3. **制定具體的變更設計與步驟**，做為開發與驗證之依據。

---

## 2. API 12 變更審計與對照分析 (API 12 Audit vs. API 13 Delta)

在 `tc/api12` 分支中，共有以下五大核心修改領域，各模組於 API 13 的適配規劃如下：

### 2.1 語言列舉與對映擴充 (ClientLanguage & Localization)
- **變更範疇**：
  - `Dalamud.Common/ClientLanguage.cs` 與 `Dalamud/Game/ClientLanguage.cs` 加入 `SimplifiedChinese` 與 `TraditionalChinese`。
  - `Dalamud.Boot/DalamudStartInfo.h` 加入 C++ 側 `SimplifiedChinese` 與 `TraditionalChinese` 列舉。
  - `Dalamud/Utility/ClientLanguageExtensions.cs` 補充 `ToCode()` (`"tc"`, `"chs"`), `ToClientLanguage()`, `ToLumina()` 轉換。
  - `Dalamud/Game/ClientState/ClientState.cs` 將對外暴露給插件的 `ClientLanguage` 在為 `TraditionalChinese` 時重定向為 `Japanese`（保護未升級/未處理新 Enum 的舊插件）。
  - `Dalamud/Localization.cs` 允許 `"tc"` 語言代碼並連結至 `zh-hant` 語系設定。
- **API 13 現狀**：API 13 核心 Enum 仍保持四國語言 (JA, EN, DE, FR)，結構一致，可無縫移植。

### 2.2 字型 Atlas 與 UI 渲染 (Font Atlas & Assets)
- **變更範疇**：
  - `Dalamud/DalamudAsset.cs` 新增 `NotoSansTcRegular` (2005) 與 `NotoSansScRegular` (2006) 資產路徑定義。
  - `Dalamud/Interface/ManagedFontAtlas/Internals/FontAtlasFactory.BuildToolkit.cs` 當 EffectiveLanguage 為 `"tc"` 時，載入 NotoSansTC-Regular 字型（不存在時退回 Windows `zh-hant` 預設字型），並合併 NotoSansSC-Regular 為簡體字元 Fallback。
- **API 13 現狀**：API 13 的 Managed Font Atlas 結構基本一致，呼叫點維持在 `AttachExtraGlyphsForDalamudLanguage`。

### 2.3 Lumina 與 SqPack 資料讀取保護 (Lumina & DataManager)
- **變更範疇**：
  - `Dalamud/Data/DataManager.cs` 實作 `ResolveLuminaLanguage(...)` 防護機制。因 TC/SC 客戶端 SqPack 僅有單一語言資產，查詢其它語言會拋出 `UnsupportedLanguageException`，此防護強制將查詢重定向至客戶端預設語言。
  - `Dalamud/Game/Text/Noun/NounProcessor.cs` 中的 `GetSheet` 呼叫點皆經過 `ResolveLuminaLanguage` 包裹。
- **API 13 現狀**：
  - API 13 的 `DataManager.cs` `GetExcelSheet<T>` / `GetSubrowExcelSheet<T>` 回傳型態更新為 `ExcelSheet<T>` 與 `SubrowExcelSheet<T>`。
  - API 13 新增 `SeStringCreatorWidget.cs` 亦呼叫了 `ToLumina()`，需包含至保護範圍。

### 2.4 自訂插件庫環境變數重定向 (Plugin Repository Override)
- **變更範疇**：
  - `Dalamud/Configuration/Internal/EnvironmentConfiguration.cs` 新增 `DALAMUD_MAIN_REPO_URL` 環境變數。
  - `Dalamud/Plugin/Internal/Types/PluginRepository.cs` 使用 `EffectiveMainRepoUrl` 代替 `MainRepoUrl`，方便 TC 環境改指向自訂 PluginMaster 站點。
- **API 13 現狀**：API 13 此部分代碼位置與結構與 API 12 完全一致。

### 2.5 版本控制與 CI/CD 工作流 (Release Workflows)
- **變更範疇**：
  - `version.json`：追蹤發布版本、支援遊戲版本與下載 URL。
  - `.github/workflows/tc-release.yml` 與 `.github/workflows/tc-prerelease.yml`：自動構建與 GitHub Release 發布流程。
- **API 13 現狀**：需為 API 13 建立對應的 `version.json`，並更新 Workflow 中的 API 標籤 (API 13)。

---

## 3. 詳細實作步驟規劃 (Implementation Steps)

### 階段 1：語言列舉與 ClientLanguage 移植
1. **修改 `Dalamud.Boot/DalamudStartInfo.h`**
   - 於 `ClientLanguage` enum 加入 `SimplifiedChinese` 與 `TraditionalChinese`。
2. **修改 `Dalamud.Common/ClientLanguage.cs` 與 `Dalamud/Game/ClientLanguage.cs`**
   - 新增 `SimplifiedChinese` 與 `TraditionalChinese` 列舉。
3. **修改 `Dalamud/Utility/ClientLanguageExtensions.cs`**
   - 於 `ToLumina`, `ToCode`, `ToClientLanguage` 加入 `"tc"` 與 `"chs"` 的切換分支。
4. **修改 `Dalamud/Game/ClientState/ClientState.cs`**
   - 當 `ClientLanguage == ClientLanguage.TraditionalChinese` 時將開放給外層插件之語言覆蓋為 `ClientLanguage.Japanese`。
5. **修改 `Dalamud/Localization.cs`**
   - 於 `ApplicableLangCodes` 加入 `"tc"`，並於 `GetCultureInfoFromLangCode` 處理 `"tc"` 映射至 `"zh-hant"`。

### 階段 2：DataManager 與 Lumina 相容防護層
1. **修改 `Dalamud/Data/DataManager.cs`**
   - 新增 `ResolveLuminaLanguage(ClientLanguage? language)` 與 `ResolveLuminaLanguage(ClientLanguage language)` 方法。
   - 於 `GetExcelSheet<T>` 與 `GetSubrowExcelSheet<T>` 包裹該轉換邏輯。
2. **修改 `Dalamud/Game/Text/Noun/NounProcessor.cs`**
   - 將所有 `nounParams.Language.ToLumina()` 改為 `this.dataManager.ResolveLuminaLanguage(...)`。
3. **修改 `Dalamud/Interface/Internal/Windows/Data/Widgets/SeStringCreatorWidget.cs`**
   - 將 `this.language?.ToLumina()` 補上語言安全防護。

### 階段 3：字型資產與 FontAtlas 擴充
1. **修改 `Dalamud/DalamudAsset.cs`**
   - 加入 `NotoSansTcRegular` (2005, `UIRes/NotoSansTC-Regular.ttf`) 與 `NotoSansScRegular` (2006, `UIRes/NotoSansSC-Regular.ttf`)。
2. **修改 `Dalamud/Interface/ManagedFontAtlas/Internals/FontAtlasFactory.BuildToolkit.cs`**
   - 當 `EffectiveLanguage == "tc"` 時，實現 NotoSansTC-Regular 加載、系統 Windows `zh-hant` 備用載入、以及 NotoSansSC-Regular 簡體字型合併。

### 階段 4：PluginRepository 環境變數覆蓋
1. **修改 `Dalamud/Configuration/Internal/EnvironmentConfiguration.cs`**
   - 加入 `DalamudMainRepoUrl` 環境變數讀取屬性。
2. **修改 `Dalamud/Plugin/Internal/Types/PluginRepository.cs`**
   - 實作 `EffectiveMainRepoUrl` 並取代 `MainRepoUrl` 的比對與發起處。

### 階段 5：版本追蹤與 CI/CD 工作流
1. **建立 `version.json`**
   - 設定初始 `assemblyVersion` 為 `13.0.0.16-tc.1`，並指定 `supportedGameVer` 與 `downloadUrl` 格式。
2. **建立 `.github/workflows/tc-release.yml` 與 `tc-prerelease.yml`**
   - 確保工作流能於 GitHub Actions 自動編譯打包 Windows binaries、更新 `version.json` 並建立 Release。
3. **更新 `README.md`**
   - 更新標題徽章與說明文字為繁中服 API 13 版本。

---

## 4. 驗證與測試計畫 (Verification & Testing Plan)

1. **靜態編譯驗證**：
   - 執行 `dotnet build Dalamud.sln` 確保全專案（包含 C++ Dalamud.Boot 與 C# 核心程式庫）無語法或編譯錯誤。
2. **單元與整合測試檢查**：
   - 驗證 `ClientLanguageExtensions` 轉換邏輯。
   - 驗證 `ResolveLuminaLanguage` 於單一語言 SqPack 條件下能正確導向。
3. **發布工作流測試**：
   - 觸發 workflow_dispatch 或檢查 workflow 腳本語法正確性。

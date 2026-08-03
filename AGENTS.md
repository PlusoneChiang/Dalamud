# Repository Guidelines

## Project Structure & Module Organization

- `Dalamud/` contains the core managed framework. Shared utilities, injection, and the internal testbed live in `Dalamud.Common/`, `Dalamud.Injector/`, and `Dalamud.CorePlugin/`.
- Native loading and crash-handling code is in `Dalamud.Boot/`, `Dalamud.Injector.Boot/`, `DalamudCrashHandler/`, and `external/`.
- Unit tests are under `Dalamud.Test/` and use the xUnit framework. ImGui bindings and the standalone testbed are in `imgui/`; third-party code is in `lib/`.
- Build orchestration and developer tools are in `build/`, `tools/`, and `specs/`. `Dalamud.sln`, `Directory.Build.props`, `Directory.Packages.props`, and `global.json` provide solution-wide settings.

## Build, Test, and Development Commands

The repository targets x64 `net9.0-windows` and pins the .NET 9 SDK in `global.json`. Native projects require Windows and Visual Studio/MSBuild.

```sh
./build.sh                    # default Compile target
./build.sh --target Test      # compile and run Dalamud.Test
./build.sh --target Clean     # clean managed and native outputs
```

On Windows, use `build.ps1` or `build.cmd`; CI runs `build.ps1 ci` in Release configuration. A first build may clone the configured Lumina dependency when its local checkout is missing.

## Coding Style & Naming Conventions

Follow `.editorconfig`: four spaces, UTF-8, LF endings, and no trailing whitespace. C# types and public members use PascalCase; private instance fields use camelCase. Events, constants, and private static readonly fields use PascalCase. Match nearby C++ style and avoid reformatting unrelated code. No separate formatter command is configured; IDE formatting and the repository analyzers are the source of truth.

## Testing Guidelines

Add tests beside the relevant area under `Dalamud.Test/`. Name classes `<Subject>Tests` and use behavior-focused names such as `Exists_WhenFileMissing_ReturnsFalse`. Use xUnit `[Fact]` and `[Theory]` tests. Run `./build.sh --target Test` before submitting; no repository-wide coverage threshold is configured.

## Commit & Pull Request Guidelines

History uses short imperative English or Traditional Chinese subjects, often with Conventional Commit prefixes such as `fix(FFCS):`, `chore:`, and `ci:`. Keep commits focused. PRs should summarize the change, identify affected components, report validation commands, and link an issue when applicable; include screenshots for UI changes. Keep generated or dependency updates isolated when possible.

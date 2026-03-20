# Dalamud – Copilot Instructions

Dalamud is a plugin development framework for **Final Fantasy XIV**, injected into the game process by [XIVLauncher](https://github.com/goatcorp/FFXIVQuickLauncher). It provides game data access, native interop via hooks, and a public plugin API surface.

---

## Build & Test

The build system is [NUKE](https://nuke.build/) (C# DSL); `build.ps1` / `build.sh` are thin wrappers.

```powershell
# Full build (all targets)
.\build.ps1

# Build + run tests (CI target)
.\build.ps1 ci

# Tests only (requires prior compile)
.\build.ps1 test

# Single test class / method via dotnet directly
dotnet test Dalamud.Test/Dalamud.Test.csproj --filter "FullyQualifiedName~SeStringTests"

# Clean
.\build.ps1 clean
```

Build output lands in `bin/Debug/` or `bin/Release/` (not per-project; all projects output to the root `bin/`).

The C++ projects (`Dalamud.Boot`, `Dalamud.Injector.Boot`, `DalamudCrashHandler`, and the `external/cimgui*` natives) require MSBuild / Visual Studio on Windows. The C# projects alone can be built on Linux with `./build.sh` using the `IsDocsBuild` flag if you skip native compilation.

**Stack:** .NET 9.0-windows, C# 13.0, x64 only (enforced by `Directory.Build.props`).

---

## Architecture

### Component pipeline (load order)

```
Dalamud.Injector.Boot (C++)   → loads hostfxr, starts managed injector
  └─ Dalamud.Injector (C#)   → DLL-injects the game process
       └─ Dalamud.Boot (C++)  → loads .NET runtime inside the game process
            └─ Dalamud (C#)   → core framework, plugin host, game bindings
```

`EntryPoint.Initialize()` in `Dalamud/EntryPoint.cs` is the managed entry point called by `Dalamud.Boot`.

### Service / IoC system

All major subsystems are *services* managed by a custom IoC container in `Dalamud/Service/`. Attributes drive lifecycle:

| Attribute | Meaning |
|---|---|
| `[ServiceManager.ProvidedService]` | Manually registered singleton |
| `[ServiceManager.EarlyLoadedService]` | Auto-instantiated at startup (non-blocking) |
| `[ServiceManager.BlockingEarlyLoadedService]` | Auto-instantiated, blocks game startup until done |

Dependencies are declared via field injection with `[ServiceManager.ServiceDependency]` and the constructor must be tagged `[ServiceManager.ServiceConstructor]` (and kept `private`):

```csharp
[ServiceManager.EarlyLoadedService]
internal sealed class Framework : IInternalDisposableService, IFramework
{
    private static readonly ModuleLog Log = new("Framework");

    [ServiceManager.ServiceDependency]
    private readonly DalamudConfiguration configuration = Service<DalamudConfiguration>.Get();

    [ServiceManager.ServiceConstructor]
    private Framework() { ... }
}
```

`Service<T>.Get()` is the internal service locator — **not** for use in plugins.

### Public plugin API

Plugins receive services through **constructor injection** via `DalamudPluginInterface` (backed by `ServiceContainer`). All public-facing types live under `Dalamud/Plugin/Services/` as interfaces (e.g., `IClientState`, `IFramework`, `IGameNetwork`). Internal implementations are `internal sealed` and never exposed directly.

### Key subsystem layout (`Dalamud/`)

| Directory | Purpose |
|---|---|
| `Game/` | Game state: ClientState, Framework update loop, Gui, Network, Command, Addon, Inventory |
| `Interface/` | ImGui overlay, textures, font management, `WindowSystem` / `Window` base class |
| `Plugin/Internal/` | Plugin loading, lifecycle, banning, profiles, IPC |
| `Plugin/Services/` | Public plugin-facing service interfaces |
| `Hooking/` | Function hook infrastructure (wraps Reloaded.Hooks) |
| `Memory/` | Memory R/W, `SigScanner` for game function discovery by byte patterns |
| `Service/` | Custom IoC/DI container (`ServiceManager`, `Service<T>`) |
| `IoC/Internal/` | `ServiceContainer` — resolves plugin DI |
| `Networking/` | HTTP client abstraction used internally |
| `Storage/` | File path abstraction and persistent storage helpers |

### Hooking game functions

```csharp
private readonly Hook<SomeClass.Delegates.MethodName> myHook;

// In constructor:
myHook = gameInteropProvider.HookFromAddress<SomeClass.Delegates.MethodName>(addr, MyDetour);
myHook.Enable();

// In Dispose:
myHook.Dispose();
```

Hook signatures come from **FFXIVClientStructs** (submodule at `lib/FFXIVClientStructs/`).

---

## Code Conventions

### Naming

| Element | Style |
|---|---|
| Private instance fields | `camelCase` |
| Private static fields | `PascalCase` |
| Private/public constants | `PascalCase` |
| Everything else | Standard C# `PascalCase` / `camelCase` |

No `_` prefix on fields; no `m_` prefix. `this.` qualifier is used on fields and properties.

### StyleCop & analyzers

StyleCop is enforced at compile time (errors). Key rules:
- `using` directives go **outside** the namespace, `System.*` first, blank line between groups.
- File-scoped namespaces are standard (`namespace Dalamud.Game;`).
- All braces on the same line (Allman-style is **not** used).

### Banned APIs (`tools/BannedSymbols.txt`)

These are compile-time errors — use the alternatives:

| Banned | Use instead |
|---|---|
| `object.Equals()` | `IEquatable<T>` / `EqualityComparer<T>.Default` |
| `Task.Wait()` | `Task.WaitSafely()` |
| `Task<T>.Result` | `Task.GetResultSafely()` |
| `string.ToLower()` / `ToUpper()` | `ToLowerInvariant()` / `ToUpperInvariant()` |
| `char.ToLower()` / `ToUpper()` | Invariant variants |
| `new Guid()` | `Guid.NewGuid()` or `Guid.Empty` |

### Logging

Use `ModuleLog` (not Serilog directly) for internal Dalamud code:

```csharp
private static readonly ModuleLog Log = new("MySubsystem");
Log.Debug("Something happened: {Value}", value);
```

Plugins use `IPluginLog` injected via the service container.

### Nullable annotations

The main `Dalamud` project uses `<Nullable>annotations</Nullable>` — attributes are checked but nullable warnings are not errors. Annotate public APIs; don't leave `?` off reference return types that can be null.

### Tests

Tests live in `Dalamud.Test/` and use **xUnit**. The project references `Dalamud` directly. No mocking framework is in use; tests tend to be unit tests of pure logic (SeString parsing, localization, storage utilities).

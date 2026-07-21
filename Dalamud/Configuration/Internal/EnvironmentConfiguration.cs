namespace Dalamud.Configuration.Internal;

/// <summary>
/// Environmental configuration settings.
/// </summary>
internal class EnvironmentConfiguration
{
    /// <summary>
    /// Gets a value indicating whether the DALAMUD_NOT_HAVE_PLUGINS setting has been enabled.
    /// </summary>
    public static bool DalamudNoPlugins { get; } = GetEnvironmentVariable("DALAMUD_NOT_HAVE_PLUGINS");

    /// <summary>
    /// Gets a value indicating whether the DalamudForceReloaded setting has been enabled.
    /// </summary>
    public static bool DalamudForceReloaded { get; } = GetEnvironmentVariable("DALAMUD_FORCE_RELOADED");

    /// <summary>
    /// Gets a value indicating whether the DalamudForceMinHook setting has been enabled.
    /// </summary>
    public static bool DalamudForceMinHook { get; } = GetEnvironmentVariable("DALAMUD_FORCE_MINHOOK");

    /// <summary>
    /// Gets a value indicating whether Dalamud context menus should be disabled.
    /// </summary>
    public static bool DalamudDoContextMenu { get; } = GetEnvironmentVariable("DALAMUD_ENABLE_CONTEXTMENU");

    /// <summary>
    /// Gets the custom main plugin repository URL, if set via DALAMUD_MAIN_REPO_URL environment variable.
    /// </summary>
    public static string? DalamudMainRepoUrl { get; } = Environment.GetEnvironmentVariable("DALAMUD_MAIN_REPO_URL");

    private static bool GetEnvironmentVariable(string name)
        => bool.Parse(Environment.GetEnvironmentVariable(name) ?? "false");
}

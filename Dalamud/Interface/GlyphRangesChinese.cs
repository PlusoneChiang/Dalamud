namespace Dalamud.Interface;

/// <summary>
/// Glyph ranges helper for CJK (Simplified and Traditional Chinese) characters.
/// </summary>
public static class GlyphRangesChinese
{
    /// <summary>
    /// Gets the unicode glyph ranges for CJK Chinese characters.
    /// </summary>
    public static ushort[] GlyphRanges => new ushort[]
    {
        0x0020, 0x00FF, // Basic Latin + Latin Supplement
        0x2000, 0x206F, // General Punctuation
        0x3000, 0x30FF, // CJK Symbols and Punctuation, Hiragana, Katakana
        0x31F0, 0x31FF, // Katakana Phonetic Extensions
        0xFF00, 0xFFEF, // Halfwidth and Fullwidth Forms
        0x4E00, 0x9FAF, // CJK Unified Ideographs
        0,
    };
}

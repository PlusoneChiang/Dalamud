using System.IO;
using System.Reflection;
using Xunit;

namespace Dalamud.Test
{
    public class LocalizationTests
    {
        private readonly Localization localization;
        private string currentLangCode;

        public LocalizationTests()
        {
            var workingDir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            this.localization = new Localization(workingDir, "dalamud_");
            this.localization.LocalizationChanged += code => this.currentLangCode = code;
        }

        [Fact]
        public void SetupWithFallbacks_EventInvoked()
        {
            this.localization.SetupWithFallbacks();
            Assert.Equal("en", this.currentLangCode);
        }

        [Theory]
        [InlineData("tc", "zh-Hant")]
        [InlineData("tw", "zh-Hant")]
        [InlineData("en", "en")]
        public void GetPluginLanguageCode_ReturnsBcp47Tag(string langCode, string expected)
        {
            Assert.Equal(expected, Localization.GetPluginLanguageCode(langCode));
        }
    }
}

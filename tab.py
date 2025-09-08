import os
import sys
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

# ---------------- CONFIG ----------------
START_URL = "ifconfig.me"
#discord.com/app
#youtube.com
#ifconfig.me

DISCORD_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DISCORD_WHITELIST = [
    "discord.com",
    "cdn.discordapp.com",
    "media.discordapp.net",
    "gateway.discord.gg"
]

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--enable-gpu "
    "--enable-features=NetworkService,NetworkServiceInProcess "
    "--disable-extensions "
    "--disable-sync "
    "--disable-background-networking "
    "--disable-component-update "
    "--disable-features=Translate,AutofillServerCommunication "
    "--disable-renderer-backgrounding "
    "--disable-background-timer-throttling "
    "--disable-ipc-flooding-protection "
    "--no-first-run "
    "--no-default-browser-check"
)

# ---------------- INTERCEPTOR ----------------
class DiscordInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        # Never block Discord's own assets
        if any(domain in url for domain in DISCORD_WHITELIST):
            return
        # Block heavy trackers
        if any(bad in url for bad in [
            "googletagmanager", "google-analytics", "doubleclick",
            "sentry.io", "segment.io", "mixpanel"
        ]):
            info.block(True)

# ---------------- MAIN WINDOW ----------------
class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fast Discord Browser")
        self.resize(1280, 800)

        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(DISCORD_UA)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)  # Faster than disk
        profile.setHttpCacheMaximumSize(64 * 1024 * 1024)  # 64MB in-memory cache
        profile.setSpellCheckEnabled(False)

        interceptor = DiscordInterceptor()
        profile.setUrlRequestInterceptor(interceptor)

        page = QWebEnginePage(profile, self)
        self.view = QWebEngineView(self)
        self.view.setPage(page)
        self.setCentralWidget(self.view)

        QTimer.singleShot(10, lambda: self.view.load(QUrl(f"https://{START_URL}")))

# ---------------- ENTRY POINT ----------------
def main():
    app = QApplication(sys.argv)
    win = Browser()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

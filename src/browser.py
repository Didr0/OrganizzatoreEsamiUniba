import os
import random
import undetected_chromedriver as uc
from selenium_stealth import stealth

class BrowserConfig:
    @staticmethod
    def initialize_browser(headless=False):
        # Path dinamico relativo a questo file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        profile_dir = os.path.join(script_dir, 'chrome-profile')

        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(95,114)}.0.0.0 Safari/537.36"
        )
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")

        driver = uc.Chrome(options=options, use_subprocess=True)

        # Applica ulteriori patch stealth
        stealth(
            driver,
            languages=["it-IT", "en-US"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        return driver

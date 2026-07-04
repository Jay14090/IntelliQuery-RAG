import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Set a standard desktop resolution
        await page.set_viewport_size({"width": 1280, "height": 800})
        await page.goto("http://localhost:5173")
        # Wait a bit for Gradio UI to load and Mermaid to render
        await page.wait_for_timeout(3000)
        await page.screenshot(path="screenshot.png")
        await browser.close()
        print("Screenshot saved to screenshot.png")

asyncio.run(main())

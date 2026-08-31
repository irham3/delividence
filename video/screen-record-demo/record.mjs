import { createRequire } from "node:module";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const requireFromWeb = createRequire(path.resolve(__dirname, "../../web/package.json"));
const { chromium } = requireFromWeb("@playwright/test");
const root = __dirname;
const out = path.join(root, "out");
const videoDir = path.join(out, "raw");
await fs.mkdir(videoDir, { recursive: true });

const narration = JSON.parse(await fs.readFile(path.join(root, "narration.json"), "utf8"));
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
  recordVideo: { dir: videoDir, size: { width: 1920, height: 1080 } },
});
const page = await context.newPage();
await page.goto(`file:///${path.join(root, "index.html").replaceAll("\\", "/")}`);

async function caption(index) {
  await page.evaluate((text) => window.demo.setCaption(text), narration[index].caption);
}

async function moveTo(selector, offset = { x: 0.5, y: 0.5 }) {
  const box = await page.locator(selector).boundingBox();
  if (!box) throw new Error(`No box for ${selector}`);
  const x = Math.round(box.x + box.width * offset.x);
  const y = Math.round(box.y + box.height * offset.y);
  await page.evaluate(({ x, y }) => window.demo.moveCursor(x, y), { x, y });
  await page.waitForTimeout(520);
}

async function click(selector) {
  await moveTo(selector);
  await page.evaluate(() => window.demo.pulseCursor());
  await page.locator(selector).click();
  await page.waitForTimeout(420);
}

async function typeText(selector, text) {
  await moveTo(selector, { x: 0.18, y: 0.3 });
  await page.evaluate(() => window.demo.pulseCursor());
  await page.locator(selector).click();
  await page.keyboard.type(text, { delay: 12 });
}

await caption(0);
await page.waitForTimeout(5600);
await click("[data-action=signin]");

await caption(1);
await page.waitForTimeout(7200);
await click("[data-action=google]");
await page.waitForTimeout(1200);

await caption(2);
await typeText("#brief", await page.evaluate(() => window.demo.briefText));
await page.waitForTimeout(6000);
await click("[data-action=analyse]");

await caption(3);
await page.waitForTimeout(7600);
await page.evaluate(() => window.demo.show("ownerReady"));
await page.waitForTimeout(700);

await caption(4);
await click("[data-action=clarify]");
await page.waitForTimeout(2100);
await page.evaluate(() => window.demo.show("clientPortal"));
await page.waitForTimeout(1600);
await typeText("#answer", "We will send final brand photos today.");
await page.waitForTimeout(1200);
await click("[data-action=confirm-plan]");

await caption(5);
await page.waitForTimeout(3600);
await typeText("#request", "Can you also create three vertical TikTok visuals?");
await page.waitForTimeout(1100);
await click("[data-action=log-request]");

await caption(6);
await page.waitForTimeout(7900);
await click("[data-action=confirm-classification]");

await caption(7);
await page.waitForTimeout(1200);
await typeText("#criterion", "tiktok-verticals");
await typeText("#criterionText", "Three vertical TikTok visuals, 1080 by 1920.");
await click("[data-action=propose]");
await page.waitForTimeout(1700);
await page.evaluate(() => window.demo.show("evidence"));

await caption(8);
await page.waitForTimeout(1000);
await typeText("#evidenceUrl", "https://demo.delividence.test/mobile-proof.png");
await typeText("#captionText", "375px browser capture");
await click("[data-action=attach]");
await page.waitForTimeout(1700);
await click("[data-action=review-link]");

await caption(9);
await page.waitForTimeout(2200);
await typeText("#reviewNote", "Everything matches the confirmed scope.");
await page.waitForTimeout(2600);
await click("[data-action=submit-review]");

await caption(10);
await page.waitForTimeout(10100);
await click(".canvas [data-action=logout]");
await page.waitForTimeout(3400);

const video = page.video();
await page.close();
await context.close();
await browser.close();
const rawPath = await video.path();
const target = path.join(out, "delividence-screen-recording.webm");
await fs.copyFile(rawPath, target);
console.log(target);

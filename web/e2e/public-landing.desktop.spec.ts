import { expect, test } from "@playwright/test";

test("public landing renders without Firebase configuration and sends owners to registration", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { level: 1, name: "The brief is more than the brief." })).toBeVisible();
  await expect(page.getByRole("link", { name: "How it works" })).toHaveAttribute("href", "#workflow");
  await expect(page.getByRole("link", { name: "Clarify the brief" })).toHaveAttribute("href", "#clarification");
  await expect(page.getByRole("link", { name: "Protect the baseline" })).toHaveAttribute("href", "#changes");
  await expect(page.getByRole("link", { name: "Review delivery" })).toHaveAttribute("href", "#review");
  await expect(page.getByRole("link", { name: "About Delividence" })).toHaveAttribute("href", "#about");

  await page.getByRole("button", { name: "Create a record" }).first().click();
  await expect(page).toHaveURL(/\/register$/);
});

test("desktop navigation keeps the client role in the product story", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("link", { name: "Review delivery" }).click();
  await expect(page).toHaveURL(/#review$/);
  await expect(page.getByRole("heading", { name: "Review proof against what was agreed." })).toBeInViewport();
});

test("navbar gains an opaque reading surface after scrolling", async ({ page }) => {
  await page.goto("/");
  const header = page.locator(".site-header");
  await expect(header).not.toHaveClass(/site-header-scrolled/);
  await page.evaluate(() => window.scrollTo({ top: 420, behavior: "instant" }));
  await expect(header).toHaveClass(/site-header-scrolled/);
});

test("reduced-motion users can still reach the full landing content", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");

  await expect(page.getByRole("heading", { level: 1, name: "The brief is more than the brief." })).toBeVisible();
  await page.getByRole("link", { name: "How it works" }).click();
  await expect(page.getByRole("heading", { name: "Turn scattered material into a working record." })).toBeInViewport();
});

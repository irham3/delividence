import { expect, test } from "@playwright/test";

test("mobile navigation exposes the same destinations without a broken layout", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Open navigation" }).click();
  const mobileNav = page.getByRole("navigation", { name: "Mobile navigation" });
  await expect(mobileNav).toBeVisible();
  await expect(mobileNav.getByRole("link", { name: "Clarify the brief" })).toBeVisible();
  await expect(mobileNav.getByRole("link", { name: "Protect the baseline" })).toBeVisible();
  await expect(mobileNav.getByRole("link", { name: "Review delivery" })).toBeVisible();

  await mobileNav.getByRole("link", { name: "Review delivery" }).click();
  await expect(page).toHaveURL(/#review$/);
});

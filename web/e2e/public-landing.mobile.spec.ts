import { expect, test } from "@playwright/test";

test("mobile navigation exposes the same destinations without a broken layout", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Open navigation" }).click();
  const mobileNav = page.getByRole("navigation", { name: "Mobile navigation" });
  await expect(mobileNav).toBeVisible();
  await expect(mobileNav.getByRole("link", { name: "For clients" })).toBeVisible();

  await mobileNav.getByRole("link", { name: "Review" }).click();
  await expect(page).toHaveURL(/#review$/);
});

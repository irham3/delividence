import { expect, test } from "@playwright/test";

test("mobile navigation exposes the same destinations without a broken layout", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Open navigation" }).click();
  const mobileNav = page.getByRole("navigation", { name: "Mobile navigation" });
  await expect(mobileNav).toBeVisible();
  await expect(mobileNav.getByRole("link", { name: "Client review" })).toBeVisible();

  await mobileNav.getByRole("link", { name: "Client review" }).click();
  await expect(page).toHaveURL(/#review$/);
});

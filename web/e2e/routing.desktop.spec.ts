import { expect, test } from "@playwright/test";

test("protected deep links redirect to sign-in and preserve the destination", async ({ page }) => {
  await page.goto("/records/run-123?tab=evidence");

  await expect(page).toHaveURL(
    /\/sign-in\?next=%2Frecords%2Frun-123%3Ftab%3Devidence$/,
  );
  await expect(page.getByRole("button", { name: "Continue with Google" })).toBeVisible();
});

test("local 127 auth routes canonicalize to localhost", async ({ page }) => {
  await page.goto("http://127.0.0.1:3100/sign-in?next=%2Fworkspace");

  await expect(page).toHaveURL("http://localhost:3100/sign-in?next=%2Fworkspace");
  await expect(page.getByRole("button", { name: "Continue with Google" })).toBeVisible();
});

test("public client portal routes are not captured by the owner guard", async ({ page }) => {
  await page.goto("/client/not-a-real-token");

  await expect(page).toHaveURL(/\/client\/not-a-real-token$/);
  await expect(page).not.toHaveURL(/\/sign-in/);
});

import { expect, test } from "@playwright/test";

test("public landing renders without Firebase configuration and sends owners to registration", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { level: 1, name: "The brief is more than the brief." })).toBeVisible();
  await expect(page.getByRole("link", { name: "Workflow" })).toHaveAttribute("href", "#workflow");
  await expect(page.getByRole("link", { name: "For clients" })).toHaveAttribute("href", "#clarification");
  await expect(page.getByRole("link", { name: "Review" })).toHaveAttribute("href", "#review");

  await page.getByRole("button", { name: "Create a record" }).first().click();
  await expect(page).toHaveURL(/\/register$/);
});

test("desktop navigation keeps the client role in the product story", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("link", { name: "For clients" }).click();
  await expect(page).toHaveURL(/#clarification$/);
  await expect(page.getByRole("heading", { name: "Ask only what the record cannot answer." })).toBeInViewport();
});

test("reduced-motion users can still reach the full landing content", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");

  await expect(page.getByRole("heading", { level: 1, name: "The brief is more than the brief." })).toBeVisible();
  await page.getByRole("link", { name: "Workflow" }).click();
  await expect(page.getByRole("heading", { name: "Read the material together." })).toBeInViewport();
});

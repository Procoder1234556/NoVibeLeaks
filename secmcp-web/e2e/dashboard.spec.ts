import { test, expect } from "@playwright/test";

test("dashboard runs snippet scan and shows score", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page.getByTestId("scan-dashboard")).toBeVisible();
  await page.getByTestId("run-scan").click();
  await expect(page.getByTestId("scan-result")).toBeVisible({ timeout: 60_000 });
  await expect(page.getByRole("img", { name: /Security score/i })).toBeVisible();
});

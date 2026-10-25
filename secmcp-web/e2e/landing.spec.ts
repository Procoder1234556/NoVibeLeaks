import { test, expect } from "@playwright/test";

test("landing page markets SecMCP and links to dashboard", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Security MCP for vibe-coded apps/i }),
  ).toBeVisible();
  await expect(page.getByRole("link", { name: /Open dashboard/i })).toBeVisible();
});

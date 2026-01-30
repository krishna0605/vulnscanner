import { test, expect } from '@playwright/test';

test('homepage has title and main content', async ({ page }) => {
  await page.goto('/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/VulnScanner|Vulnerability/i);

  // Check if main heading exists (adjust selector based on actual UI)
  // Assuming there's an H1 or some main element.
  // If we don't know exact content yet, checking for the body visibility is a safe basic smoke test.
  await expect(page.locator('body')).toBeVisible();
});

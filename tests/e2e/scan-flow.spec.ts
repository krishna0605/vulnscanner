import { expect, test } from '@playwright/test';

test.describe('Critical path shell', () => {
  test('homepage loads', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/VulnScanner|Vulnerability/i);
    await expect(page.locator('body')).toBeVisible();
  });

  test('Clerk sign-in shell loads', async ({ page }) => {
    await page.goto('/sign-in');
    await expect(page.getByText(/secured by clerk|sign in/i).first()).toBeVisible({
      timeout: 15000,
    });
  });

  test('Clerk sign-up shell loads', async ({ page }) => {
    await page.goto('/sign-up');
    await expect(page.getByText(/create your account|secured by clerk/i).first()).toBeVisible({
      timeout: 15000,
    });
  });

  test.skip('full scan flow requires a seeded Clerk user and CAPTCHA-safe test mode', async () => {
    // Covered manually until a Clerk test session strategy is added.
  });
});

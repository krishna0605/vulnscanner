import { expect, test } from '@playwright/test';

test.describe('Clerk authentication routes', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
  });

  test('legacy login route redirects to Clerk sign-in', async ({ page }) => {
    await page.goto('/login');
    await expect(page).toHaveURL(/sign-in/);
    await expect(page.locator('body')).toBeVisible();
  });

  test('legacy signup route redirects to Clerk sign-up', async ({ page }) => {
    await page.goto('/signup');
    await expect(page).toHaveURL(/sign-up/);
    await expect(page.locator('body')).toBeVisible();
  });

  test('Clerk sign-in page renders', async ({ page }) => {
    await page.goto('/sign-in');
    await expect(page.locator('body')).toBeVisible();
    await expect(page.getByText(/secured by clerk|sign in/i).first()).toBeVisible({
      timeout: 15000,
    });
  });

  test('Clerk sign-up page renders', async ({ page }) => {
    await page.goto('/sign-up');
    await expect(page.locator('body')).toBeVisible();
    await expect(page.getByText(/create your account|secured by clerk/i).first()).toBeVisible({
      timeout: 15000,
    });
  });
});

import { test, expect } from '@playwright/test';

test.describe('Critical Path: Scan Flow', () => {
  test('Login Page loads correctly', async ({ page }) => {
    await page.goto('/login');

    // Check for essential form elements
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /log in/i })).toBeVisible();

    // Check links
    await expect(page.getByRole('link', { name: /create account/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /forgot password/i })).toBeVisible();
  });

  test('Signup Page loads correctly', async ({ page }) => {
    await page.goto('/signup');

    // Check for essential form elements
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
    // Confirm password might be present
    // await expect(page.getByLabel(/confirm/i)).toBeVisible();

    await expect(page.getByRole('button', { name: /sign up|create account/i })).toBeVisible();
  });

  // TODO: Enable this test when a valid test user is seeded in the database
  /*
  test('Full Scan Flow (requires seeded user)', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password/i).fill('password123');
    await page.getByRole('button', { name: /log in/i }).click();

    // Verify redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Create Project
    await page.getByRole('link', { name: /projects/i }).click();
    await page.getByRole('button', { name: /new project/i }).click();
    await page.getByLabel(/name/i).fill('E2E Test Project');
    await page.getByRole('button', { name: /create/i }).click();
    
    // Verify Project Created
    await expect(page.getByText('E2E Test Project')).toBeVisible();
  });
  */
});

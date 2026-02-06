import { test, expect } from '@playwright/test';

/**
 * Authentication E2E Tests
 * Tests for login, logout, and auth state management
 */
test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing cookies/storage before each test
    await page.context().clearCookies();
  });

  test.describe('Login Page', () => {
    test('displays login form correctly', async ({ page }) => {
      await page.goto('/login');

      // Check form elements are present
      await expect(page.getByLabel(/email/i)).toBeVisible();
      await expect(page.getByLabel(/password/i)).toBeVisible();
      await expect(page.getByRole('button', { name: /log in/i })).toBeVisible();

      // Check navigation links
      await expect(page.getByRole('link', { name: /create account|sign up/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /forgot password/i })).toBeVisible();
    });

    test('shows validation errors for empty form', async ({ page }) => {
      await page.goto('/login');

      // Click login without filling form
      await page.getByRole('button', { name: /log in/i }).click();

      // Should show validation errors or remain on page
      await expect(page).toHaveURL(/login/);
    });

    test('shows error for invalid credentials', async ({ page }) => {
      await page.goto('/login');

      await page.getByLabel(/email/i).fill('invalid@example.com');
      await page.getByLabel(/password/i).fill('wrongpassword');
      await page.getByRole('button', { name: /log in/i }).click();

      // Should show error message
      await expect(page.getByText(/invalid|error|incorrect/i)).toBeVisible({ timeout: 10000 });
    });

    test('navigates to signup page', async ({ page }) => {
      await page.goto('/login');

      await page.getByRole('link', { name: /create account|sign up/i }).click();

      await expect(page).toHaveURL(/signup/);
    });

    test('navigates to forgot password page', async ({ page }) => {
      await page.goto('/login');

      await page.getByRole('link', { name: /forgot password/i }).click();

      await expect(page).toHaveURL(/forgot-password|reset/);
    });
  });

  test.describe('Signup Page', () => {
    test('displays signup form correctly', async ({ page }) => {
      await page.goto('/signup');

      await expect(page.getByLabel(/email/i)).toBeVisible();
      await expect(page.getByLabel(/password/i)).toBeVisible();
      await expect(page.getByRole('button', { name: /sign up|create account/i })).toBeVisible();
    });

    test('shows validation for weak password', async ({ page }) => {
      await page.goto('/signup');

      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).first().fill('weak');
      
      // Should show password requirements
      await page.getByRole('button', { name: /sign up|create account/i }).click();
      await expect(page).toHaveURL(/signup/);
    });

    test('has link back to login', async ({ page }) => {
      await page.goto('/signup');

      await expect(page.getByRole('link', { name: /log in|sign in/i })).toBeVisible();
    });
  });

  test.describe('Protected Routes', () => {
    test('redirects to login when accessing dashboard without auth', async ({ page }) => {
      await page.goto('/dashboard');

      // Should redirect to login
      await expect(page).toHaveURL(/login/);
    });

    test('redirects to login when accessing projects without auth', async ({ page }) => {
      await page.goto('/projects');

      await expect(page).toHaveURL(/login/);
    });

    test('redirects to login when accessing scans without auth', async ({ page }) => {
      await page.goto('/scans');

      await expect(page).toHaveURL(/login/);
    });
  });

  // Tests requiring authenticated user (commented until test user is seeded)
  test.describe.skip('Authenticated User', () => {
    test.beforeEach(async ({ page }) => {
      // Login with test user
      await page.goto('/login');
      await page.getByLabel(/email/i).fill(process.env.TEST_USER_EMAIL || 'test@example.com');
      await page.getByLabel(/password/i).fill(process.env.TEST_USER_PASSWORD || 'Test123!');
      await page.getByRole('button', { name: /log in/i }).click();
      
      // Wait for redirect to dashboard
      await page.waitForURL(/dashboard/, { timeout: 10000 });
    });

    test('can access dashboard after login', async ({ page }) => {
      await expect(page).toHaveURL(/dashboard/);
    });

    test('can logout', async ({ page }) => {
      // Find and click logout button/link
      await page.getByRole('button', { name: /logout|sign out/i }).click();

      // Should redirect to login
      await expect(page).toHaveURL(/login/);
    });

    test('cannot access login page when authenticated', async ({ page }) => {
      await page.goto('/login');

      // Should redirect to dashboard
      await expect(page).toHaveURL(/dashboard/);
    });
  });
});

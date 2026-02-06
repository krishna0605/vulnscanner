import { test, expect } from '@playwright/test';

/**
 * Projects E2E Tests
 * Tests for project CRUD operations
 * Note: These tests require authentication - enable when test user is seeded
 */
test.describe('Project Management', () => {
  // Skip all tests until test user is properly seeded
  test.describe.configure({ mode: 'serial' });

  test.describe.skip('Project CRUD Operations', () => {
    test.beforeEach(async ({ page }) => {
      // Login with test user
      await page.goto('/login');
      await page.getByLabel(/email/i).fill(process.env.TEST_USER_EMAIL || 'test@example.com');
      await page.getByLabel(/password/i).fill(process.env.TEST_USER_PASSWORD || 'Test123!');
      await page.getByRole('button', { name: /log in/i }).click();
      await page.waitForURL(/dashboard/, { timeout: 10000 });

      // Navigate to projects page
      await page.getByRole('link', { name: /projects/i }).click();
      await expect(page).toHaveURL(/projects/);
    });

    test('displays projects list page', async ({ page }) => {
      // Check for projects heading or empty state
      const hasProjects = await page.getByRole('heading', { name: /projects/i }).isVisible();
      expect(hasProjects).toBe(true);
    });

    test('opens create project dialog', async ({ page }) => {
      await page.getByRole('button', { name: /new project|create project/i }).click();

      // Check dialog is visible
      await expect(page.getByRole('dialog')).toBeVisible();
      await expect(page.getByLabel(/name/i)).toBeVisible();
    });

    test('creates a new project', async ({ page }) => {
      const projectName = `E2E Test Project ${Date.now()}`;

      // Open create dialog
      await page.getByRole('button', { name: /new project|create project/i }).click();

      // Fill in project details
      await page.getByLabel(/name/i).fill(projectName);
      await page.getByLabel(/description/i).fill('Created by E2E test');

      // Submit
      await page.getByRole('button', { name: /create|save/i }).click();

      // Verify project appears in list
      await expect(page.getByText(projectName)).toBeVisible({ timeout: 10000 });
    });

    test('opens project details', async ({ page }) => {
      // Click on first project in list
      const projectCard = page.locator('[data-testid="project-card"]').first();
      await projectCard.click();

      // Should navigate to project detail page
      await expect(page).toHaveURL(/projects\/[a-f0-9-]+/);
    });

    test('edits project details', async ({ page }) => {
      // Open first project
      await page.locator('[data-testid="project-card"]').first().click();
      await page.waitForURL(/projects\/[a-f0-9-]+/);

      // Find edit button
      await page.getByRole('button', { name: /edit|settings/i }).click();

      // Update name
      const nameInput = page.getByLabel(/name/i);
      await nameInput.clear();
      await nameInput.fill('Updated Project Name');

      // Save
      await page.getByRole('button', { name: /save|update/i }).click();

      // Verify update
      await expect(page.getByText('Updated Project Name')).toBeVisible();
    });

    test('deletes a project', async ({ page }) => {
      // Create a project to delete
      const projectName = `Delete Me ${Date.now()}`;
      await page.getByRole('button', { name: /new project|create project/i }).click();
      await page.getByLabel(/name/i).fill(projectName);
      await page.getByRole('button', { name: /create|save/i }).click();
      await expect(page.getByText(projectName)).toBeVisible();

      // Find and click delete button
      const projectRow = page.locator(`text=${projectName}`).locator('..');
      await projectRow.getByRole('button', { name: /delete/i }).click();

      // Confirm deletion
      await page.getByRole('button', { name: /confirm|yes/i }).click();

      // Verify project is removed
      await expect(page.getByText(projectName)).not.toBeVisible();
    });
  });

  // Skip in CI - requires Supabase for session verification and redirect
  test.describe.skip('Public Pages', () => {
    test('projects page redirects to login when not authenticated', async ({ page }) => {
      await page.goto('/projects');
      await expect(page).toHaveURL(/login/);
    });

    test('project detail page redirects to login when not authenticated', async ({ page }) => {
      await page.goto('/projects/some-project-id');
      await expect(page).toHaveURL(/login/);
    });
  });
});

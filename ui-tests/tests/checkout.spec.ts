
import { test, expect } from '@playwright/test';

test('user can load UI home page', async ({ page }) => {
  await page.goto('http://localhost:5006/', { waitUntil: 'networkidle' });

  // Assert that the browser title matches your UI title
  await expect(page).toHaveTitle(/Microservices Shop - UI/);
});


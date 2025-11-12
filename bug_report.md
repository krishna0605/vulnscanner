# Bug Report

This report details the bugs and problems found in the VulnScanner codebase.

## 1. Critical Bugs

### 1.1. Inconsistent Model Import in `crawler/engine.py`

*   **File:** `C:\Users\Admin\Desktop\vulscAN\backend\crawler\engine.py`
*   **Line:** 15
*   **Code Snippet:**
    ```python
    from models.unified_models import ScanSession, DiscoveredUrl, ExtractedForm, TechnologyFingerprint
    ```
*   **Description:** The file `backend/models/unified_models.py` does not exist. This will cause an `ImportError` and the application will not run.
*   **Recommendation:** Change the import to `from models.dashboard import ScanSession, DiscoveredUrl, ExtractedForm, TechnologyFingerprint` or `from models.sqlite_models import ScanSession, DiscoveredUrl, ExtractedForm, TechnologyFingerprint` depending on which models should be used.

### 1.2. Inconsistent `start_crawl_task` import in `api/routes/dashboard.py`

*   **File:** `C:\Users\Admin\Desktop\vulscAN\backend\api\routes\dashboard.py`
*   **Line:** 20
*   **Code Snippet:**
    ```python
    from tasks.crawler_tasks import start_crawl_task
    ```
*   **Description:** The file `backend/tasks/crawler_tasks.py` does not exist. This will cause an `ImportError` and the application will not run.
*   **Recommendation:** Create the `crawler_tasks.py` file in the `backend/tasks` directory and implement the `start_crawl_task` function.

### 1.3. Inconsistent Schema Import in `crawler/spider.py`

*   **File:** `C:\Users\Admin\Desktop\vulscAN\backend\crawler\spider.py`
*   **Line:** 15
*   **Code Snippet:**
    ```python
    from schemas.dashboard import ScanConfigurationSchema
    ```
*   **Description:** The file `schemas/dashboard.py` does not contain `ScanConfigurationSchema`. It contains `ScanConfiguration`. This will cause an `ImportError` and the application will not run.
*   **Recommendation:** Change the import to `from schemas.dashboard import ScanConfiguration`.

## 2. Major Bugs

### 2.1. Potential Race Condition in `_apply_rate_limit`

*   **File:** `C:\Users\Admin\Desktop\vulscAN\backend\crawler\engine.py`
*   **Line:** 336
*   **Description:** The `self.last_request_time` is shared between all the workers. When multiple workers enter the `async with self.rate_limiter:` block, they all read the same `self.last_request_time`. If one worker updates `self.last_request_time`, the other workers will not be aware of this change and might not sleep for the correct amount of time. This could lead to the rate limit being exceeded.
*   **Recommendation:** Use a more robust rate limiting library that is designed for asynchronous applications, or use a lock to protect the `self.last_request_time` variable.

### 2.2. Missing Celery Task Cancellation

*   **File:** `C:\Users\Admin\Desktop\vulscAN\backend\api\routes\dashboard.py`
*   **Line:** 560
*   **Description:** The `stop_scan_session` function has a `TODO` comment to cancel the Celery task when a scan is stopped. This is an important feature that is missing. If the task is not cancelled, it will continue to run in the background even after the scan is stopped, which could lead to wasted resources and unexpected behavior.
*   **Recommendation:** Implement the Celery task cancellation logic.

### 2.3. Inconsistent `getAuthHeaders` in `projectService.ts`

*   **File:** `C:\Users\Admin\Desktop\vulscAN\frontend\src\services\projectService.ts`
*   **Line:** 23
*   **Description:** This `getAuthHeaders` function is different from the one in `dashboardService.ts`. This one directly reads the token from `localStorage` or `sessionStorage`, while the other one uses the Supabase client to get the session. This could lead to inconsistencies in how the authentication token is retrieved.
*   **Recommendation:** Use a single, consistent way to retrieve the authentication token. The `getAuthHeaders` function in `dashboardService.ts` is more robust and should be used instead.

### 2.4. Missing Error Handling for `getAuthHeaders` in `dashboardService.ts`

*   **File:** `C:\Users\Admin\Desktop\vulscAN\frontend\src\services\dashboardService.ts`
*   **Line:** 70
*   **Description:** If there is an error getting the Supabase session, the function just logs the error to the console and returns the headers without the `Authorization` header. This could lead to authentication errors in the API calls.
*   **Recommendation:** Throw an error if the Supabase session cannot be retrieved.

## 3. Minor Bugs and Code Smells

### 3.1. N+1 Query Problem in `_store_forms` and `_perform_fingerprinting`

*   **File:** `C:\Users\Admin\Desktop\vulscAN\backend\crawler\engine.py`
*   **Lines:** 380 and 428
*   **Description:** Both of these functions first query the `DiscoveredUrl` table to get the URL record, and then they perform some action with it. This is a classic N+1 query problem.
*   **Recommendation:** Fetch all the necessary data in a single query to avoid the N+1 query problem.

### 3.2. Inefficient CSRF Token Detection

*   **File:** `C:\Users\Admin\Desktop\vulscAN\backend\crawler\parser.py`
*   **Line:** 215
*   **Description:** The code iterates through a list of regex patterns to find CSRF tokens. This is inefficient.
*   **Recommendation:** Use a single regex pattern that combines all the CSRF patterns.

### 3.3. Broad Exception Handling

*   **File:** `C:\Users\Admin\Desktop\vulscAN\backend\crawler\parser.py`
*   **Line:** 58
*   **Description:** The code uses a broad `except Exception` clause to catch all exceptions. This is not a good practice, as it can hide bugs and make it difficult to debug the code.
*   **Recommendation:** Catch more specific exceptions, such as `ParserError` from BeautifulSoup.

### 3.4. Hardcoded Backend URL

*   **Files:** `C:\Users\Admin\Desktop\vulscAN\frontend\src\services\dashboardService.ts`, `C:\Users\Admin\Desktop\vulscAN\frontend\src\services\projectService.ts`
*   **Description:** The `API_BASE_URL` is hardcoded. This is not a good practice, as it makes it difficult to change the backend URL for different environments.
*   **Recommendation:** The `REACT_APP_API_URL` environment variable should be set in the `.env` file for each environment.

### 3.5. Dynamic Import of Supabase

*   **File:** `C:\Users\Admin\Desktop\vulscAN\frontend\src\services\dashboardService.ts`
*   **Line:** 65
*   **Description:** The Supabase client is imported dynamically inside the `getAuthHeaders` function. This is done to avoid circular dependencies, but it can make the code harder to read and understand.
*   **Recommendation:** Consider refactoring the code to avoid the circular dependency and import Supabase at the top of the file.

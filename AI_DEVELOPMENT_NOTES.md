# AI Development Notes

This project was developed as a disciplined, phase-based implementation using GitHub Copilot Agent mode and direct verification. AI assistance was used to accelerate code generation, test creation, and debugging, but the final logic, validation, product decisions, and acceptance checks were always grounded in the real dataset and code execution.

## 1. How GitHub Copilot Agent mode was used

GitHub Copilot Agent mode was used to:

- set up the project structure and Python environment
- generate the initial FastAPI app shell
- create SQLite schema and import logic
- implement analytics functions and question intent detection
- add tests for invalid input, edge cases, and service failures
- refine the frontend dashboard and API flow
- debug issues discovered during verification

The agent was not used to invent unsupported business logic or bypass the requirement that all financial results be computed from the database.

## 2. Phase-by-phase development

The project was developed in phases, in line with the assignment requirements:

1. Dataset and assignment inspection
   - verified the original CSV and assignment files were in the parent project folder
   - confirmed the project should be built in a separate `ai-bi-assistant` directory
   - checked the dataset structure and quality issues before implementation

2. Project setup
   - created the workspace structure
   - initialized the Python virtual environment
   - installed the required runtime and test libraries

3. Database import and validation
   - created SQLite schema for `transactions`, `validation_issues`, and `import_runs`
   - implemented CSV ingestion and validation rules
   - preserved original records while tracking exclusions

4. Analytics implementation
   - built deterministic SQL calculations for revenue, product rankings, region totals, monthly trend, and month-by-month comparison
   - verified the results directly from SQLite queries

5. Gemini and AI integration
   - selected a free-tier compatible model
   - implemented safe intent extraction
   - validated AI output against an allow-listed intent set
   - kept calculations driven by database logic rather than model-generated numbers

6. FastAPI and frontend integration
   - served the frontend and API from the same app
   - connected the browser UI to `/api/ask`
   - verified the dashboard rendered and handled result data correctly

7. Full testing and verification
   - executed the project’s test suite
   - fixed genuine issues surfaced by validation
   - confirmed the app was stable and requirements were satisfied

## 3. Important prompts and development decisions

The key design decisions were driven by the requirement to keep the AI safe and the business metrics trustworthy.

Examples of meaningful decisions:

- Use Gemini for intent classification only, not for calculating revenue.
- Validate JSON output from Gemini before proceeding.
- Restrict supported intents to a known allow-list.
- Use SQLite as the source of truth for all analytics.
- Preserve invalid rows in the database while recording exclusion reasons.
- Keep the frontend simple and deterministic, with no direct SQL access.

## 4. How generated code was reviewed and tested

All generated code was reviewed against the actual requirements and then validated with automated tests and live checks.

The project includes automated tests covering:

- total revenue calculation
- product rankings
- monthly trend values
- region revenue values
- monthly comparison values
- invalid and empty questions
- returned/zero/missing-price exclusions
- basic API behavior
- Gemini failure handling

The final validation command used was:

```bash
cd "/home/user/RSG/JD and Assessment for GETs/ai-bi-assistant" && . .venv/bin/activate && pytest -q
```

This completed successfully with 24 tests passing.

## 5. Bugs discovered and corrected

A few issues surfaced during development and were corrected before final verification:

- unsupported currency formatting and inconsistent output handling
- product breakdown showing more rows than intended
- empty-question handling returning unclear validation behavior
- earlier discrepancy in a monthly revenue value that was resolved by directly checking SQLite calculations
- need to ensure the app does not rely on model-generated financial results

These were fixed by tightening validation, keeping calculations deterministic, and verifying database results directly.

## 6. Security precautions

Important security measures were applied throughout the project:

- API key was read from `rsg.txt` or environment variables, not hardcoded into source files.
- The key was not printed or exposed in logs or API responses.
- Gemini output was validated against a strict allow-list.
- Only predefined analytics intents were executed.
- No arbitrary SQL generation from user input was permitted.
- The project does not expose secret material through the public UI or runtime logs.

## 7. Limitations of AI-assisted development

AI-assisted development was helpful, but it had limits:

- it can propose plausible code that is structurally good but not fully aligned with the actual dataset rules
- it may overuse model-generated outputs if not restrained by business logic
- it may generate correct-looking but unverified analytics if not checked against real queries

Because of this, the project depended on direct verification of database results, tests, and actual API behavior.

## 8. What was manually verified

The following were manually verified or exercised: 

- the dataset shape and quality issues were inspected before implementation
- the CSV was imported into SQLite successfully
- the exact revenue values were confirmed from the database
- the free-tier Gemini model compatibility was checked before integration
- API endpoints responded successfully
- the dashboard assets loaded and the UI could send requests
- the final pytest suite passed
- the original assignment files remained unchanged

## 9. Final assessment

AI-assisted development was a practical accelerator for this project, but the final correctness came from disciplined review, data validation, test execution, and database-driven calculations. The resulting application is working, tested, and aligned with the assignment requirements.

# Data Export

Internal script for pulling paginated data from the Data Export API.

## Files

- [main.py](main.py): requests the export, polls until data is ready, paginates through `NextToken`, and writes JSON output to `data/`
- [.env.example](.env.example): template for local configuration

## Setup

1. Use `.env.example` as the template for the expected keys.
2. Create `.env` from `.env.example` if you do not already have one.
3. Set `X-CG-API-Secret=` to your API secret.
4. Set `X-CG-School=` to your school code.
5. Set `endpoint=` to one of the values listed in the Allowed Endpoints section below.

Example `.env`:

```env
X-CG-API-Secret=your_secret_here
X-CG-School=onboarding
endpoint=users
```

## Allowed Endpoints

- `events`
- `rsvp`
- `checkins`
- `event_registration_options`
- `payments`
- `members`
- `users`
- `groups`
- `tags`
- `academic_experiences`
- `work_experiences`
- `budgets`
- `budget_transactions`
- `surveys`
- `survey_submissions`
- `rooms`
- `rooms_reservations`
- `badges`
- `badges_completions`
- `feed_posts`
- `tracks`
- `checklists`
- `checklist_items`
- `stores`
- `store_products`
- `announcements`
- `announcement_recipients`

## Usage

Run:

```bash
python main.py
```

Before running, review the manual config block at the bottom of [main.py](main.py):
- `UPDATED_START`
- `UPDATED_END`
- `QUERY_ID`
- `TOKEN`

Use `UPDATED_START` and `UPDATED_END` for the export window. Leave `QUERY_ID` and `TOKEN` unset for a new export, or set them to resume an existing one.

The script will:

1. Request a `queryId` for the configured endpoint and date range.
2. Poll until the export is ready.
3. Fetch every page using `NextToken`.
4. Save the final output to:

```text
data/{school_code}-{endpoint}.json
```

If a request fails during pagination, it also saves:

```text
data/{school_code}-{endpoint}-partial.json
```

The log file is:

```text
data/{school_code}-{endpoint}.log
```

## Resume From A Known Query

If you already have a `queryId` and optional `token`, set them directly in [main.py](main.py) near the bottom:

```python
QUERY_ID = "..."
TOKEN = "..."
```

Then run the script again.

"""Test Socrata pagination (limit + offset) on a small date window."""

from data_loader import NYCParkingDataLoader, ESSENTIAL_FIELDS
import pandas as pd


def paginate_date_range(start_date, end_date, page_size=1000, max_pages=5):
    """Fetch pages using $limit + $offset and verify unique rows."""
    loader = NYCParkingDataLoader()

    # Narrow query: pick a small window to keep results manageable
    # Filter by year in API, then by exact dates in pandas
    start_year = start_date.split("-")[0]
    end_year = end_date.split("-")[0]

    if start_year == end_year:
        where_clause = f"issue_date like '%/{start_year}'"
    else:
        years = range(int(start_year), int(end_year) + 1)
        year_conditions = [f"issue_date like '%/{year}'" for year in years]
        where_clause = " OR ".join(year_conditions)

    results = []

    for page in range(max_pages):
        offset = page * page_size
        params = {
            "$limit": page_size,
            "$offset": offset,
            "$where": where_clause,
            "$order": "issue_date DESC"
        }

        if ESSENTIAL_FIELDS:
            params["$select"] = ",".join(ESSENTIAL_FIELDS)

        data = loader._make_request(params)
        if not data:
            break

        df = pd.DataFrame(data)
        df["issue_date_parsed"] = pd.to_datetime(df["issue_date"], format="%m/%d/%Y", errors="coerce")
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        df = df[(df["issue_date_parsed"] >= start_dt) & (df["issue_date_parsed"] <= end_dt)].copy()
        df = df.drop(columns=["issue_date_parsed"])

        if df.empty:
            break

        results.append(df)

    if not results:
        print("No data returned.")
        return

    combined = pd.concat(results, ignore_index=True)

    print(f"Pages fetched: {len(results)}")
    print(f"Total rows (combined): {len(combined):,}")

    # Check duplicate summons numbers across pages (if present)
    if "summons_number" in combined.columns:
        dupes = combined["summons_number"].duplicated().sum()
        print(f"Duplicate summons numbers across pages: {dupes}")

    # Show date range observed
    if "issue_date" in combined.columns:
        parsed = pd.to_datetime(combined["issue_date"], format="%m/%d/%Y", errors="coerce")
        print(f"Observed date range: {parsed.min()} to {parsed.max()}")


if __name__ == "__main__":
    # Example small window (adjust as needed)
    paginate_date_range(start_date="2016-01-01", end_date="2016-01-15", page_size=1000, max_pages=5)

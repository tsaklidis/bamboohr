from datetime import date

from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff
from helpers.helpers import iter_weekdays


def print_emps(emps):
    for emp in emps:
        print(f"    {emp.display_name} - {emp.job_title} | {emp.sector}")


if __name__ == "__main__":
    bamboo = BambooTimeOff(api_key, bamboo_domain)

    # A range that includes Easter Monday (2026-04-13), a Greek public holiday
    start = "2026-04-13"
    end = "2026-04-17"

    # 1. Fetch the raw who's-out data once for the whole range
    raw_whos_out = bamboo.get_who_is_out_employees(start, end)

    # 2. Extract holiday dates from the raw response
    holiday_dates = bamboo.extract_holiday_dates(raw_whos_out)
    print(f"Company holidays between {start} and {end}:")
    for h in sorted(holiday_dates):
        print(f"  * {h.strftime('%A, %Y-%m-%d')}")
    print()

    # 3. Iterate weekdays and show per-day breakdown
    total = bamboo.emp_qs.count_all_available_employees()
    print(f"Day-by-day breakdown ({total} employees total):")
    print("-" * 50)

    for day in iter_weekdays(start, end):
        day_label = day.strftime("%A, %Y-%m-%d")

        if day in holiday_dates:
            print(f"\n  {day_label}  =>  Holiday (all {total} out)")
        else:
            # 4. Get the employee IDs that are out on this specific day
            out_ids = bamboo.get_out_ids_for_date(raw_whos_out, day)
            avail_count = total - len(out_ids)
            print(f"\n  {day_label}  =>  {avail_count} available, {len(out_ids)} out")

            if out_ids:
                out_emps = bamboo.emp_qs.get_employees_by_ids(list(out_ids))
                print("  Out of office:")
                print_emps(out_emps)

    print()
    print("-" * 50)


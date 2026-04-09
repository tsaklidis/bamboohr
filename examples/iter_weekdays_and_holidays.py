from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff
from helpers.helpers import iter_weekdays


if __name__ == "__main__":
    bamboo = BambooTimeOff(api_key, bamboo_domain)

    # A two-week sprint that includes Easter Monday (2026-04-13)
    start = "2026-04-06"
    end = "2026-04-17"

    # Fetch the raw who's-out data once
    raw_whos_out = bamboo.get_who_is_out_employees(start, end)
    holiday_dates = bamboo.extract_holiday_dates(raw_whos_out)

    if holiday_dates:
        print("Holidays in this sprint:")
        for h in sorted(holiday_dates):
            print(f"  * {h.strftime('%A, %Y-%m-%d')}")
        print()

    # iter_weekdays yields only Mon-Fri, skipping weekends automatically
    weekdays = list(iter_weekdays(start, end))
    non_holiday_weekdays = [d for d in weekdays if d not in holiday_dates]

    print(f"Sprint range:       {start} to {end}")
    print(f"Total weekdays:     {len(weekdays)}")
    print(f"Holidays:           {len(weekdays) - len(non_holiday_weekdays)}")
    print(f"Effective work days: {len(non_holiday_weekdays)}")
    print()

    # Show which weekdays are working days vs holidays
    for day in weekdays:
        tag = " (Holiday)" if day in holiday_dates else ""
        print(f"  {day.strftime('%a, %Y-%m-%d')}{tag}")


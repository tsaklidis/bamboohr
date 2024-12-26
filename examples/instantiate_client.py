from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff

if __name__ == "__main__":
    bamboo = BambooTimeOff(api_key, bamboo_domain)
    start = "2024-12-23"
    end = "2024-12-27"
    working_dates = bamboo.get_working_days(start, end)
    company_holidays = bamboo.get_company_holidays(start, end)

    print(f"For the range between {start} and {end}")
    print("The following dates are working days:")
    for dt in working_dates:
        print(f"{dt.strftime('%Y-%m-%d')}")

    print("The following dates are company holidays:")
    for dt in company_holidays:
        print(f"{dt.strftime('%Y-%m-%d')}")



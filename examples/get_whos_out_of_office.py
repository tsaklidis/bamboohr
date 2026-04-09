from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff


def print_emps(emps):
    for emp in emps:
        print(f"  {emp.display_name} - {emp.job_title} | {emp.sector}")


if __name__ == "__main__":
    bamboo = BambooTimeOff(api_key, bamboo_domain)

    # --- Who is out today ---
    today = "2026-04-09"
    print(f"Employees out of office on {today}:")
    out_ids = bamboo.get_who_is_out_employees(today, today, only_ids=True)
    if out_ids:
        out_employees = bamboo.emp_qs.get_employees_by_ids(out_ids)
        print_emps(out_employees)
    else:
        print("  No one is out of office today.")

    print()

    # --- Who is out for a date range ---
    start = "2026-04-13"
    end = "2026-04-17"
    print(f"Employees out of office between {start} and {end}:")
    out_ids = bamboo.get_who_is_out_employees(start, end, only_ids=True)
    if out_ids:
        out_employees = bamboo.emp_qs.get_employees_by_ids(out_ids)
        print_emps(out_employees)
    else:
        print("  No one is out of office for this range.")


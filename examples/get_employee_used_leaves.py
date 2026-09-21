from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff


if __name__ == "__main__":
    bamboo = BambooTimeOff(api_key, bamboo_domain)

    employee_id = "123"  # Replace with the actual BambooHR employee ID
    start = "2026-01-01"
    end = "2026-12-31"

    print(f"Used leaves for employee {employee_id} ({start} to {end}):\n")

    # --- No permissions required ---
    # Uses /time_off/whos_out/ endpoint (works without special permissions)
    result = bamboo.get_employee_used_leaves_no_perms(employee_id, start, end)

    print(f"  Total used days: {result['total_used_days']}")
    if result["dates"]:
        print("  Dates out:")
        for d in result["dates"]:
            print(f"    {d}")
    else:
        print("  No leave days found.")

    # --- With permissions (time-off access required) ---
    # Uses /time_off/requests endpoint (provides leave type breakdown)
    # Uncomment below if your API key has time-off access permissions:
    #
    # result = bamboo.get_employee_used_leaves(employee_id, start, end)
    # print(f"\n  Total used days: {result['total_used_days']}")
    # if result["by_type"]:
    #     print("  Breakdown by type:")
    #     for leave_type, days in result["by_type"].items():
    #         print(f"    {leave_type}: {days} day(s)")

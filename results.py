from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff

if __name__ == "__main__":
    bamboo = BambooTimeOff(api_key, bamboo_domain)
    start = "2024-12-20"
    end = "2024-12-20"
    # cap = bamboo.calculate_sprint_capacity(start, end)
    cap = bamboo.get_available_employees(start, end)
    cap2 = bamboo.get_available_employees_v2(start, end, sector=("BE", ))


    print(78*"#")
    print(f"# Calculating capacity for sprint starting at: {start} ending: {end} #")
    print(78*"#")

    for emp in cap2:
        print(f"{emp.display_name} - {emp.sector}")






import csv
import json

try:
    with open("logs/latest_metrics.csv") as f:
        rows = list(csv.DictReader(f))

    last = rows[-1]
    print(f"Total Ticks: {len(rows)}")
    print(f"Final Population: {last['population']}")
    print(f"Final Avg Energy: {last['avg_energy']}")

    with open("logs/latest_run.jsonl") as f:
        events = [json.loads(line) for line in f]

    hunts = sum(1 for e in events if e.get("event") == "hunt" and e.get("payload", {}).get("success"))  # noqa: E501
    attacks = sum(1 for e in events if e.get("event") == "attack" and e.get("payload", {}).get("success"))  # noqa: E501
    builds = sum(1 for e in events if e.get("event") == "build" and e.get("payload", {}).get("success") is not False)  # noqa: E501
    births = sum(1 for e in events if e.get("event") == "reproduce" and e.get("payload", {}).get("success"))  # noqa: E501
    deaths = sum(1 for e in events if e.get("event", "") == "death")
    decay_counts = sum(1 for e in events if e.get("event", "") == "structure_decay")

    print(f"Successful Hunts: {hunts}")
    print(f"Successful Attacks: {attacks}")
    print(f"Successful Builds (Nests/Walls): {builds}")
    print(f"Births: {births}")
    print(f"Deaths: {deaths}")
    print(f"Structure Decays: {decay_counts}")

except Exception as e:
    print(e)

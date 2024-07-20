import json

import requests

write_threshold = 500_000
total_records = 0
after = ""
dids: dict[str, dict] = {}
unsaved_dids = False

PLC_URL = "https://plc.directory"


def write_to_file(data):
    global unsaved_dids
    file = "dids.json"

    with open(file, "w") as f:
        json.dump(data, f, indent=2)

    unsaved_dids = False
    print(f"Data written to {file}. Total DIDs: {len(dids)} After: {after}")


try:
    while True:
        res = requests.get(
            f"{PLC_URL}/export?limit=1000" + (f"&after={after}" if after else ""),
        )

        records: list[dict] = json.loads("[" + res.text.replace("\n", ",") + "]")

        if len(records) == 0:
            break

        for i, record in enumerate(records):
            unsaved_dids = True

            try:
                did = record["did"]
                if did in dids:
                    continue

                dids[did] = {
                    "did": did,
                    "created_at": record["createdAt"],
                }

                total_records += 1

            except Exception as e:
                print(e, record)

            if total_records % write_threshold == 0:
                write_to_file(dids)

        after = records[-1]["createdAt"]


except Exception as e:
    print(f"An error occurred: {e}")
    if unsaved_dids:
        write_to_file(dids)

finally:
    if unsaved_dids:
        write_to_file(dids)

print(
    f"Data collection complete. All DIDs ({len(dids)}) have been written to dids.json"
)

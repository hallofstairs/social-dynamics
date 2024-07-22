import csv
import json
import os
from typing import Any, Generator, Iterable

import requests
from libipld import decode_car  # type: ignore

STREAM_DIR = "./stream"
DID_PATH = "./dids.csv"
START_DATE_CUTOFF = "2022-11-16"  # Start of bsky network
END_DATE_CUTOFF = "2023-07-01"  # TODO: Extend


def fetch_repo(did: str) -> Generator[dict[str, Any], None, None]:
    res = requests.get(
        f"https://bsky.network/xrpc/com.atproto.sync.getRepo?did={did}",
    )

    repo: tuple[dict, dict] = decode_car(res.content)
    blocks: dict[str, dict[str, Any]] = dict(
        sorted(repo[1].items(), key=lambda x: x[1].get("createdAt", "zzzzzzzzzzzz"))
    )

    for _, record in blocks.items():
        if "createdAt" in record:
            yield {
                "did": did,
                "$type": record["$type"],
                "createdAt": record["createdAt"],
                **record,
            }
        else:
            break


def append_record(record: dict[str, Any], bucket_path: str):
    with open(bucket_path, "a") as f:
        json.dump(record, f)
        f.write("\n")


def distribute_records(records: Iterable[dict[str, Any]], log: bool = True) -> None:
    total_records = 0

    try:
        for record in records:
            file_idx = record["createdAt"][:10]  # YYYY-MM-DD
            if file_idx > END_DATE_CUTOFF:
                break

            if file_idx < START_DATE_CUTOFF:
                continue

            file_path = f"{STREAM_DIR}/{file_idx}.jsonl"
            append_record(record, file_path)

            total_records += 1

        if log:
            print(f"Added {total_records} records.")
    except Exception as e:
        print("ERROR: ", e)


if __name__ == "__main__":
    os.makedirs(STREAM_DIR, exist_ok=True)
    total_users = 0

    with open(DID_PATH, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            did = row["did"]
            created_at = row["created_at"]

            if created_at[:10] > END_DATE_CUTOFF:
                break

            print("PROCESSING: ", did)
            profile_create_record = {
                "did": did,
                "$type": "app.bsky.actor.profile",
                "createdAt": created_at,
            }
            distribute_records([profile_create_record], False)

            records = fetch_repo(did)
            distribute_records(records)

            total_users += 1

    print(f"Finished crawl to {END_DATE_CUTOFF}. Total users: {total_users}")

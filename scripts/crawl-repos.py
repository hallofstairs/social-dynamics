import csv
import fcntl
import json
import os
from typing import Any, Generator, Iterable

import requests
from libipld import decode_car  # type: ignore

NUM_FILES = 20
STREAM_DIR = "./stream"
DATE_CUTOFF = "2022-11-17"  # TODO: Extend


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
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            json.dump(record, f)
            f.write("\n")
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def distribute_records(records: Iterable[dict[str, Any]], log: bool = True) -> None:
    total_records = 0

    try:
        for record in records:
            file_idx = record["createdAt"][:10]  # YYYY-MM-DD
            if file_idx > DATE_CUTOFF:
                break

            file_path = f"{STREAM_DIR}/{file_idx}.jsonl"
            append_record(record, file_path)

            total_records += 1

        if log:
            print(f"Added {total_records} records.")
    except Exception as e:
        print("ERROR: ", e)


def read_csv(path: str):
    with open(path, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


if __name__ == "__main__":
    os.makedirs(STREAM_DIR, exist_ok=True)
    did_list = read_csv("./dids-2024-02-06.csv")
    # did_list = [
    #     {
    #         "did": "did:plc:p7flpn65bzf3kzjrp2xftshq",
    #         "created_at": "2023-04-07T20:36:34.100Z",
    #     }
    # ]

    for did_info in did_list:
        did = did_info["did"]
        created_at = did_info["created_at"]

        if created_at[:10] > DATE_CUTOFF:
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

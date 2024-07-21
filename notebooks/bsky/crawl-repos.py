# %%

import json
from typing import Optional

import libipld
import requests

# %%


class s32:
    S32_CHAR = "234567abcdefghijklmnopqrstuvwxyz"

    @classmethod
    def encode(cls, i: int) -> str:
        s = ""
        while i:
            c = i % 32
            i = i // 32  # Integer division in Python
            s = s32.S32_CHAR[c] + s
        return s

    @classmethod
    def decode(cls, s: str) -> int:
        i = 0
        for c in s:
            i = i * 32 + s32.S32_CHAR.index(c)
        return i


def parse_rev(rev: str) -> tuple[int, int]:
    timestamp = s32.decode(rev[:-2])  # unix, microseconds
    clock_id = s32.decode(rev[-2:])

    return timestamp, clock_id


def parse_post(d: dict):
    clean_record = {
        "text": d["text"],
        "langs": d.get("langs", []),
        "created_at": d["createdAt"],
        "root_uri": None,
        "parent_uri": None,
        "subject_uri": None,
        "link_card_url": None,
        "link_card_thumb": None,
        "link_card_title": None,
        "link_card_desc": None,
        "image_0_link": None,
        "image_0_alt": None,
        "image_1_link": None,
        "image_1_alt": None,
        "image_2_link": None,
        "image_2_alt": None,
        "image_3_link": None,
        "image_3_alt": None,
    }

    if "reply" in d:
        clean_record["root_uri"] = d["reply"]["root"]["uri"]
        clean_record["parent_uri"] = d["reply"]["parent"]["uri"]

    if "embed" in d:
        embed = d["embed"]

        match embed["$type"]:
            case "app.bsky.embed.recordWithMedia":
                clean_record["subject_uri"] = embed["record"]["record"]["uri"]
                match embed["media"]["$type"]:
                    case "app.bsky.embed.external":
                        clean_record["link_card_url"] = embed["media"]["external"][
                            "uri"
                        ]
                        clean_record["link_card_title"] = embed["media"]["external"][
                            "title"
                        ]
                        clean_record["link_card_desc"] = embed["media"]["external"][
                            "description"
                        ]

                        if (
                            "thumb" in embed["media"]["external"]
                            and "ref" in embed["media"]["external"]["thumb"]
                        ):
                            clean_record["link_card_thumb"] = embed["media"][
                                "external"
                            ]["thumb"]["ref"]["$link"]

                    case "app.bsky.embed.images":
                        for i, image in enumerate(embed["media"]["images"]):
                            if "ref" in image["image"]:
                                clean_record[f"image_{i}_link"] = image["image"]["ref"][
                                    "$link"
                                ]
                            if "alt" in image:
                                clean_record[f"image_{i}_alt"] = image["alt"]
                    case __:
                        print("MISSING TYPE: ", __)

            case "app.bsky.embed.images":
                for i, image in enumerate(embed["images"]):
                    if "ref" in image["image"]:
                        clean_record[f"image_{i}_link"] = image["image"]["ref"]["$link"]
                    if "alt" in image:
                        clean_record[f"image_{i}_alt"] = image["alt"]

            case "app.bsky.embed.record":
                clean_record["subject_uri"] = embed["record"]["uri"]
            case "app.bsky.embed.external":
                clean_record["link_card_url"] = embed["external"]["uri"]
                clean_record["link_card_title"] = embed["external"]["title"]
                clean_record["link_card_desc"] = embed["external"]["description"]

                if "thumb" in embed["external"] and "ref" in embed["external"]["thumb"]:
                    clean_record["link_card_thumb"] = embed["external"]["thumb"]["ref"][
                        "$link"
                    ]
            case ____:
                print("MISSING TYPE: ", ____)

    return clean_record


def parse_like(d: dict):
    return {
        "subject_did": d["subject"]["uri"],
        "created_at": d["createdAt"],
    }


def parse_follow(d: dict):
    return {
        "subject_did": d["subject"],
        "created_at": d["createdAt"],
    }


def parse_repost(d: dict):
    return {
        "subject_did": d["subject"]["uri"],
        "created_at": d["createdAt"],
    }


def parse_profile(d: dict):
    return {
        "display_name": d["displayName"],
        "description": d["description"],
    }


# TODO: Make deletes a separate list
def crawl_repo(did: str):
    records = {}
    raw_events = {
        "app.bsky.feed.like": [],
        "app.bsky.feed.post": [],
        "app.bsky.feed.repost": [],
        "app.bsky.graph.follow": [],
        "app.bsky.actor.profile": [],
    }

    res = requests.get(
        f"https://bsky.network/xrpc/com.atproto.sync.getRepo?did={did}",
        # headers={"user-agent": "jaz-repo-checkout-demo/0.0.1"},
    )

    repo = libipld.decode_car(res.content)  # type: ignore
    blocks = dict(
        sorted(repo[1].items(), key=lambda x: x[1].get("rev", "zzzzzzzzzzzz"))
    )

    def get_keys(cid: str) -> list[str]:
        keys = []
        data = blocks[cid]
        prev_key = ""

        if data["l"] is not None:
            keys.extend(get_keys(data["l"]))

        for record in data["e"]:
            key = prev_key[: record["p"]] + record["k"].decode("utf-8")
            prev_key = key

            if key not in records:
                records[key] = blocks[record["v"]]

            keys.append(key)

            if record["t"] is not None:
                more_keys = get_keys(record["t"])
                keys.extend(more_keys)

        return keys

    def diff_blocks(
        last_keys: list[str], curr_keys: list[str]
    ) -> Optional[tuple[bool, str]]:
        last = set(last_keys)
        curr = set(curr_keys)

        create = curr - last
        if create:
            return True, create.pop()

        delete = last - curr
        if delete:
            return False, delete.pop()

    last_keys = []
    curr_keys = []

    total_records = 0

    for _, op in blocks.items():
        if "rev" in op:  # Commit
            print(op)

            timestamp, clock_id = parse_rev(op["rev"])
            data_cid = op["data"]

            curr_keys = get_keys(data_cid)

            diff = diff_blocks(last_keys, curr_keys)

            print(diff)
            # if diff:
            #     is_create, key = diff
            #     _type, rkey = key.split("/")

            #     # print(records[key])
            #     total_records += 1

            #     event = {
            #         "did": did,
            #         "ts": timestamp,
            #         "type": _type,
            #         "rkey": rkey,
            #         "op": "create" if is_create else "delete",
            #     }

            #     match _type:
            #         case "app.bsky.feed.like":
            #             raw_events[_type].append({**event, **parse_like(records[key])})
            #         case "app.bsky.feed.post":
            #             raw_events[_type].append(
            #                 {
            #                     "uri": f"at://{did}/{_type}/{rkey}",
            #                     **event,
            #                     **parse_post(records[key]),
            #                 }
            #             )
            #         case "app.bsky.feed.repost":
            #             raw_events[_type].append(
            #                 {**event, **parse_repost(records[key])}
            #             )
            #         case "app.bsky.graph.follow":
            #             raw_events[_type].append(
            #                 {**event, **parse_follow(records[key])}
            #             )
            #         case "app.bsky.actor.profile":
            #             raw_events[_type].append(
            #                 {**event, **parse_profile(records[key])}
            #             )
            #         case _:
            #             print("Not crawling: ", _type)

            # last_keys = curr_keys

        else:
            break

    print("Total records: ", total_records)

    return raw_events


rando = "did:plc:p7flpn65bzf3kzjrp2xftshq"  # hallofstairs
records = crawl_repo(rando)

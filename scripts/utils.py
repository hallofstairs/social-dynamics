from typing import Optional


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


def get_keys(cid: str) -> list[str]:
    keys = []
    blocks = {}  # Placeholder
    records = {}  # Placeholder

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

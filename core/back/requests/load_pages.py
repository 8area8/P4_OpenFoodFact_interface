#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""Load the OpenFoodFact datas page per page."""

import requests
import json
import os
from pathlib import Path
import asyncio


DATAS_PATH = Path().resolve() / "core" / "back" / "requests" / "datas"

with open(DATAS_PATH / "categories_fr.json", encoding='utf-8') as file:
    CATEGORIES_FR = json.load(file)
with open(DATAS_PATH / "categories_en.json", encoding='utf-8') as file:
    CATEGORIES_EN = json.load(file)

USED_NAMES = []  # Avoid duplicates.
MAX_ASYNC_IO = asyncio.Semaphore(30)


def init(start, end):
    """Load the products from OpenFoodFact."""
    try:
        assert 0 < start <= end
    except Exception as error:
        raise error

    _remove_data_files()
    print("wait few minutes (~2min), we are requesting OpenFoodFact...")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_load_pages(loop, start, end + 1))
    loop.close()


def _remove_data_files():  # https: // stackoverflow.com/questions/185936
    """Remove each file from products folder."""
    folder = DATAS_PATH / "products"

    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as error:
            print(error)
    print("datas files removed.")


async def _load_pages(loop, start, end):
    """Create the datas file."""
    base_url = ("https://world.openfoodfacts.org/cgi/search.pl?"
                "action=process&tagtype_0=categories&tagtype_1=countries"
                "&tag_contains_1=france&page_size=1000&json=1")

    responses = []
    for index in range(start, end):
        url = base_url + f"&page={index}"
        async with MAX_ASYNC_IO:
            responses.append(loop.run_in_executor(None, requests.get, url))

    index = 1
    for response in await asyncio.gather(*responses):  # wait ~1.5 sec
        _filter_and_dump(response.json(), index)
        print(f"page {index}/{end - 1} done.")
        index += 1


def _filter_and_dump(resp, index):
    """Filter and dump the datas."""
    datas = _filtered_datas(resp)
    file_path = DATAS_PATH / "products" / f"products{index}.json"

    with open(file_path, "w", encoding='utf8') as file:
        json.dump(datas, file, indent=4, ensure_ascii=False)


def _filtered_datas(datas):
    """Filter the datas."""
    datas = datas["products"]
    filtered_datas = []

    for product in datas:
        categories = product.get("categories_tags", [])

        product = {
            "name": product.get('product_name', "").replace("'", " "),
            "description": product.get("generic_name", "").replace("'", " "),
            "categories": _translate_categories(categories),
            "stores": product.get("stores", "").replace("'", " "),
            "site_url": product.get("url", "").replace("'", " "),
            "score": int(product["nutriments"].get("nutrition-score-fr", 100))
        }
        if not product["categories"] or not product["name"]:
            continue
        if product["score"] == 100:
            continue
        if product["name"] in USED_NAMES:
            continue

        USED_NAMES.append(product["name"])
        filtered_datas.append(product)
    return filtered_datas


def _translate_categories(categories):
    """Translate the english categories to french."""
    french_categories = []
    for name in categories:
        name = name.replace("-", " ").replace("'", " ")
        name = name[3:].capitalize()

        if name in french_categories:
            continue

        if name in CATEGORIES_EN:
            index = CATEGORIES_EN.index(name)
            french_categories.append(CATEGORIES_FR[index])
        elif name in CATEGORIES_FR:
            french_categories.append(name)

    return french_categories


if __name__ == "__main__":
    init(1, 30)

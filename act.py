import pandas as pd
import re
import numpy as np
from InquirerPy import inquirer
from pathlib import Path
from consts import CATS, BASE_PATH, COLS, OUT_PATH, CAT_SAVE_PATH, AMZ_ORDERS_PATH
import json


def inquire(msg: str, choices: list[str]):
    return inquirer.select(
        message=msg,
        choices=choices,
    ).execute()


def get_cat(cat_store: dict[str, str], descript: str):
    if descript in cat_store:
        return cat_store[descript]
    ret = inquire(descript, CATS)
    cat_store[descript] = ret
    return ret


def load_data(dataname: Path):
    data = pd.read_csv(dataname)
    return data


def format_chase(data: pd.DataFrame):
    # for some reason all the cols are messed up on these
    data["Date"] = data["Details"]
    data = data.reset_index()
    data["Type"] = data["index"]
    data["Debit"] = data["Description"].abs()
    data["Credit"] = data["Description"].abs()
    data["Description"] = data["Posting Date"]

    data.loc[data["Type"] != "DEBIT", "Debit"] = 0
    data.loc[data["Type"] != "CREDIT", "Credit"] = 0
    return data


def format_citi_or_cap(data: pd.DataFrame):
    data.Credit = data.Credit.fillna(0)
    data.Debit = data.Debit.fillna(0)
    if "Transaction Date" in data.columns:
        data["Date"] = data["Transaction Date"]
    return data


def format_amz(data: pd.DataFrame):
    data["Date"] = data["Transaction Date"]
    data["Credit"] = data["Amount"].abs()
    data["Debit"] = data["Amount"].abs()
    data.loc[data.Amount > 0, "Debit"] = 0
    data.loc[data.Amount < 0, "Credit"] = 0
    return data


def load_amz_orders():

    amz_data = pd.read_csv(AMZ_ORDERS_PATH, thousands=",")[
        [
            "Order Date",
            "Order ID",
            "Total Owed",
            "Product Name",
        ]
    ]
    amz_data["Total Owed"] = amz_data["Total Owed"].astype(float)
    amz_data_g = amz_data.groupby("Order ID").agg(
        {"Total Owed": "sum", "Product Name": "sum", "Order Date": "last"}
    )
    amz_data_g["Date"] = pd.to_datetime(
        amz_data_g["Order Date"].apply(lambda x: x.split("T")[0])
    )
    return amz_data_g


def add_amz_infos(data: pd.DataFrame):
    # Get amz info
    amz_orders = load_amz_orders()
    amz_orders = amz_orders.loc[
        (amz_orders.Date > (data.Date.min() - pd.Timedelta(days=5)))
        & (amz_orders.Date < (data.Date.max() + pd.Timedelta(days=5)))
    ]

    # Perform a cartesian join
    data = data.reset_index()
    data["key"] = 1
    amz_orders["key"] = 1
    merged = pd.merge(data, amz_orders, on="key").drop("key", axis=1)

    # Filter based on exact Price match and date within 5 days
    merged = merged[
        (merged["Total Owed"] == merged["Debit"])
        & (np.abs((merged["Date_x"] - merged["Date_y"]).dt.days) <= 5)
    ]
    merged

    # remerge onto og index
    data = data.merge(merged[["index", "Product Name"]], on="index", how="left")

    data["Description"] = data.apply(
        lambda row: (
            f"Amz - {row['Product Name']}"
            if pd.notna(row["Product Name"])
            else row["Description"]
        ),
        axis=1,
    )

    return data


def get_data(dataname: Path, cat_store: dict[str, str]):
    data = load_data(dataname)
    if "citi" in dataname.stem.lower() or "cap" in dataname.stem.lower():
        data = format_citi_or_cap(data)
    elif "chase" in dataname.stem.lower():
        data = format_chase(data)
    elif "amz" in dataname.stem.lower():
        data = format_amz(data)

    data.Date = pd.to_datetime(data.Date)

    data.Description = data.Description.apply(lambda x: re.sub(r"([*\.])", " ", x))
    data.Description = data.Description.apply(lambda x: re.sub(r"[^A-Za-z ]+", "", x))
    data.Description = data.Description.apply(lambda x: re.sub(r"(XX+)", "", x))
    data.Description = data.Description.apply(lambda x: x.title())
    data.Description = data.Description.apply(lambda x: re.sub(r"(Ny|Nj|Ca)", "", x))
    data.Description = data.Description.apply(lambda x: " ".join(x.split(" ")[:6]))

    if "amz" in dataname.stem.lower():
        data = add_amz_infos(data)

    data["Category"] = data.Description.apply(lambda x: get_cat(cat_store, x))
    data["Source"] = dataname.stem.split(".")[0].split("_")[0]

    return data[COLS]


def main():
    month = "dec"
    path = BASE_PATH / month

    cat_store = {}
    if CAT_SAVE_PATH.exists():
        with CAT_SAVE_PATH.open("r") as f:
            cat_store = json.load(f)

    all_data = []
    for dataname in path.iterdir():
        if not ".csv" in dataname.suffix.lower():
            continue
        print(dataname)
        all_data.append(get_data(dataname, cat_store))

    all_data = pd.concat(all_data)

    all_data.to_csv(OUT_PATH.format(month=month))

    with CAT_SAVE_PATH.open("w") as f:
        json.dump(cat_store, f)


main()

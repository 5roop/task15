from typing import Union, List
from pathlib import Path

import pandas as pd

directory = "/home/rupnik/parlamint"
xmlid = "10"

text_path = Path(directory) / (xmlid + "_text.txt")
meta_path = Path(directory) / (xmlid + "_meta.tsv")
mp_path = Path(directory) / Path("Croatia_MPs_final_ 20220917.xlsx")
parties_path = Path(directory) / Path("Croatia_parties_final_20220917.xlsx")


def parse_meta_file(file: Union[str, Path]) -> pd.DataFrame:
    if isinstance(file, Path):
        assert file.exists(), "The path does not exist!"
        file = str(file)
    return pd.read_csv(file, sep="\t")


def parse_text_file(file: Union[str, Path]) -> pd.DataFrame:
    if isinstance(file, Path):
        assert file.exists(), "The path does not exist!"
        file = str(file)
    with open(file, "r") as f:
        contents = f.readlines()
    IDs = [i.split()[0] for i in contents]
    texts = [" ".join(i.split()[1:]) for i in contents]

    return pd.DataFrame(data={
        "ID": IDs,
        "Text": texts
    })
mpdf = pd.read_excel(str(mp_path))
partiesdf = pd.read_excel(str(parties_path))

textdf = parse_text_file(text_path)
metadf = parse_meta_file(meta_path)

metatextdf = textdf.merge(metadf, on="ID")
metatextdf["term2"] = int(xmlid)

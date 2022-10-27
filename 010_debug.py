from pathlib import Path
from tempfile import NamedTemporaryFile
from utils import prepare_interim_files, construct_TEI
from parse import compile
from concurrent.futures import ProcessPoolExecutor

datadir = Path("/home/rupnik/parlamint/S_data/")

# Identify all (T,S) pairs:
files = list(datadir.glob("*"))
pattern = "{prefix}_T{term:02}_S{session:02}.{ending}"
p = compile(pattern)
terms_and_sessions = set((p.parse(i.name).named["term"], p.parse(i.name).named["session"]) for i in files)


def process(term, session) -> None:
    term, session = int(term), int(session)
    text_path = datadir / (f"text_T{term:02}_S{session:02}.txt")
    meta_path = datadir / (f"meta_T{term:02}_S{session:02}.tsv")
    mp_path = Path("/home/rupnik/parlamint/") / Path("Croatia_MPs_final_ 20220917.xlsx")
    parties_path = Path("/home/rupnik/parlamint/") / Path("Croatia_parties_final_20220917.xlsx")
    
    merged_file = NamedTemporaryFile()
    prepare_interim_files(
        text_path = text_path,
        meta_path = meta_path,
        mp_path = mp_path,
        parties_path= parties_path,
        out_file = merged_file.name
    )
    
    construct_TEI(
        pickled_file = merged_file.name,
        session_index=session,
        term_index=term,
        out_file = Path("/home/rupnik/parlamint/S/") / f"ParlaMint-HR_T{term:02}_S{session:02}.xml"
        )
    
    
with ProcessPoolExecutor(max_workers=20) as executor:
    futures = executor.map(process, [term for term, session in terms_and_sessions], [session for term, session in terms_and_sessions])

# for term, session in list(terms_and_sessions):
#     process(term, session)
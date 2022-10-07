from datetime import datetime 
from pathlib import Path
from typing import List, Union

import pandas as pd
from tqdm import tqdm

directory = ".."
xmlid = "5"

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


def split_sentences(s: str) -> List[str]:
    
    try:
        global pipeline
        results = pipeline.process(s)
    except:
        import classla
        try:
            pipeline = classla.Pipeline("hr", processors="tokenize")
        except FileNotFoundError:
            classla.download('hr')
            pipeline = classla.Pipeline("hr", processors="tokenize")
    finally:
        results = pipeline.process(s)
    return [i.text for i in results.sentences]


def prepare_interim_files(
    text_path: Union[str, Path],
    meta_path: Union[str, Path],
    mp_path: Union[str, Path],
    parties_path: Union[str, Path],
    out_file: Union[str, Path]
                            ) -> None:
    """Merges and preprocesses data for a single term.
    
    Saves pickled df to `out_file` location.

    Args:
        text_path (Union[str, Path]): path to text
        meta_path (Union[str, Path]): path to metadata
        mp_path (Union[str, Path]): path to MP metadata
        parties_path (Union[str, Path]): path to Parties metadata
        out_file (Union[str, Path]): output path for the result.
    """    

    mpdf = pd.read_excel(str(mp_path))
    partiesdf = pd.read_excel(str(parties_path))

    textdf = parse_text_file(text_path)
    metadf = parse_meta_file(meta_path)

    metatextdf = textdf.merge(metadf, on="ID")
    metatextdf["term2"] = int(xmlid)

    alldatamerged = metatextdf.merge(mpdf,
                                     how="left",
                                     left_on=["term2", "Codemp"],
                                     right_on=["term2", "codemp"]
                                     ).merge(partiesdf,
                                             how="left",
                                             left_on=["term2", "party"],
                                             right_on=["term2", "party"]
                                             )
    tqdm.pandas()
    alldatamerged["sentences"] = alldatamerged.Text.progress_apply(
        split_sentences)

    to_categ = ['ID', 'Title', 'From', 'To', 'House', 'Term', 'Session',
                'Meeting', 'Sitting', 'Agenda', 'Subcorpus', 'Speaker_role',
                'Speaker_type', 'Speaker_party', 'Speaker_party_name', 'Party_status',
                'Speaker_name', 'Speaker_gender', 'Speaker_birth', 'Codemp',
                'Codeparty', 'term2', 'codemp', 'order_id', 'term1_x', 'term_id',
                'type_of_list', 'fullname', 'firstname', 'lastname', 'party',
                'date_of_birth', 'year_of_birth', 'gender', 'place_of_birth',
                'field_of_study', 'education_y', 'constituency', 'bp_lat', 'bp_lon',
                'codeparty', 'term1_y', 'full_name', 'established', 'chairman',
                'ideology_LR', 'party_family', 'election_result', 'no_seats',
                'coalition', 'coalition_composition', 'ruling']
    for c in to_categ:
        alldatamerged[c] = pd.Categorical(alldatamerged[c])
    alldatamerged.to_pickle(out_file)


def construct_TEI(pickled_file: Union[str, Path], out_file: Union[str, Path], file_index: int) -> None:
    
    from xml.dom import minidom
    from xml.etree.ElementTree import XML, Element, SubElement, tostring
    merged = pd.read_pickle(pickled_file)
    
    def get_who_field(row) -> str:
        try:
            lastname = "".join(row["lastname"].split())
            firstname = "".join(row["firstname"].split())
            return f"#{lastname}{firstname}"
        except:
            try:
                lastname = row["Speaker_name"].split(",")[0]
                firstname = row["Speaker_name"].split(",")[1]
                lastname = "".join(lastname.split())
                firstname = "".join(firstname.split())
                return f"#{lastname}{firstname}"
            except:
                print("Getting errors for ", row["Speaker_name"], row["lastname"], row["firstname"])
                

    def get_ana_field(row) -> str:
        mapping = dict(
            Chairperson="#chair",
            Regular="#regular"
        )
        try:
            return mapping.get(row["Speaker_role"])
        except KeyError:
            raise KeyError("Can't find mapping for "+row["Speaker_role"])
        
    today_isostr = datetime.today().date().isoformat()
    min_isostr = min(merged.From.tolist())
    max_isostr = max(merged.To.tolist())


    stringheader = f"""
<teiHeader>
    <fileDesc>
        <titleStmt>
            <title type="main" xml:lang="hr">Hrvatski parlamentarni korpus ParlaMint-HR, Mandat {file_index} [ParlaMint SAMPLE]</title>
            <title type="main" xml:lang="en">Croatian parliamentary corpus ParlaMint-HR, Term {file_index} [ParlaMint SAMPLE]</title>
            <title type="sub" xml:lang="hr">Zapisnici sjednica Hvratskog sabora, mandat {file_index}</title>
            <title type="sub" xml:lang="en">Minutes of the National Assembly of the Republic of Croatia, Term {file_index}</title>
            <meeting n="{file_index}" corresp="#HS" ana="#parla.term #HS.9">{file_index}. mandat</meeting>
            <respStmt>
            <persName ref="https://orcid.org/0000-0001-7169-9152">Nikola Ljubešić</persName>
            <resp xml:lang="hr">Preuzimanje i čiščenje digitalnog izvora</resp>
            <resp xml:lang="en">Download and clean-up of the JSON digital source</resp>
            </respStmt>
            <respStmt>
            <persName ref="https://orcid.org/0000-0002-1560-4099">Tomaž Erjavec</persName>
            <resp xml:lang="hr">Kodiranje Parla-CLARIN TEI XML</resp>
            <resp xml:lang="en">Parla-CLARIN TEI XML corpus encoding</resp>
            </respStmt>
            <respStmt>
            <persName >Peter Rupnik</persName>
            <resp xml:lang="hr">Kodiranje Parla-CLARIN TEI XML</resp>
            <resp xml:lang="en">Parla-CLARIN TEI XML corpus encoding</resp>
            </respStmt>
            <funder>
            <orgName xml:lang="hr">Istraživačka infrastrukutra CLARIN</orgName>
            <orgName xml:lang="en">The CLARIN research infrastructure</orgName>
            </funder>
        </titleStmt>
        <editionStmt>
            <edition>0.0a</edition>
        </editionStmt>
        <extent><!--These numbers do not reflect the size of the sample!-->
            <measure unit="speeches" quantity="3941" xml:lang="hr">3.941 govora</measure>
            <measure unit="speeches" quantity="3941" xml:lang="en">3,941 speeches</measure>
            <measure unit="words" quantity="631188" xml:lang="hr">631.188 riječi</measure>
            <measure unit="words" quantity="631188" xml:lang="en">631,188 words</measure>
        </extent>
        <publicationStmt>
            <publisher>
            <orgName xml:lang="hr">Istraživačka infrastrukutra CLARIN</orgName>
            <orgName xml:lang="en">CLARIN research infrastructure</orgName>
            <ref target="https://www.clarin.eu/">www.clarin.eu</ref>
            </publisher>
            <idno subtype="handle" type="URI">http://hdl.handle.net/11356/1432</idno>
            <availability status="free">
            <licence>http://creativecommons.org/licenses/by/4.0/</licence>
            <p xml:lang="hr">Ovaj rad je dostupan pod <ref target="http://creativecommons.org/licenses/by/4.0/">međunarodnom licencom Creative Commons Imenovanje 4.0</ref>
            </p>
            <p xml:lang="en">This work is licensed under the <ref target="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</ref>
            </p>
            </availability>
            <date when="2021-06-09">2021-06-09</date>
        </publicationStmt>
        <sourceDesc>
            <bibl>
            <title type="main" xml:lang="en">Minutes of the National Assembly of the Republic of Croatia</title>
            <idno type="URI" subtype="business">https://parlametar.hr/</idno>
            <idno type="URI" subtype="parliament">http://www.sabor.hr/</idno>
            <date from="{min_isostr}" to="{max_isostr}">{min_isostr} - {max_isostr}</date>
            </bibl>
        </sourceDesc>
    </fileDesc>
    <encodingDesc>
        <projectDesc>
            <p xml:lang="hr">
            <ref target="https://www.clarin.eu/content/parlamint">ParlaMint</ref>
            </p>
            <p xml:lang="en">
            <ref target="https://www.clarin.eu/content/parlamint">ParlaMint</ref>
            </p>
        </projectDesc>
        <tagsDecl><!--These numbers do not reflect the size of the sample!-->
            <namespace name="http://www.tei-c.org/ns/1.0">
            <tagUsage gi="text" occurs="1"/>
            <tagUsage gi="body" occurs="1"/>
            <tagUsage gi="div" occurs="1"/>
            <tagUsage gi="head" occurs="1"/>
            <tagUsage gi="note" occurs="1"/>
            <tagUsage gi="u" occurs="3941"/>
            <tagUsage gi="seg" occurs="17551"/>
            <tagUsage gi="vocal" occurs="201"/>
            <tagUsage gi="desc" occurs="349"/>
            <tagUsage gi="kinesic" occurs="9"/>
            <tagUsage gi="gap" occurs="139"/>
            </namespace>
        </tagsDecl>
    </encodingDesc>
    <profileDesc>
        <settingDesc>
            <setting>
            <name type="address">Trg sv. Marka 6</name>
            <name type="city">Zagreb</name>
            <name type="country" key="HR">Croatia</name>
            <date  from="{min_isostr}" to="{max_isostr}" ana="#parla.session"> {min_isostr} - {max_isostr}</date>
            </setting>
        </settingDesc>
    </profileDesc>
    <revisionDesc xml:lang="en">
        <change when="{today_isostr}">
            <name>Peter Rupnik</name>:Compile from source</change>
    </revisionDesc>
</teiHeader>
    """

    TEI = Element('TEI')
    TEI.set("xmlns", "http://www.tei-c.org/ns/1.0")
    TEI.set("xml:lang", "hr")
    TEI.set("xml:id", f"ParlaMint-HR_T{file_index:02}")
    TEI.set("ana", "#parla.term #reference")
    TEI.append(XML(stringheader))

    text = SubElement(TEI, "text")
    body = SubElement(text, "body")
    div = SubElement(body, "div")

    current_u_n = 0
    seg_index = 0
    title = None
    word_count = 0
    for i, row in merged.iterrows():
        if row["Title"] != title:
            head = SubElement(div, "head")
            head.text = row["Title"]
            title = row["Title"]
        u = SubElement(div, "u")
        u.set("who", get_who_field(row))
        u.set("ana", get_ana_field(row))
        u.set("xml:id", row["ID"])
        u.set("n",str(current_u_n))

        for segment in row["sentences"]:
            seg = SubElement(u, "seg")
            seg.set("xml:id", f"seg{file_index:02}{seg_index:010}")
            seg.text = segment
            seg_index += 1
            word_count += len(segment.split())
        current_u_n += 1
        

    # Get right values for tag usages:
    all_tagusages = TEI.findall(".//namespace/")
    for tagUsage in all_tagusages:
        gi = tagUsage.get("gi")
        occurs = len(TEI.findall(f".//{gi}"))
        tagUsage.set("occurs", str(occurs))
        
    # Get right values for extent measures:
    extent_measures = TEI.findall(".//extent/")
    for measure in extent_measures:
        unit = measure.get("unit")
        lang = measure.get(measure.keys()[-1])
        if unit == "speeches":
            nr_speeches = len(TEI.findall(".//u"))
            measure.set("quantity", str(nr_speeches))
            if lang == "hr":
                measure.text = f"{nr_speeches:,d} govora".replace(",", ".")
            else:
                measure.text = f"{nr_speeches:,d} speeches"
        if unit == "words":
            nr_speeches = len(TEI.findall(".//u"))
            measure.set("quantity", str(word_count))
            if lang == "hr":
                measure.text = f"{word_count:,d} riječi".replace(",", ".")
            else:
                measure.text = f"{word_count:,d} words"


    string_to_write = minidom.parseString(tostring(TEI).decode("utf")).toprettyxml("\t")

    # Filter out blank lines:
    string_to_write = "\n".join(
        [i for i in string_to_write.splitlines() if i.split() != []]
    )

    with open(
        #f"ParlaMint-HR_{file_index:02}.xml",
        out_file,
        "w"
        ) as f:
        f.write(string_to_write)    
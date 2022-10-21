# task15
ParlaMint data wrangling


# Addendum 2022-09-29T13:43:34

So, the data joining is complete. The quotes in metadata is not a problem. When merging, I took into account the term as well as the name/party abbreviation.

The sentence splitting worked nicely.

Next I'll turn to generating TEI files.


For posterity: so far we have seen markers:
* `(Pljesak.)`
* `- Izvođenje himne -Lijepa naša domovino - `
* ` - Minuta šutnje - -`(sic)
* `/Pljesak./`
* `(Pljesak!)`
* `(ne razumije se)`
* `(govornik se naknadno uključio, ne čuje se)`




# Addendum 2022-09-30T10:54:31


First draft of non-main xml is done.

Issues found:
* Sometimes utterances are overlaping:
```xml
<u who="#ŠeksVladimir" ana="#regular" xml:id="ParlaMint-HR_T5.S1.u2" n="1">
    lots of text here... but then:
    <seg xml:id="seg050000000113">Izvješće Mandatno-imunitetnog povjerenstva o provedenim izborima, davanje ...</seg>
    <seg xml:id="seg050000000114">Izbor predsjednika, potpredsjednika i ....</seg>
    <seg xml:id="seg050000000115">Ima li tko od zastupnika prigovor na predloženi dnevni red?</seg>
    <seg xml:id="seg050000000116">Ako nema prigovora konstatiram da je dnevni red utvrđen.</seg>
    <seg xml:id="seg050000000117">Prelazimo sada na rad prema utvrđenom dnevnom redu.</seg>
</u>
<u who="#ŠeksVladimir" ana="#chair" xml:id="ParlaMint-HR_T5.S1.u3" n="2">
    <seg xml:id="seg050000000118">Izvješće Mandatno-imunitetnog povjerenstva ...</seg>
    <seg xml:id="seg050000000119">Izbor predsjednika, potpredsjednika i članova Odbora za Ustav,...</seg>
    <seg xml:id="seg050000000120">Ima li tko od zastupnika prigovor na predloženi dnevni red?</seg>
    <seg xml:id="seg050000000121">Ako nema prigovora konstatiram da je dnevni red utvrđen.</seg>
    <seg xml:id="seg050000000122">Prelazimo sada na rad prema utvrđenom dnevnom redu.</seg>
    <seg xml:id="seg050000000123">1. Izbor predsjednika, potpredsjednika i članova...</seg>
    <seg xml:id="seg050000000124">Članak 5. Poslovnika utvrđuje da ...</seg>
```
* Sometimes sentence splitting does not work like intended (albeit in very specific situations):
```xml
<seg xml:id="seg050000000155">Slijedom iznijetog Povjerenstvo je zaključilo da danom konstituiranja Sabora prestaje mandat zastupnicima prethodnog saziva Sabora, i da su u Hrvatski sabor izabrani sljedeći zastupnici, poredani po abecednom redu: Pod 1. Jene Adam, pod 2. Đurđa Adlešić, 3. Zdenko Antešić, pod 4. Ingrid Antičević Marinović, 5. Željka Antunović, 6. Franjo Arapović, 7. Mr.</seg>
<seg xml:id="seg050000000156">Mato Arlović, 8. Zdenka Nediljka Babić Petričević, 9. Branko Bačić, 10.</seg>
<seg xml:id="seg050000000157">Stjepan Bačić, 11.</seg>
<seg xml:id="seg050000000158">Anto Bagarić, 12.</seg>
<seg xml:id="seg050000000159">Ivan Bagarić, 13.</seg>
<seg xml:id="seg050000000160">Marija Bajt, 14.</seg>
<seg xml:id="seg050000000161">Dr.</seg>
<seg xml:id="seg050000000162">Ivo Banac, 15.</seg>
<seg xml:id="seg050000000163">Milan Bandić, 16.</seg>
<seg xml:id="seg050000000164">Luka Bebić, 17.</seg>
<seg xml:id="seg050000000165">Snježana Biga-Friganović, 18.</seg>
<seg xml:id="seg050000000166">Mr.</seg>
<seg xml:id="seg050000000167">Božo Biškupić, 19.</seg>
```
* Is this top-level TEI attribute correct?
```xml
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:lang="hr" xml:id="ParlaMint-HR_T05" ana="#parla.term #reference">
```

* TEI header has to be constructed in concert with others. Too much stuff I'd have to make up and then correct.


# Addendum 2022-10-07T13:45:08

I implemented occurence counter in TEIheader. For the extent measures I chose that speeches are the same as instances in the data before sentence splitting.



# Addendum 2022-10-13T14:21:13

Re: main files. I can't seem to open the main xml file with any parser. The problem with the ones that work at least somewhat is that the attributes get prepended with `ns:0`, making it unusable. I shall have to resort to template strings.


TODO:
Fix affiliations!

# Addendum 2022-10-21T09:36:42

I'm getting errors like

```
ERROR ParlaMint-HR_T10: ERROR: Can't find local id for u/@who="#PavličekMarijan"
ERROR ParlaMint-HR_T10: ERROR: Can't find local id for u/@who="#BenčićSandra"
ERROR ParlaMint-HR_T10: ERROR: Can't find local id for u/@who="#PrimoracMarko"
```

but all those names do not appear in the metadata at all.

Is `Adam, Jene` written correctly?

`party.HSu` is super close to `party.HSU` (stranka umirovljenika). This will have to be changed.

# Meeting notes 2022-10-21T10:49:59

* Add missing parties to parties table. See wiki articles in skype chat.
* Fix references
* Run contrubuting.md validation as described on github.

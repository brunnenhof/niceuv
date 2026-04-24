#!/usr/bin/env python3
"""
Translate a Manula XML export from English to another language using the DeepL API.

Preserves:
  - Textile formatting  (h1. h3. *bold* _italic_ # list etc.)
  - Manula tokens       {TOPIC-LINK+xxx}  {IMAGE-LINK+xxx}
  - Image embeds        !{IMAGE-LINK+...}!  !(caption){IMAGE-LINK+...}!
  - URLs in links       "display text":https://...  (URL part kept verbatim)

Usage:
    uv add deepl
    uv run python translate_manula.py input.xml --api-key YOUR_KEY
    uv run python translate_manula.py input.xml --api-key YOUR_KEY --output out.xml --target-lang DE --formality more
    # or set DEEPL_API_KEY env var instead of --api-key
"""


import deepl
import os
import time
import io
import re

# Wir verwenden das Regionalmodell "earth4all":https://earth4all.life/the-science/, das von U. Goluke 
# und P.E. Stoknes entwickelt wurde. Es basiert wiederum auf dem von J. Randers 
# entwickelten "globalen Modell":https://stockholmuniversity.app.box.com/s/4all-Modell. Der Prototyp 
# des Spiels wurde mit "anvil.works":https://anvil.works/ von U Goluke und unzähligen Alpha- und Beta-Testern 
# erstellt. Die Produktionsentwicklung erfolgte mit Hilfe von "Claude Sonnet":https://claude.ai/login für die 
# Benutzeroberfläche, die Zustandsverwaltung und die VPS-Bereitstellung. Die Übertragung des 
# Modells von "Vensim":https://vensim.com/ nach Python sowie alle Grafiken wurden 
# mit "PyCharm":https://www.jetbrains.com/pycharm/ und "VSCode":https://code.visualstudio.com/ von U Goluke erstellt. 
# Das Spiel unterliegt dem Urheberrecht von U Goluke und ist unter der GNU Affero General Public License v3.0 
# lizenziert, siehe "Lizenz":{TOPIC-LINK+lizenz} und "Montag":{TOPIC-LINK+monday}

stra = 'Wir verwenden *das* Regionalmodell "earth4all":https://earth4all.life/the-science/, das von _U. Goluke_ und *_P.E. Stoknes_* entwickelt wurde. mit "anvil.works":https://anvil.works/ von U Goluke und erstellt. Die erfolgte mit Hilfe von "Claude Sonnet":https://claude.ai/login für die Benutzeroberfläche, die Zustandsverwaltung und die VPS-Bereitstellung. Die Übertragung des Modells von "Vensim":https://vensim.com/ nach Python sowie alle Grafiken wurden mit "PyCharm":https://www.jetbrains.com/pycharm/ und "VSCode":https://code.visualstudio.com/ von U Goluke erstellt. Das Spiel unterliegt dem Urheberrecht von U Goluke und ist unter der GNU Affero General Public License v3.0 lizenziert, siehe "Lizenz":{TOPIC-LINK+lizenz} und "Montag":{TOPIC-LINK+monday}'

strb = '			<title translate="yes"><![CDATA[Danke]]></title>'
strc = '			<content translate="yes"><![CDATA[Wir verwenden das Regionalmodell "earth4all":https://earth4all.life/the-science/, das von U. Goluke und P.E. Stoknes entwickelt wurde. Es basiert wiederum auf dem von J. Randers entwickelten "globalen Modell":https://stockholmuniversity.app.box.com/s/uh7fjh52pvh7yx1mqfwqcyxdcvegrodfearth4all-Modell. Der Prototyp des Spiels wurde mit "anvil.works":https://anvil.works/ von U Goluke und unzähligen Alpha- und Beta-Testern erstellt. Die Produktionsentwicklung erfolgte mit Hilfe von "Claude Sonnet":https://claude.ai/login für die Benutzeroberfläche, die Zustandsverwaltung und die VPS-Bereitstellung. Die Übertragung des Modells von "Vensim":https://vensim.com/ nach Python sowie alle Grafiken wurden mit "PyCharm":https://www.jetbrains.com/pycharm/ und "VSCode":https://code.visualstudio.com/ von U Goluke erstellt. Das Spiel unterliegt dem Urheberrecht von U Goluke und ist unter der GNU Affero General Public License v3.0 lizenziert, siehe "Lizenz":{TOPIC-LINK+lizenz}.'
strd = ''
stre = 'h4. Der größte Dank gilt unseren Alpha-Testern, den Schülern des SW101-Kurses an der Realschule Baesweiler, der im April 2024 von René Langohr unterrichtet wurde, sowie allen Beta-Testern.]]></content>'

deepl_api_key = "428b236c-2ac9-49a8-bc0e-6d1b49aaca05:fx"
translator = deepl.Translator(deepl_api_key)
translate_to = 'FR' ## the deepl.com translations are listed here
translate_from = 'DE' # 0=en 1=de_sie 2=de_du 3=fr_vous 4=no_bokmål 5=nl
source_file = 'scratch/m_01_de_fr_260403'
source_file = source_file +'.xml'
out = source_file + '_raw.xml'
out2 = source_file + '_raw_2.xml'
# Check account usage
usage = str(translator.get_usage().character)
my_usage = usage.split(" ")
usage_start = my_usage[0]

#result = str(translator.translate_text(stra, target_lang=translate_to, tag_handling='xml', tag_handling_version='v2'))
#result = re.sub(r'«\s*([^»]+?)\s*»\s*:(https?://)', r'"\1":\2', result)
#s = re.sub(r'«\s*([^»]+?)\s*»\s*:(\{[^}]+\}|https?://\S+)', r'"\1":\2', result)
#print(result)
#print(s)
#resultc = str(translator.translate_text(strc, target_lang=translate_to, tag_handling='xml', tag_handling_version='v2'))
#print(resultc)
#resultd = str(translator.translate_text(strd, target_lang=translate_to, tag_handling='xml', tag_handling_version='v2'))
#print(resultd)
#resulte = str(translator.translate_text(stre, target_lang=translate_to, tag_handling='xml', tag_handling_version='v2'))

def get_url(part: str) -> str:
    urls = re.findall(r'://[^\s,)]+', part)
    s_without_url = re.sub(r'://[^\s,)]+', '', part)
    return urls[0], s_without_url

def get_link(part: str) -> str:
    new_sp = ''
    sp = part.split(' "')
    link = sp[len(sp)-1]
    link = link.replace('":','')
    for i in range(0, len(sp)-1):
        q = sp[i].find('"')
        if q == -1:
            new_sp = new_sp + sp[i] + ' '
            pass
        else:
            sp[i] = '"' + sp[i]
            new_sp = new_sp + sp[i] + ' '
            pass 
    new_sp = new_sp.replace('  ',' ')  
    return new_sp, link

def do_https(ln: str) -> str:
    split = ln.split('"')
    split2 = ln.split('https')
    if len(split2) == 1:
        return ln
    
    new_ln = ''
    for i in range(1, len(split2)):
        tx, link = get_link(split2[i-1])
        url, not_url = get_url(split2[i])
        new_ln = new_ln + ''
    left = split[0]
    tx = split[1]
    rest = split[2]
    s3 = rest.find(' ')
    http = rest[:s3]
    remainder = rest[s3:]
    while remainder.find(':https') > 0:
        left = '§§_'+left+'_§§'
        if not tx.find('.') == -1:
            tx = '§§_"'+tx+'"_§§'
        else:
            tx = tx
        tx2 = '§§_'+tx2+'_§§'
        http = rest[:s3]
        remainder = rest[s3:]
        neue = left + tx + tlink + tx2
    return neue

def do_topic_link(ln:str) -> str:
    pass

# Create a Translator object providing your DeepL API authentication key.
# To avoid writing your key in source code, you can set it in an environment
# variable DEEPL_AUTH_KEY, then read the variable in your Python code:
#translator = deepl.Translator(os.getenv("DEEPL_AUTH_KEY"))
deepl_api_key = "428b236c-2ac9-49a8-bc0e-6d1b49aaca05:fx"
translator = deepl.Translator(deepl_api_key)
### Source and target languages
#print("Source languages:")
#for language in translator.get_source_languages():
#    print(f"{language.code} ({language.name})")  # Example: "DE (German)"

#print("Target languages:")
#for language in translator.get_target_languages():
#    if language.supports_formality:
#        print(f"{language.code} ({language.name}) supports formality")
#    else:
#        print(f"{language.code} ({language.name})")

translate_to = 'FR' ## the deepl.com translations are listed here
translate_from = 'DE' # 0=en 1=de_sie 2=de_du 3=fr_vous 4=no_bokmål 5=nl
source_file = 'scratch/m_01_de_fr_260403'
source_file = source_file +'.xml'
out = source_file + '_raw.xml'
out2 = source_file + '_raw_2.xml'
# Check account usage
usage = str(translator.get_usage().character)
my_usage = usage.split(" ")
usage_start = my_usage[0]
anfang = time.time()
with io.open(source_file,'r',encoding='utf8') as f:
    mg = f.read()
mgl = mg.split("\n")

def find_skip(var):
    for i in range(0, len(var)):
        ln = var[i]
        ix = ln.find("_skip_")
        if ix != -1:
            return i
    return -1

def find_last(var):
    for i in range(0, len(var)):
        ln = var[i]
        ix = ln.find("_last_")
        if ix != -1:
            return i
    return -1

def clean_tx(tx):
    lx = len(tx)
    p1 = tx.find('"')
    sa = tx[0:p1+1]
    s1 = tx[p1+1:lx]
    lx2 = len(s1)
    p2 = s1.find('"')
    sx = s1[0:p2]
    se = s1[p2:lx2]
    return sa,sx,se

def do_translate(var, l, which):
    global newln
    skipx = find_skip(var)
    if skipx != -1:
        for i in range(1, len(var)):
            newln.append(var[i])
        return
    lastx = find_last(var)
    if lastx == 7: # already to Dutch
        for ii in range(1, 7):
            newln.append(var[ii])
        return
    ### should this be which + 1 ?????
    tx = var[which]
    ta,tx,te = clean_tx(tx)
    result = str(translator.translate_text(tx, target_lang=translate_to))
    my = ta + result + te
    if lastx == 6:
#        newln.append(var[0])
        newln.append(var[1])
        newln.append(var[2])
        newln.append(var[3]) ## SIE to DU
        newln.append(var[4])
        newln.append(var[5])
        newln.append(my)
        newln.append(var[6])
#        newln.append(']')
    elif lastx == -1:
        newln.append(var[1])
        newln.append(var[2])
        newln.append(var[3])
        newln.append(var[4])
        newln.append(my)
        newln.append('    ' + '" _last_"')


# Wir verwenden das Regionalmodell "earth4all":https://earth4all.life/the-science/, das von U. Goluke 
# und P.E. Stoknes entwickelt wurde. Es basiert wiederum auf dem von J. Randers 
# entwickelten "globalen Modell":https://stockholmuniversity.app.box.com/s/4all-Modell. Der Prototyp 
# des Spiels wurde mit "anvil.works":https://anvil.works/ von U Goluke und unzähligen Alpha- und Beta-Testern 
# erstellt. Die Produktionsentwicklung erfolgte mit Hilfe von "Claude Sonnet":https://claude.ai/login für die 
# Benutzeroberfläche, die Zustandsverwaltung und die VPS-Bereitstellung. Die Übertragung des 
# Modells von "Vensim":https://vensim.com/ nach Python sowie alle Grafiken wurden 
# mit "PyCharm":https://www.jetbrains.com/pycharm/ und "VSCode":https://code.visualstudio.com/ von U Goluke erstellt. 
# Das Spiel unterliegt dem Urheberrecht von U Goluke und ist unter der GNU Affero General Public License v3.0 
# lizenziert, siehe "Lizenz":{TOPIC-LINK+lizenz} und "Montag":{TOPIC-LINK+monday}

def do_https(ln: str) -> str:
    split = ln.split('"')
    left = split[0]
    tx = split[1]
    rest = split[2]
    s3 = rest.find(' ')
    http = rest[:s3]
    remainder = rest[s3:]
    while remainder.find(':https') > 0:
        left = '§§_'+left+'_§§'
        if not tx.find('.') == -1:
            tx = '§§_"'+tx+'"_§§'
        else:
            tx = tx
        tx2 = '§§_'+tx2+'_§§'
        http = rest[:s3]
        remainder = rest[s3:]
        neue = left + tx + tlink + tx2
    return neue

def do_trans(s: str, https: bool) -> str:
    if s == '':
        return s
    tx = str(translator.translate_text(s, target_lang=translate_to, tag_handling='xml',
                                           tag_handling_version='v2', formality='less'))
#result = re.sub(r'«\s*([^»]+?)\s*»\s*:(https?://)', r'"\1":\2', result)
    if https:
#        tx = re.sub(r'«\s*([^»]+?)\s*»\s*:(\{[^}]+\}|https?://\S+)', r'"\1":\2', tx)
#        tx = re.sub(r'«\s*([^»]+?)\s*»\s*:(\{[^}]+\}|https?://\S+)', r'"\1":\2', tx)
        tx = re.sub(r'«\s*([^»]+?)\s*»\s*:\s*(\{[^}]+\}|https?://\S+)', r'"\1":\2', tx)

    return tx
    

newln = []
strs = []
in_content = False
i = 0
while i < len(mgl):
    ln = mgl[i]
    if len(newln) > 1:
        print(newln[-1])
    print(f'input: {ln}')
    y = ln.find('translate="yes"')
    in_c = ln.find('content translate="yes"')
    in_c_end = ln.find('></content>')
    if in_c > 0 and not in_content:
        in_content = True
    if in_c_end > 0 and in_content:
        in_content = False
    kword = ln.find('keywords translate="yes"')
    if not kword == -1:
        newln.append(ln)
        i += 1
        continue
    
    if not in_content:
        
        # needs to be translated, and checked for https / TOPIC-LINK / ]]></content>
        newln.append(ln)
        i += 1
        print(f'not in content: {newln[-1]}')
        continue

    if y > 0:
        c = ln.find('CDATA[')
        if c > 0:
            s = ln.split('CDATA[')
            first = s[0]
            s2 = s[1]
            c2 = s2.find(']]')
            if c2 > 0:
                s3 = s2.split(']]')
                tx = s3[0]
                last = s3[1]
                tx = do_trans(tx, False)
                neue = first + 'CDATA[' + tx + ']]' + last
                newln.append(neue)
                i += 1
                pass
            elif not s2.find('h3. ') == -1:
                tx = s2[4:]
                tx = do_trans(tx, False)
                neue = first + 'CDATA[h3. ' + tx
                newln.append(neue)
                i += 1
            elif not s2.find('h4. ') == -1:
                tx = s2[4:]
                tx = do_trans(tx, False)
                neue = first + 'CDATA[h4. ' + tx
                newln.append(neue)
                i += 1
                pass
            else:
                i += 1
                newln.append(ln)
                pass
        pass
    else: # not CDATA
        if ln.find('TOPIC-LINK') > 0:
            split = ln.split('"')
            left = split[0]
            tx = split[1]
            rest = split[2]
            split3 = rest.split('}')
            tlink = split3[0]
            tx2 = split3[1]
            left = do_trans(left, False)
            tx = do_trans(tx, False)
            tx2 = do_trans(tx2, False)
            neue = left + '"' + tx + '"' + tlink + '}' + tx2
            newln.append(neue)
            i += 1
            continue
        elif ln.find('h3. ') == 0:
            tx = ln[4:]
            tx = do_trans(tx, False)
            neue = 'h3. ' + tx
            newln.append(neue)
            i += 1
            continue
        elif ln.find('h4. ') == 0:
            tx = ln[4:]
            tx = do_trans(tx, False)
            neue = 'h4. ' + tx
            newln.append(neue)
            i += 1
            continue
        elif ln.find(':https') > 0:
            closing_brackets = ln.find(']]')
            if not closing_brackets == -1:
                cs = ln.split(']]')
                neue = do_trans(cs[0], True)
                neue = neue + ']]' + cs[1]
            else:
                neue = do_trans(ln, True)
            newln.append(neue)
            i += 1
            continue
        if in_content:
            top_link = ln.find('{TOPIC-LINK')
            if not top_link == -1:
                trans = do_trans(ln, True)
            else:
                trans = do_trans(ln, False)
            newln.append(trans)
        else:
            newln.append(ln)
        i += 1

with io.open(out,'w',encoding='utf8') as f:
    for i in range(0, len(strs)):
        f.write(strs[i])
        f.write("\n")
with io.open(out2,'w',encoding='utf8') as f:
    for i in range(0, len(newln)):
        f.write(newln[i])
        f.write("\n")
dauer = time.time() - anfang
print('Dauer: '+str(dauer)+' sec')
usage = str(translator.get_usage().character)
my_usage_end = usage.split(" ")
usage_end = my_usage_end[0]
chars_consumed = int(usage_end) - int(usage_start)
print('Chars consumed: '+str(chars_consumed))
left = 500000 - int(usage_end)
print('Chars left: '+str(left))

# Translate multiple texts into British English
#result = translator.translate_text(["お元気ですか？", "¿Cómo estás?"], target_lang="EN-GB")
#print(result[0].text)  # "How are you?"
#print(result[0].detected_source_lang)  # "JA"
#print(result[1].text)  # "How are you?"
#print(result[1].detected_source_lang)  # "ES"

# Translate a formal document from English to German
#translator.translate_document_from_filepath(
#    "Instruction Manual.docx",
#    "Bedienungsanleitung.docx",
#    target_lang="DE",
#    formality="more"
#)

# Glossaries allow you to customize your translations
#glossary_en_to_de = translator.create_glossary(
#    "My glossary",
#    source_lang="EN",
#    target_lang="DE",
#    entries={"artist": "Maler", "prize": "Gewinn"},
#)

#with_glossary = translator.translate_text_with_glossary(
#    "The artist was awarded a prize.", glossary_en_to_de
#)
#print(with_glossary)  # "Der Maler wurde mit einem Gewinn ausgezeichnet."

#without_glossary = translator.translate_text(
#    "The artist was awarded a prize.", target_lang="DE"
#)
#print(without_glossary)  # "Der Künstler wurde mit einem Preis ausgezeichnet."

#AR (Arabic)
#BG (Bulgarian)
#CS (Czech)
#DA (Danish)
#DE (German) supports formality
#EL (Greek)
#EN-GB (English (British))
#EN-US (English (American))
#ES (Spanish) supports formality
#ET (Estonian)
#FI (Finnish)
#FR (French) supports formality
#HU (Hungarian)
#ID (Indonesian)
#IT (Italian) supports formality
#JA (Japanese) supports formality
#KO (Korean)
#LT (Lithuanian)
#LV (Latvian)
#NB (Norwegian)
#NL (Dutch) supports formality
#PL (Polish) supports formality
#PT-BR (Portuguese (Brazilian)) supports formality
#PT-PT (Portuguese (European)) supports formality
#RO (Romanian)
#RU (Russian) supports formality
#SK (Slovak)
#SL (Slovenian)
#SV (Swedish)
#TR (Turkish)
#UK (Ukrainian)
#ZH (Chinese (simplified))
#ZH-HANS (Chinese (simplified))
#ZH-HANT (Chinese (traditional))

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import time

try:
    import deepl
except ImportError:
    print("deepl not installed. Run: uv add deepl", file=sys.stderr)
    sys.exit(1)

# Short XML tag name used as DeepL ignore tag
_NOTRANSLATE = "x"


# ── XML helpers ───────────────────────────────────────────────────────────────

def _xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _xml_unescape(s: str) -> str:
    return (s
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
            .replace("&#39;", "'"))


# ── Core: protect → translate → restore ──────────────────────────────────────

def _collect_protected_spans(text: str) -> list[tuple[int, int]]:
    """Return sorted, non-overlapping (start, end) spans that must NOT be translated."""
    spans: list[tuple[int, int]] = []

    # 1. Image embeds  !(optional-attrs){IMAGE-LINK+...}!
    for m in re.finditer(r'!(?:\([^)]*\))?\{IMAGE-LINK\+[^}]+\}!', text):
        spans.append((m.start(), m.end()))

    # 2. Standalone Manula tokens  {TOPIC-LINK+xxx}  {IMAGE-LINK+xxx}
    for m in re.finditer(r'\{(?:TOPIC-LINK|IMAGE-LINK)\+[^}]+\}', text):
        spans.append((m.start(), m.end()))

    # 3. URL part only of Textile links  "display text":https://...
    #    We protect just the URL so the display text IS translated.
    #    Exclude trailing punctuation (,.) from the URL span to avoid double punctuation.
    for m in re.finditer(r'"[^"\n]+":(https?://[^\s\n]*?)([,.)]*(?:\s|$))', text):
        spans.append((m.start(1), m.end(1)))

    # Sort and drop overlapping spans (first one wins)
    spans.sort()
    merged: list[tuple[int, int]] = []
    for s, e in spans:
        if merged and s < merged[-1][1]:
            continue  # overlaps previous span, skip
        merged.append((s, e))

    return merged


def _build_protected_xml(text: str) -> str:
    """
    Build an XML string where non-translatable spans are wrapped in <x>...</x>
    and the rest is XML-escaped.  The whole thing is wrapped in <root>.
    """
    spans = _collect_protected_spans(text)
    parts: list[str] = ["<root>"]
    last = 0
    for s, e in spans:
        parts.append(_xml_escape(text[last:s]))
        parts.append(f"<{_NOTRANSLATE}>{_xml_escape(text[s:e])}</{_NOTRANSLATE}>")
        last = e
    parts.append(_xml_escape(text[last:]))
    parts.append("</root>")
    return "".join(parts)

def _extract_from_protected_xml(xml_str: str) -> str:
    xml_str = xml_str.strip()
    xml_str = re.sub(r'^<root>(.*)</root>$', r'\1', xml_str, flags=re.DOTALL)
    xml_str = re.sub(rf'<{_NOTRANSLATE}[^>]*>(.*?)</{_NOTRANSLATE}>', r'\1', xml_str, flags=re.DOTALL)
    return _xml_unescape(xml_str)


def _fix_topic_link_display_texts(translator: deepl.Translator, text: str,
                                   target_lang: str, formality: str,
                                   glossary_id: str | None = None) -> str:
    """Post-processing: translate display texts of {TOPIC-LINK+xxx} links.

    DeepL skips anchor text in "text":{TOPIC-LINK+xxx} patterns during the main
    translation pass.  This function collects those display texts, translates them
    in one batch call, and substitutes them back.
    """
    # Match both ASCII " and typographic quotes „ " " that DeepL inserts
    _oq = r'["\u201c\u201e]'   # opening: " „ "
    _cq = r'["\u201c\u201d]'   # closing:  " " "
    pattern = rf'{_oq}([^"\u201c\u201d\u201e\n]+){_cq}:\s*(\{{(?:TOPIC-LINK|IMAGE-LINK)\+[^}}]+\}})'
    matches = list(re.finditer(pattern, text))
    if not matches:
        return text

    # Unique display texts, order-preserving
    unique_texts = list(dict.fromkeys(m.group(1) for m in matches))

    kwargs: dict = dict(source_lang="EN", target_lang=target_lang)
    if formality != "default":
        kwargs["formality"] = formality
    if glossary_id:
        kwargs["glossary"] = glossary_id
    results = translator.translate_text(unique_texts, **kwargs)
    if isinstance(results, deepl.TextResult):
        results = [results]

    mapping = {orig: res.text for orig, res in zip(unique_texts, results)}

    def replace(m: re.Match) -> str:
        return f'"{mapping.get(m.group(1), m.group(1))}":{m.group(2)}'

    return re.sub(pattern, replace, text)


def _translate_field(translator: deepl.Translator, text: str,
                     target_lang: str, formality: str,
                     glossary_id: str | None = None) -> str:
    """Translate one Textile/Manula text field via DeepL, protecting special tokens."""
    if not text or not text.strip():
        return text

    protected_xml = _build_protected_xml(text)

    kwargs: dict = dict(
        source_lang="EN",
        target_lang=target_lang,
        tag_handling="xml",
        ignore_tags=[_NOTRANSLATE],
        outline_detection=False,
        split_sentences="nonewlines",   # preserve line-break structure
    )
    if formality != "default":
        kwargs["formality"] = formality
    if glossary_id:
        kwargs["glossary"] = glossary_id

#    result = text + '_test_'
#    print(result)
#    return result
    result = translator.translate_text(protected_xml, **kwargs)
    translated = _extract_from_protected_xml(result.text)
    translated = _fix_topic_link_display_texts(translator, translated, target_lang, formality, glossary_id)
    # Restore ASCII quotes in Textile links: „text":url or "text":url → "text":url
    translated = re.sub(r'[\u201c\u201e]([^\u201c\u201d\u201e\n]+)[\u201c\u201d]:(https?://)',
                        r'"\1":\2', translated)
    # Remove space DeepL inserts between closing quote and URL: "text": https:// → "text":https://
    translated = re.sub(r'"([^"\n]+)":\s+(https?://)', r'"\1":\2', translated)
    print(translated)
    return translated


# ── XML I/O ───────────────────────────────────────────────────────────────────

def _write_with_cdata(tree: ET.ElementTree, output_path: Path) -> None:
    """Write XML, wrapping translated field content back in CDATA sections."""
    tree.write(str(output_path), encoding="unicode", xml_declaration=True)
    raw = output_path.read_text(encoding="utf-8")

    def wrap_cdata(m: re.Match) -> str:
        open_tag = m.group(1)
        content  = _xml_unescape(m.group(2))  # undo ElementTree's escaping
        close_tag = m.group(3)
        return f'{open_tag}<![CDATA[{content}]]>{close_tag}'

    raw = re.sub(
        r'(<(?:title|content|keywords) translate="yes">)(.*?)(</(?:title|content|keywords)>)',
        wrap_cdata,
        raw,
        flags=re.DOTALL,
    )
    output_path.write_text(raw, encoding="utf-8")


# ── Main routine ──────────────────────────────────────────────────────────────

def translate_manula_xml(input_path, output_path,
                         api_key: str, target_lang: str, formality: str,
                         glossary_id: str | None = None) -> None:
    input_path = Path(input_path)
    output_path = Path(output_path)
    translator = deepl.Translator(api_key)

    usage = translator.get_usage()
    print(f"DeepL usage before: {usage.character.count:,} / {usage.character.limit:,} chars")

    tree = ET.parse(input_path)
    root = tree.getroot()

    topics = root.findall(".//topic")
    print(f"Translating {len(topics)} topics → {target_lang} (formality={formality})\n")

    total_chars = 0
    for topic in topics:
        tid = topic.findtext("id", "?")
        for field_name in ("title", "content", "keywords"):
            field = topic.find(field_name)
            if field is None or field.get("translate") != "yes":
                continue
            if not field.text or not field.text.strip():
                continue

            n = len(field.text)
            total_chars += n
            print(f"  [{tid}] {field_name} ({n} chars) … ", end="", flush=True)
            field.text = _translate_field(translator, field.text, target_lang, formality, glossary_id)
            print("OK... sleep 2 sec")
            time.sleep(2)

    print(f"\nTotal chars sent: {total_chars:,}")
    _write_with_cdata(tree, output_path)
    print(f"Output written → {output_path}")


def main() -> None:
#    parser = argparse.ArgumentParser(
#        description="Translate a Manula XML export using the DeepL API"
#    )
#    parser.add_argument("input",          help="Input XML file")
#    parser.add_argument("--output",  "-o", help="Output XML file (default: <input>_<lang>.xml)")
#    parser.add_argument("--api-key", "-k", help="DeepL API key (or set DEEPL_API_KEY env var)")
#    parser.add_argument("--target-lang", "-t", default="DE",
#                        help="DeepL target language code, e.g. DE FR NB (default: DE)")
#    parser.add_argument("--formality", "-f",
#                        choices=["default", "more", "less", "prefer_more", "prefer_less"],
#                        default="default",
#                        help="Formality for languages that support it (default: default)")
#    args = parser.parse_args()
#
#    api_key = args.api_key or os.environ.get("DEEPL_API_KEY")
#    if not api_key:
#        print("Error: DeepL API key required (--api-key or DEEPL_API_KEY env var).", file=sys.stderr)
#        sys.exit(1)
#
#    input_path = Path(args.input)
#    if not input_path.exists():
#        print(f"Error: File not found: {input_path}", file=sys.stderr)
#        sys.exit(1)
#
#    lang_suffix = args.target_lang.lower().replace("-", "_")
#    output_path = Path(args.output) if args.output else \
#        input_path.with_name(f"{input_path.stem}_{lang_suffix}.xml")

#    translate_manula_xml(input_path, output_path, api_key, args.target_lang, args.formality)
    translate_manula_xml("scratch/manula_uk_de_260402.xml", "scratch/out.xml", "428b236c-2ac9-49a8-bc0e-6d1b49aaca05:fx", "DE", "less",
                         glossary_id="7dfbe50f-5f23-4d9e-93d0-51f96a8153e4")


if __name__ == "__main__":
    main()

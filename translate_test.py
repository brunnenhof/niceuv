import deepl
import os
import time
import io

# Create a Translator object providing your DeepL API authentication key.
# To avoid writing your key in source code, you can set it in an environment
# variable DEEPL_AUTH_KEY, then read the variable in your Python code:
#translator = deepl.Translator(os.getenv("DEEPL_AUTH_KEY"))
deepl_api_key = "428b236c-2ac9-49a8-bc0e-6d1b49aaca05:fx"
translator = deepl.Translator(deepl_api_key)
### Source and target languages
print("Source languages:")
for language in translator.get_source_languages():
    print(f"{language.code} ({language.name})")  # Example: "DE (German)"

print("Target languages:")
for language in translator.get_target_languages():
    if language.supports_formality:
        print(f"{language.code} ({language.name}) supports formality")
    else:
        print(f"{language.code} ({language.name})")

translate_to = 'NL' ## the deepl.com translations are listed here
translate_from = 0 # 0=en 1=de_sie 2=de_du 3=fr_vous 4=no_bokmål 5=nl
source_file = 'scratch/new 25.txt'
# Check account usage
usage = str(translator.get_usage().character)
my_usage = usage.split(" ")
usage_start = my_usage[0]
anfang = time.time()
with io.open(source_file,'r',encoding='utf8') as f:
    mg = f.read()
mgl = mg.split("\n")

import time

def translate_with_retry(text, target_lang, formal):
    retries = 5
    delay = 3
    for attempt in range(retries):
        try:
            if formal == 'more':
                return str(translator.translate_text(text, target_lang=target_lang, formality=formal))
            elif formal == 'less':
                return str(translator.translate_text(text, target_lang=target_lang, formality=formal))
            else:
                return str(translator.translate_text(text, target_lang=target_lang))

        except deepl.exceptions.TooManyRequestsException:
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))  # 2s, 4s, 6s
            else:
                raise

mgb = []
for i in range(0, len(mgl)):
    ln = mgl[i]
    if ln == ']':
        mg1 = []
        for j in range(i-6,i):
            mg1.append(mgl[j])
        mg1.append(']')
        mgb.append(mg1)
        pass
    
new_mg = []    
for i in range(0,len(mgb)):
    loc = mgb[i]
    print(loc)
    for j in range(0,len(loc)):
        ln = str(loc[j])
        ln = ln.replace("\t","    ")
        if j == 0:
            q0 = ln.find(" =")
            s = ln[:q0]
            s = s.replace(' ','_')
            s = s.replace(':','')
            s = s.replace('!','')
            s = s.replace('-','')
            s = s.replace('?','')
            s = s.replace(',','')
            s = s.replace("'","")
            s = s.encode("ascii", errors="ignore").decode("ascii")

            if s == 'continue':
                s = s+'_ug'
            if s == '-- OR --':
                s = 'or_ug'
            new_mg.append(s+' = [')
            continue
        if j == 1:
            q0 = ln.find('"')
            s = ln[q0+1:]
            q1 = s.find('"')
            org = s[:q1]
            new_mg.append('    "'+org+'",')
            continue
        if j >= 2:
            p0 = ln.find('""')
            if p0 == -1:
                new_mg.append(ln)
                continue
            else:
                if j == 2:
                    result = 'formal DE'
#                    result = str(translator.translate_text(org, target_lang='DE', formality='more'))
                    result = translate_with_retry(org, 'DE', 'more')
                elif j == 3:
                    result = 'IN-formal DE'
#                    result = str(translator.translate_text(org, target_lang='DE', formality='less'))
                    result = translate_with_retry(org, 'DE', 'less')
                elif j == 4:
                    result = 'formal FR'
#                    result = str(translator.translate_text(org, target_lang='FR', formality='more'))
                    result = translate_with_retry(org, 'FR', 'more')
                elif j == 5:
                    result = 'Norsk Bokmal'                    
#                    result = str(translator.translate_text(org, target_lang='NB'))
                    result = translate_with_retry(org, 'NB', 'None')
                    
                new_mg.append('    "'+result+'",')

with io.open('lulu2_deepl.py','w',encoding='utf8') as f:
    for i in range(0, len(new_mg)):
        f.write(new_mg[i])
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

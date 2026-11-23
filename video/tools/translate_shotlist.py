#!/usr/bin/env python3
"""Make the English humpback shot list from the Ukrainian one: same shots, English on-screen text.

Usage: python3 tools/translate_shotlist.py   (run from video/)
Reads src/humpback/shotlist.tsx, writes src/humpback-en/shotlist.tsx. Fails if any Ukrainian string is left.
"""
import re

EN = {
    " М": " M", " С": " SEC", " СМ": " CM", " Т": " T", " ХВ": " MIN", "КМ": "KM",
    "1 ГОРБИК = 1 ВОЛОСИНА": "1 BUMP = 1 HAIR", "100 КИТІВ": "100 WHALES", "11 ЧЕРВНЯ 2021": "11 JUNE 2021",
    "13 М": "13 M", "20 ХВ": "20 MIN", "30–40 С": "30–40 SEC", "38 СМ": "38 CM", "40 ТОННИ": "40 TONNES",
    "40 ТОНН": "40 TONNES", "= КИТИ ЗНИЗУ": "= WHALES BELOW", "~2 РОКИ": "~2 YEARS", "~30 С": "~30 SEC", "~45 СМ": "~45 CM",
    "«...ВЖЕ МЕРТВИЙ»": "“...ALREADY DEAD”", "«ЗОРЯ СХОДУ»": "STAR OF THE EAST", "«КИСЛОТА»": "“ACID”",
    "«НІ СЛОВА\\nПРАВДИ»": "“NOT ONE WORD\\nOF TRUTH”", "«НАЧЕ МЕНЕ ЗБИЛА\\nВАНТАЖІВКА»": "“LIKE BEING HIT\\nBY A TRUCK”",
    "«СПОКІЙНО.\\nХАПАЙСЯ ЗА ЧОВЕН»": "“STAY CALM.\\nGRAB THE BOAT”", "«Я ДУМАВ, ЩО Я...": "“I THOUGHT I WAS...",
    "«Я ЗАРАЗ ПОМРУ»": "“I'M GOING TO DIE”", "І ЗНОВУ": "AND AGAIN", "ІЛЮСТРАТИВНЕ ВІДЕО": "ILLUSTRATIVE FOOTAGE",
    "ІЛЮСТРАЦІЯ": "ILLUSTRATION", "ІСТОРИК": "HISTORIAN", "ЇЖІ НЕМАЄ": "NO FOOD", "ЇЖА": "FOOD", "ЇЖА?": "FOOD?",
    "ЇХ ЗНОВУ": "AGAIN THERE ARE", "АВСТРАЛІЯ": "AUSTRALIA", "АВСТРАЛІЯ → ПОЛІНЕЗІЯ": "AUSTRALIA → POLYNESIA",
    "АДРІАН": "ADRIÁN", "АДРІАН СІМАНКАС": "ADRIÁN SIMANCAS", "АДРІАН У ПАЩІ КИТА": "ADRIÁN IN THE WHALE'S MOUTH",
    "АКУЛА?": "A SHARK?", "АЛЯСКА": "ALASKA", "АНАЛІЗ ВІДЕО": "VIDEO ANALYSIS", "АНТАРКТИДА": "ANTARCTICA",
    "БІЛЬШЕ, НІЖ 6 СЛОНІВ": "MORE THAN 6 ELEPHANTS", "БАЛОН": "TANK", "БЕЗ ЖОДНОЇ ПОДРЯПИНИ": "NOT A SCRATCH",
    "БЕЗ ПЕРЕЛОМІВ": "NO BROKEN BONES", "БЕРИ\\nПОВЕРХНЕВИЙ БУЙ": "TAKE A\\nSURFACE BUOY", "БУЛЬБАШКИ": "BUBBLES",
    "БУЛЬБАШКОВА\\nСІТКА": "BUBBLE\\nNET", "ВІД КИТА · ПРИБЛИЗНО": "FROM A WHALE · ABOUT", "ВІДЕО · 2025": "VIDEO · 2025",
    "ВІДЕО · ADAM FISH · CC BY 3.0": "VIDEO · ADAM FISH · CC BY 3.0", "ВІДЕО · NOAA SANCTUARIES · CC BY 3.0": "VIDEO · NOAA SANCTUARIES · CC BY 3.0",
    "ВІДЕО · WALKINGKOOKA · CC BY 3.0": "VIDEO · WALKINGKOOKA · CC BY 3.0", "ВІДПЛИВАЙ\\nГЕТЬ": "PADDLE\\nAWAY",
    "ВІДПОВІДЬ №1": "ANSWER #1", "ВІН": "THE DIVER", "ВАГА": "WEIGHT", "ВИПАДКІВ": "CASES", "ВИСОКИЙ ПИСК": "HIGH SQUEALS",
    "ВРЯТУВАВСЯ": "ESCAPED", "ВХІД ДО ШЛУНКА": "WAY TO THE STOMACH", "ГЛИБИНА": "DEPTH", "ГОДИНАМИ": "FOR HOURS",
    "ГОЛОДНИЙ": "HUNGRY", "ГОРБАТИЙ КИТ": "HUMPBACK WHALE", "ГОРБИКИ НА ГОЛОВІ": "BUMPS ON THE HEAD", "ГОРЛО": "THROAT",
    "ГОРЛО КАШАЛОТА": "SPERM WHALE THROAT", "ГОРЛО КИТА": "WHALE'S THROAT", "ГОРЛО — ВУЗЬКЕ": "THE THROAT IS NARROW",
    "ГУДІННЯ": "GROANS", "ДАЛІ ЗА ВСІХ": "FURTHER THAN ALMOST ANY", "ДЕСЯТКИ ТИСЯЧ": "TENS OF THOUSANDS",
    "ДЖЕЙМС БАРТЛІ": "JAMES BARTLEY", "ДЖЕЙМС БАРТЛІ — НЕМАЄ": "JAMES BARTLEY — NOT LISTED",
    "ДЖЕЙМС БАРТЛІ\\nУ КИТІ": "JAMES BARTLEY\\nIN THE WHALE", "ДО МЕЖІ": "TO THE LIMIT", "ДОВЖИНА": "LENGTH",
    "ДОДОМУ —\\nТОГО Ж ДНЯ": "HOME —\\nTHE SAME DAY", "ДОРОСЛИЙ КИТ · 14–17 М": "ADULT WHALE · 14–17 M",
    "ДРУЖИНА КАПІТАНА": "THE CAPTAIN'S WIFE", "ЕДВАРД ДЕВІС": "EDWARD DAVIS", "ЕНЕРГІЯ": "ENERGY", "ЖЕРТВА": "VICTIM",
    "ЖЕРТВА — ГОРБАТИЙ КИТ?": "VICTIM — A HUMPBACK?", "ЖОДНОГО ВИПАДКУ": "NOT ONE CASE", "ЗА ОДИН КОВТОК": "IN ONE GULP",
    "ЗАПАС ЖИРУ": "FAT RESERVE", "ЗВУК": "SOUND", "ЗВУК НАПАДУ": "SOUND OF AN ATTACK", "ЗНАЙШЛИ\\nЖИВИМ!": "FOUND\\nALIVE!",
    "ЗНОВУ": "AGAIN", "ЗУБІВ": "TEETH", "ЗУБІВ НЕМАЄ": "NO TEETH", "ЗУБИ": "TEETH", "КІЛЬКА СЕКУНД": "A FEW SECONDS",
    "КІЛЬЦЕ БУЛЬБАШОК": "RING OF BUBBLES", "КІЛЬЦЕ → КИТИ": "RING → WHALES", "КІЛЬЦЕ\\nБУЛЬБАШОК": "RING OF\\nBUBBLES",
    "КАШАЛОТ": "SPERM WHALE", "КЕЙП-КОД": "CAPE COD", "КИДКОВЕ\\nЖИВЛЕННЯ": "LUNGE\\nFEEDING", "КИТ": "WHALE",
    "КИТ ПРОКОВТНУВ\\nМОРЯКА!": "WHALE SWALLOWS\\nA SAILOR!", "КИТОБІЙНЕ\\nСУДНО?": "A WHALING\\nSHIP?",
    "КИТОВИЙ ВУС": "BALEEN", "КМІТЛИВІ": "CLEVER", "КОМАНДА": "CREW",
    "КОМЕРЦІЙНИЙ\\nКИТОБІЙНИЙ ПРОМИСЕЛ": "COMMERCIAL\\nWHALING", "КОСТА-РИКА": "COSTA RICA", "КРИЛЬ": "KRILL",
    "ЛИСТ ДРУЖИНИ КАПІТАНА": "LETTER FROM THE CAPTAIN'S WIFE", "ЛИШИЛОСЯ МЕНШЕ 5": "FEWER THAN 5 LEFT",
    "ЛОВЕЦЬ ОМАРІВ": "LOBSTER DIVER", "ЛЮДИНА — НІ": "A PERSON — NO", "ЛЮДИНА\\nВ КИТІ": "MAN IN\\nTHE WHALE",
    "ЛЮТИЙ 2025": "FEBRUARY 2025", "МІСЬКИЙ АВТОБУС · ~12 М": "CITY BUS · ~12 M", "МІФ": "MYTH",
    "МАГЕЛЛАНОВА ПРОТОКА": "STRAIT OF MAGELLAN", "МАЙКЛ": "MICHAEL", "МАЙКЛ ПАКАРД": "MICHAEL PACKARD",
    "МАКСИМУМ": "AT MOST", "МОЖЕ, НАВІТЬ": "MAYBE EVEN", "МОРАТОРІЙ": "MORATORIUM", "МОРСЬКІ ПТАХИ": "SEABIRDS",
    "МОРЯК": "SAILOR", "НІ": "NO", "НАБАГАТО ДОВШЕ": "MUCH LONGER", "НАВІЩО?": "WHY?",
    "НАВІЩО\\nРЯТУВАТИ ТЮЛЕНЯ?": "WHY SAVE\\nA SEAL?", "НАСТУПНОГО ДНЯ": "THE NEXT DAY", "НЕ ЗМОЖЕ": "IT CAN'T",
    "НЕ НАВМИСНО": "NOT ON PURPOSE", "НЕ ПОТРІБЕН": "NOT NEEDED", "НЕ ПРОЙДЕШ": "YOU WON'T FIT", "НЕПРАВДА": "UNTRUE",
    "НОВА ВЕРСІЯ": "NEW VERSION", "ОДИН ІЗ НАЙБІЛЬШИХ": "ONE OF THE LARGEST", "ОДИН ГРУДНИЙ ПЛАВЕЦЬ": "ONE FLIPPER",
    "ОДНА З НАЙДОВШИХ\\nМІГРАЦІЙ": "ONE OF THE LONGEST\\nMIGRATIONS", "ОДНА ПІСНЯ": "ONE SONG",
    "ОЗНАКИ ГОДУВАННЯ": "SIGNS OF FEEDING", "ПІДПЛИСТИ\\nБЛИЖЧЕ?": "PADDLE\\nCLOSER?", "ПІСНЯ": "SONG", "ПАРА?": "A MATE?",
    "ПЕРЕВІРКА": "CHECKED", "ПЛАСТИН З КОЖНОГО БОКУ": "PLATES ON EACH SIDE", "ПОВІЛЬНІ": "SLOW", "ПОВІТРЯ Є": "AIR LEFT",
    "ПОЛЮВАННЯ": "HUNTING", "ПОЛЮВАННЯ ЗУПИНЕНО": "HUNTING STOPPED", "ПОНАД 100 РОКІВ ТОМУ": "MORE THAN 100 YEARS AGO",
    "ПОПЕРЕДЖЕННЯ": "THE WARNING", "ПОПУЛЯЦІЯ": "POPULATION", "ПРАВИЛА": "THE RULES", "ПРОКОВТНЕ?": "SWALLOW YOU?",
    "ПРОКОВТНУТИ\\nЛЮДИНУ": "SWALLOW\\nA PERSON", "ПРОКОВТНУТИЙ?": "SWALLOWED?", "ПРОКОВТНУТИХ ЛЮДЕЙ": "PEOPLE SWALLOWED",
    "ПТАХИ": "BIRDS", "ПТАХИ ПІРНАЮТЬ\\nВ ОДНЕ МІСЦЕ": "BIRDS DIVING\\nINTO ONE SPOT", "РІК": "YEAR", "РЕКОРД": "RECORD",
    "РИБА": "FISH", "РИБА ВИСТРИБУЄ\\nІЗ ВОДИ": "FISH JUMPING\\nOUT OF THE WATER", "РОБЕРТ ПІТМАН": "ROBERT PITMAN",
    "РОЗТЯГНУТЕ ГОРЛО": "THROAT, STRETCHED", "СВІДЧЕННЯ": "IN HIS WORDS", "СЕКУНДИ": "SECONDS", "СИЛИ": "STRENGTH",
    "СИНЦІ": "BRUISES", "СКІЛЬКИ ТИ ПРОТРИМАЄШСЯ?": "HOW LONG COULD YOU LAST?", "СКОРОТИЛАСЯ БІЛЬШ НІЖ НА": "FELL BY MORE THAN",
    "СПІВ": "SINGING", "СТОГІН": "MOANS", "СТОЛІТТЯ ПОЛЮВАННЯ": "A CENTURY OF HUNTING", "СТОП": "STOP", "СУДНО": "THE SHIP",
    "СУЧАСНИЙ\\nЙОНА": "A MODERN\\nJONAH", "ТВЕРДИЙ ПЛАСТИК": "HARD PLASTIC", "ТВОЇ ПЛЕЧІ": "YOUR SHOULDERS",
    "ТЕМНО. ТІСНО.": "DARK. TIGHT.", "ТИ": "YOU", "ТИЖНЯМИ": "FOR WEEKS", "ТОННИ ВОДИ": "TONNES OF WATER",
    "ТРИМАЙ\\nДИСТАНЦІЮ": "KEEP YOUR\\nDISTANCE", "ТРЮК": "THE TRICK", "ТЮЛЕНЬ ІНШОГО ВИДУ": "A SEAL OF ANOTHER SPECIES",
    "У ПАЩІ": "IN THE MOUTH", "У ПАЩІ КИТА": "IN THE WHALE'S MOUTH", "ФІЛЬТР": "FILTER", "ФОЛКЛЕНДИ": "FALKLANDS",
    "ФРАНЦУЗЬКА ПОЛІНЕЗІЯ": "FRENCH POLYNESIA", "ХОЛОДНІ ВОДИ · ІЛЮСТРАЦІЯ": "COLD WATERS · ILLUSTRATION",
    "ХТО ЗАВГОДНО": "ANYONE", "ХТО ХОЧЕ ЦЕ ЗАКІНЧИТИ": "WHO WANTS IT OVER", "ЦЕ ЗАНУРЕННЯ ПОКАЖЕ": "THIS DIVE WILL SHOW",
    "ЧАС ДУМАТИ": "TIME TO THINK", "ЧЕРВЕНЬ 2021": "JUNE 2021", "ЧИ МОЖЕ ВІН ТЕБЕ ПРОКОВТНУТИ?": "CAN IT SWALLOW YOU?",
    "ЧИЛІ": "CHILE", "ЧОМУ ВІН РЯТУЄ ІНШИХ?": "WHY DOES IT SAVE OTHERS?", "ШИРИНА": "WIDTH", "ШКІРА — БІЛА": "SKIN — BLEACHED",
    "ЩІЛЬНІШЕ": "TIGHTER", "ЩО БУДЕ, ЯКЩО ТЕБЕ ПРОКОВТНЕ": "WHAT HAPPENS WHEN A", "ЯК КУЛАК": "LIKE A FIST",
    "ЯК ЦЬОГО УНИКНУТИ": "HOW TO AVOID IT", "⅓ ДОВЖИНИ ТІЛА": "⅓ OF ITS BODY",
}
# The title card reads WHAT HAPPENS WHEN A / HUMPBACK WHALE / SWALLOWS YOU in English.
src = open("src/humpback/shotlist.tsx").read()
src = src.replace('mid="ЩО БУДЕ, ЯКЩО ТЕБЕ ПРОКОВТНЕ" big="ГОРБАТИЙ КИТ"', 'mid={"WHAT HAPPENS WHEN A\\nHUMPBACK WHALE"} big="SWALLOWS YOU"')
out = re.sub(r'"((?:[^"\\\n]|\\.)*)"', lambda m: '"' + EN.get(m.group(1), m.group(1)) + '"', src)
out = out.replace('from "./draw"', 'from "../humpback/draw"').replace('from "./extra"', 'from "../humpback/extra"')
out = out.replace("// One visual per shot in shots.json", "// English version, generated by tools/translate_shotlist.py from src/humpback/shotlist.tsx. Do not edit by hand.\n// One visual per shot in shots.json")
code = re.sub(r"/\*.*?\*/", "", out, flags=re.S)
code = re.sub(r"//[^\n]*", "", code)
left = sorted(set(x for x in re.findall(r'"((?:[^"\\\n]|\\.)*)"', code) if re.search("[А-ЯІЇЄҐа-яіїєґ]", x)))
if left:
    raise SystemExit("untranslated: " + repr(left))
open("src/humpback-en/shotlist.tsx", "w").write(out)
print("wrote src/humpback-en/shotlist.tsx")

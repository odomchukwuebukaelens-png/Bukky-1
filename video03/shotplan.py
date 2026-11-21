"""Video 03 shot plan: PLAN[phrase_index] = 'BUILDER:opts' - one authored shot per narration phrase (see phrases.txt)."""
PAUSES = {6: 0.6, 30: 1.0, 42: 1.0, 53: 1.0, 66: 0.8, 72: 1.0, 85: 0.6, 93: 1.0, 106: 1.0, 116: 0.8, 124: 1.0, 135: 1.0}
MAXV = {"STREET": 5, "TRUCK": 6, "MENU": 4, "BEDROOM": 5, "WINDOW_DOWN": 3, "KIDS": 5, "ARM": 4, "SATURDAY": 4, "CLOCK": 3,
        "NOTES": 3, "DAD": 3, "HOUSE": 3, "MASON": 3, "STICK": 1, "KT": 4, "YOU": 4, "COUNTDOWN": 2, "MOM_SONG": 1, "FEET": 1}
P = [
 # 0-8 cold open
 "STREET:approach,notes", "STREET:roll,notes", "TRUCK:opened", "KT:DON'T_BUY.", "WINDOW_DOWN:", "YOU:side", "BEDROOM:scared", "NOTES:", "YOU:freeze,ears",
 # 9-15 not talking about Saturday
 "SATURDAY:", "SATURDAY:", "SATURDAY:", "SATURDAY:", "SATURDAY:", "KT:THIS.", "STREET:dark,silent",
 # 16-29 summer night, the song
 "BEDROOM:sweat", "YOU:shut", "BEDROOM:", "BEDROOM:look", "CLOCK:", "CLOCK:", "YOU:wide", "NOTES:slow", "NOTES:scroll", "STREET:approach,notes",
 "NOTES:slow,missing", "NOTES:missing,scroll", "STREET:approach,notes,missing", "STREET:roll,notes",
 # 30-41 the truck arrives
 "STREET:roll,dark", "TRUCK:silent", "TRUCK:silent", "MENU:", "TRUCK:", "MENU:", "STREET:roll,lights", "STREET:roll", "STREET:stop", "TRUCK:", "STREET:stop,dark", "STREET:stop,dark",
 # 42-49 dark driver window, bell
 "TRUCK:silent", "TRUCK:silent", "YOU:scared,look", "TRUCK:bell,silent", "TRUCK:bell", "KT:DING.", "TRUCK:silent", "TRUCK:silent",
 # 50-53 the test
 "MENU:", "MENU:name", "MENU:name", "YOU:wide",
 # 54-62 seven rules
 "KT:SEVEN_RULES", "STICK:2", "ARM:", "YOU:smell", "ARM:smell,cake", "DAD:slippers", "DAD:yawn", "DAD:robe", "STREET:stop",
 # 63-87 RULE 1
 "STICK:1", "WINDOW_DOWN:", "NOTES:", "NOTES:", "TRUCK:", "STREET:stop,lights,notes", "YOU:wide", "STREET:lights", "STREET:lights,notes", "NOTES:grow",
 "BEDROOM:", "BEDROOM:", "NOTES:", "BEDROOM:freeze", "BEDROOM:freeze", "BEDROOM:freeze", "BEDROOM:lamp", "BEDROOM:lamp", "BEDROOM:lamp,off",
 "STREET:lamp", "STREET:lamp", "TRUCK:", "HOUSE:stairs", "HOUSE:stairs", "STICK:2",
 # 88-117 RULE 2
 "TRUCK:", "ARM:", "ARM:", "TRUCK:", "TRUCK:open", "TRUCK:open", "TRUCK:arm", "ARM:", "ARM:free", "YOU:scared,look", "ARM:smell,cake",
 "ARM:smell,cake", "ARM:smell,school", "ARM:smell,best", "ARM:no", "ARM:nomelt", "KIDS:", "BEDROOM:shut", "YOU:shut", "KT:EVEN_IN_JULY.",
 "ARM:", "YOU:wide", "ARM:sill", "FEET:", "CLOCK:1215", "ARM:sill,coin", "ARM:sill,coin", "ARM:sill,coin", "ARM:sill,coin", "STICK:3",
 # 118-144 RULE 3
 "STICK:3", "MENU:", "MENU:", "SATURDAY:", "MENU:dollars,rocket", "MENU:dollars", "MENU:", "MENU:rocket", "MENU:rocket", "MENU:choc", "MENU:choc",
 "MENU:name", "MENU:name", "MENU:name", "MENU:everything", "MENU:everything", "KT:NOT_MONEY.", "KT:TIME.", "MENU:paid", "MENU:paid", "MENU:paid",
 "MENU:paid", "YOU:scared", "HOUSE:door", "HOUSE:shoes", "HOUSE:shoes,gone", "DAD:robe",
 # 145-158 the plant: dad tired
 "KT:NOW_THINK.", "DAD:yawn", "DAD:yawn", "CLOCK:seven", "DAD:yawn", "DAD:yawn", "DAD:couch", "DAD:couch", "DAD:older", "DAD:older", "DAD:older",
 "HOUSE:photo", "KT:KEEP_THAT_IN_MIND.", "STICK:4",
 # 159-185 RULE 4
 "STICK:4", "KIDS:", "KIDS:count", "KIDS:", "KIDS:", "KIDS:", "WINDOW_DOWN:kids", "KIDS:", "KIDS:", "KIDS:", "KIDS:", "KIDS:", "KIDS:", "KIDS:",
 "KIDS:", "KIDS:", "KIDS:", "KIDS:count", "KIDS:count,grow", "KIDS:count,grow", "KIDS:grow", "KT:DON'T_COUNT.", "KIDS:", "KIDS:", "KIDS:", "KIDS:",
 "STREET:lamp,stop",
 # 186-208 Mason
 "MASON:file", "MASON:nine", "MASON:file", "MASON:nine", "MASON:scoop", "MENU:mint", "MASON:scoop", "MASON:calendar", "MASON:calendar", "MASON:table",
 "MASON:table", "MASON:table", "MASON:table,quiet", "MASON:table,quiet", "MASON:blank", "MASON:blank", "MASON:slows", "STREET:roll,silent",
 "MASON:slows", "TRUCK:silent", "MASON:receipt", "MASON:receipt", "STICK:5",
 # 209-234 RULE 5
 "STICK:5", "NOTES:mom", "YOU:hum", "NOTES:scroll", "NOTES:mom", "NOTES:mom", "MOM_SONG:", "MOM_SONG:", "STREET:lamp,notes", "WINDOW_DOWN:",
 "FEET:walk", "FEET:walk", "YOU:ears", "YOU:ears,hum", "YOU:hum", "YOU:hum", "BEDROOM:hum,ears", "NOTES:missing", "BEDROOM:hum", "YOU:count",
 "COUNTDOWN:", "COUNTDOWN:", "YOU:count", "COUNTDOWN:notune", "COUNTDOWN:notune", "STICK:6",
 # 235-258 RULE 6
 "STICK:6", "STICK:6", "HOUSE:shoes", "HOUSE:shoes", "HOUSE:stairs", "HOUSE:stairs", "HOUSE:stairs", "HOUSE:shoes", "HOUSE:shoes", "HOUSE:shoes,gone",
 "HOUSE:door", "HOUSE:door", "WINDOW_DOWN:dad", "KT:DON'T_FOLLOW.", "HOUSE:door,locked", "HOUSE:door,locked", "HOUSE:shoes", "HOUSE:door,locked",
 "STREET:stop", "STREET:leave", "BEDROOM:shut", "HOUSE:shoes,gone", "DAD:counter", "HOUSE:photo",
 # 259-289 the twist
 "HOUSE:photo", "HOUSE:photo", "STREET:approach,notes", "TRUCK:opened", "TRUCK:armout", "HOUSE:photo", "HOUSE:photo", "HOUSE:photo", "HOUSE:photo",
 "HOUSE:photo", "KT:SUMMER_1994", "KT:1994.", "MENU:everything", "MOM_SONG:", "MENU:name", "STREET:stop", "DAD:slippers", "DAD:slippers",
 "DAD:counter", "DAD:counter,jar", "MENU:", "MENU:", "DAD:yawn", "DAD:couch", "DAD:older", "DAD:older", "DAD:older", "SATURDAY:",
 "SATURDAY:", "STREET:leave", "STICK:7",
 # 290-323 RULE 7
 "STICK:7", "BEDROOM:", "BEDROOM:", "WINDOW_DOWN:dad", "WINDOW_DOWN:dad", "DAD:counter", "DAD:robe", "DAD:counter,jar", "DAD:robe,jar",
 "ARM:", "DAD:counter,jar", "DAD:robe,jar", "DAD:counter,jar", "KT:DON'T_WATCH.", "DAD:older", "DAD:robe,jar", "BEDROOM:shut", "YOU:shut",
 "STREET:leave,notes", "STREET:leave,silent", "HOUSE:door,close", "HOUSE:door,locked,close", "DAD:pancakes", "DAD:pancakes", "DAD:pancakes",
 "DAD:pancakes", "DAD:pancakes", "DAD:pancakes", "YOU:smile", "YOU:smile", "KT:DON'T_ASK.", "DAD:hug", "DAD:hug", "DAD:hug",
 # 324-333 ending
 "STREET:approach,notes", "STREET:roll,notes", "CLOCK:", "MENU:everything", "WINDOW_DOWN:", "HOUSE:door,close", "CLOCK:1215", "BEDROOM:shut",
 "DAD:hug", "DAD:robe,jar",
]
PLAN = dict(enumerate(P))
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "anim2d"))
from shots03 import COMPS
MAXV = {b: 3 * n for b, n in COMPS.items()}
PLAN.update({
  13: "SATURDAY:order", 62: "STICK:w1", 75: "NOTES:stop", 87: "STICK:w2", 88: "STICK:2", 108: "YOU:cone,wide", 117: "STICK:w3",
  120: "MENU:prices", 121: "SATURDAY:street", 124: "MENU:mint", 129: "MENU:prices", 131: "MENU:due", 149: "DAD:breakfast", 150: "DAD:mug",
  158: "STICK:w4", 161: "WINDOW_DOWN:kids", 162: "TRUCK:", 163: "MENU:choc", 166: "KIDS:stripes", 168: "KIDS:faces", 170: "KIDS:conecu",
  172: "KIDS:number", 173: "KIDS:faded", 174: "KT:20_YEARS", 175: "STREET:dark,silent", 181: "KIDS:arrow", 182: "KIDS:backkid", 184: "KIDS:tohouse",
  208: "STICK:w5", 216: "MOM_SONG:close", 220: "FEET:walk,door", 234: "STICK:w6", 236: "KT:SIX.", 240: "HOUSE:parents", 241: "HOUSE:tiptoe",
  242: "HOUSE:rack", 251: "HOUSE:there", 258: "JAR:", 259: "HOUSE:photo", 260: "HOUSE:photo,hot", 264: "HOUSE:photo,hall", 265: "HOUSE:photo,hall,b",
  266: "HOUSE:photo,kidcu", 267: "HOUSE:photo,conecu", 268: "HOUSE:photo,flash", 272: "HOUSE:born", 273: "MENU:due", 279: "MENU:month",
  280: "MENU:year", 281: "DAD:eyebags", 284: "DAD:dads", 286: "SATURDAY:never", 287: "SATURDAY:",
  288: "STREET:leave", 289: "STICK:w7", 299: "ARM:coins", 302: "JAR:", 304: "DAD:handover", 315: "DAD:greyhair", 316: "DAD:flip",
  237: "KT:CHECK_HIS_SHOES.", 283: "DAD:greyhair", 285: "KT:NEVER.", 317: "DAD:plate", 328: "WINDOW_DOWN:closed", 332: "DAD:dawn", 333: "SATURDAY:summer",
})
PLAN.update({
  52: "MENU:due", 67: "KT:NOT_FOR_SELLING.", 113: "ARM:sill,melt", 114: "ARM:sill,puddle", 115: "ARM:sill,coin", 116: "ARM:sill,coincu",
  126: "KT:1_YEAR.", 128: "KT:3_YEARS.", 132: "MENU:everything", 133: "KT:EVERYTHING.", 136: "YOU:look,wide", 137: "MENU:name",
  138: "MENU:paid", 139: "KT:PAID.", 152: "CLOCK:seven", 153: "DAD:calendar", 154: "DAD:older", 155: "DAD:eyebags",
  193: "MASON:calendar", 194: "KT:NEXT_SUNDAY.", 195: "MASON:table", 196: "MASON:table,quiet", 197: "MASON:eat", 198: "MASON:smile",
  199: "KT:NOT_TALKING.", 200: "MASON:blank", 201: "KT:NOTHING.", 206: "WINDOW_DOWN:", 207: "MASON:receipt", 214: "YOU:wide",
  231: "YOU:count", 233: "NOTES:stop", 246: "DAD:slippers", 250: "KT:DON'T_OPEN.", 275: "DAD:calendar", 312: "DAD:pancakes",
  313: "DAD:plate", 314: "DAD:greyhair", 315: "DAD:pancakes", 316: "DAD:flip", 317: "DAD:plate", 319: "DAD:greyhair",
  322: "YOU:smile,shut", 323: "HOUSE:photo,squint",
})
PLAN.update({65: "BEDROOM:notes", 90: "KT:FREE_SAMPLE?", 98: "ARM:smell,cake", 99: "YOU:smell", 100: "ARM:smell,school",
             101: "ARM:smell,best", 147: "DAD:eyebags", 177: "KIDS:count,grow", 178: "KIDS:arrow"})
PLAN.update({183: "KIDS:c4"})

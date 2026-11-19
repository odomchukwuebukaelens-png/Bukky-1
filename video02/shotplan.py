"""Video 02 full shot plan. PLAN[sentence] = key shots ('BUILDER:opts', or an approved opening-shot name).
build.py tops up each sentence from POOL[CTX[sentence]] so no shot exceeds 2s, never reusing a
(builder, variant, opts) combination and never putting the same builder twice in a row."""
PAUSES = {5: 0.6, 27: 1.0, 43: 1.0, 59: 1.0, 71: 1.0, 80: 0.6, 95: 1.0, 104: 1.0, 112: 0.8, 126: 1.0, 144: 1.0}
MAXV = {"YARD": 16, "DOORFRAME_VIEW": 4, "KITCHEN": 10, "BOWL": 10, "CLOCKS": 10, "HALL": 5, "YOU_CU": 20, "YOU_FULL": 5,
        "HANDS": 10, "WHISTLE": 2, "ARM_HAIR": 3, "DOG_CU": 12, "DOG_FULL": 8, "WINDOW": 10, "CURTAIN": 10, "DIAGRAM": 3,
        "EAR_CHART": 3, "WAVE": 3, "TAGS": 1, "KT": 4, "COUNT": 1, "TULSA": 4, "NEIGHBORS": 2, "WOODS": 3, "BEDROOM_DOOR": 6,
        "MEMORY": 3, "PORCH": 5, "SKY": 3, "DAWN_KITCHEN": 10}
POOL = {
  "yard": ["YARD:tuck", "DOG_FULL:tuck", "DOG_CU:head,tuck", "SKY:", "DOORFRAME_VIEW:tuck", "DOG_CU:tail,tuck", "YOU_FULL:", "PORCH:", "DOG_CU:face,tuck", "YOU_CU:scared"],
  "kitchen": ["KITCHEN:", "CLOCKS:", "BOWL:", "YOU_CU:side", "HALL:far", "WINDOW:", "CURTAIN:", "DOORFRAME_VIEW:tuck"],
  "hall": ["HALL:far", "YOU_CU:scared", "DOG_CU:eyes,face", "DOG_FULL:tuck,growl", "WINDOW:shape", "HALL:mid", "YOU_FULL:scared", "DOG_CU:face,flat"],
  "porch": ["PORCH:", "DOORFRAME_VIEW:tuck", "YOU_FULL:", "SKY:", "YARD:tuck", "DOG_FULL:tuck", "YOU_CU:"],
  "tulsa": ["TULSA:duke", "TULSA:man", "HALL:voice,far", "BOWL:duke", "TULSA:night", "SKY:", "DOG_FULL:wag", "HALL:voice,mid", "YOU_FULL:", "KITCHEN:", "WINDOW:", "DOORFRAME_VIEW:", "CLOCKS:"],
  "memory": ["MEMORY:box", "MEMORY:cry", "BEDROOM_DOOR:puppy", "MEMORY:room", "BEDROOM_DOOR:", "YOU_CU:smile", "DOG_CU:head", "MEMORY:move", "BEDROOM_DOOR:day", "DOG_FULL:wag", "KITCHEN:", "SKY:"],
  "dawn": ["WOODS:dawn", "DAWN_KITCHEN:", "YARD:nodog", "SKY:", "BEDROOM_DOOR:day", "PORCH:"],
  "ears": ["DOG_CU:ears", "DOG_FULL:", "EAR_CHART:", "DOG_CU:face", "YOU_CU:scared", "DOG_CU:head"],
}
CTX = {}
for a, b, c in ((0, 9, "yard"), (10, 17, "kitchen"), (18, 26, "yard"), (27, 42, "hall"), (43, 58, "hall"), (59, 70, "porch"),
                (71, 79, "ears"), (80, 94, "tulsa"), (95, 103, "porch"), (104, 111, "porch"), (112, 125, "memory"),
                (126, 138, "yard"), (139, 143, "dawn"), (144, 148, "porch")):
    for i in range(a, b + 1): CTX[i] = c
PLAN = {
  0: ["DOG_EYES_DARK", "YARD_WIDE_DOOR_LIGHT", "CU_YOU_DOOR"], 1: ["INS_DOOR_HANDLE"], 2: ["PORCH_STEPS_POV", "KT_DONT_GO"],
  3: ["SQUIRREL_DAY", "SQUIRREL_TREE"], 4: ["EYES_GONE"], 5: ["CLOCK_CARD"], 6: ["DOOR_OPENS_OUT", "CU_YOU_CALL"],
  7: ["YARD_FROM_PORCH", "DOG_SIDE_MED"], 8: ["DOG_HEAD_TURN"], 9: ["OTS_DOG_TO_HOUSE", "DOORWAY_BEHIND_YOU", "HALL_PUSH", "DOG_BACKS_AWAY"],
  10: ["SKY:", "DOG_CU:face,tuck"], 11: ["KITCHEN:"], 12: ["KITCHEN:", "KITCHEN:"], 13: ["KITCHEN:hum"], 14: ["CLOCKS:", "CLOCKS:"],
  15: ["BOWL:"], 16: ["BOWL:"], 17: ["DOG_CU:head,tuck"], 18: ["COUNT:"], 19: ["DOG_FULL:", "DOG_CU:tail", "DOG_CU:eyes,face"],
  20: ["DOG_CU:tail,tuck"], 21: ["DOG_CU:tail,tuck", "DOG_FULL:tuck", "KT:NOT_A_GAME"], 22: ["HALL:far", "YOU_CU:scared"],
  23: ["DOG_CU:face,tuck", "YOU_FULL:"], 24: ["TAGS:"], 25: ["TAGS:hi1", "YOU_CU:call", "KT:RULE_1"], 26: ["TAGS:hi7", "DOG_FULL:wag", "YOU_CU:tears"],
  27: ["TAGS:1"], 28: ["YOU_CU:call"], 29: ["YOU_CU:"], 30: ["DOG_CU:head"], 31: ["YARD:"], 32: ["KT:STOP."],
  33: ["HALL:far", "HALL:mid"], 34: ["WAVE:"], 35: ["WAVE:both", "YOU_CU:call"], 36: ["WAVE:it"], 37: ["YOU_CU:whistle", "DOG_CU:ears"],
  38: ["WAVE:both", "HALL:voice,mid", "YOU_CU:scared"], 39: ["HALL:mid"], 40: ["WAVE:it", "HALL:voice,near"], 41: ["KT:IT'S_LEARNING."],
  42: ["HALL:voice,far", "DOG_FULL:tuck", "YOU_CU:scared", "KT:NOT_YOU."],
  43: ["TAGS:2"], 44: ["YOU_CU:back"], 45: ["YOU_CU:scared", "HALL:near"], 46: ["YOU_CU:cold", "ARM_HAIR:"], 47: ["KITCHEN:"],
  48: ["ARM_HAIR:", "YOU_CU:scared"], 49: ["KT:DON'T_TURN."], 50: ["DOG_CU:face,tuck"], 51: ["DOG_CU:eyes,face"], 52: ["DOG_CU:eyes,shoulder"],
  53: ["DOG_CU:eyes,face", "HALL:far"], 54: ["DOG_CU:eyes,shoulder", "YOU_CU:cold"], 55: ["WINDOW:"], 56: ["WINDOW:"],
  57: ["WINDOW:", "YOU_FULL:", "WINDOW:"], 58: ["WINDOW:shape", "YOU_CU:scared"],
  59: ["TAGS:3"], 60: ["YOU_FULL:frame"], 61: ["HANDS:lock", "CURTAIN:", "HANDS:"], 62: ["KT:DON'T."], 63: ["DIAGRAM:closed,you", "YOU_FULL:", "DOG_FULL:tuck"],
  64: ["DIAGRAM:guard,you", "DOG_FULL:", "DOORFRAME_VIEW:"], 65: ["DOG_FULL:glow", "KT:30,000_YEARS"], 66: ["DOG_CU:face"],
  67: ["CURTAIN:move", "CURTAIN:move", "YOU_CU:scared"], 68: ["CURTAIN:move"], 69: ["KT:LET_IT_TEST."], 70: ["DOORFRAME_VIEW:"],
  71: ["TAGS:4", "DOG_CU:ears"], 72: ["DOG_CU:face", "YOU_CU:side"], 73: ["DOG_CU:ears", "EAR_CHART:up"], 74: ["DOG_CU:ears,flat", "EAR_CHART:flat", "YOU_CU:scared"],
  75: ["DOG_CU:ears,one", "EAR_CHART:one"], 76: ["DOG_CU:face,flat,growl", "DOG_FULL:growl,tuck", "YOU_CU:scared", "HALL:near", "DOG_CU:head,flat,growl"],
  77: ["DOG_CU:eyes,shoulder", "YOU_CU:cold"], 78: ["DOG_CU:ears,flat"], 79: ["KT:IT_DOES."],
  80: ["TULSA:file"], 81: ["TULSA:duke"], 82: ["TULSA:duke"], 83: ["TULSA:man,call"], 84: ["TULSA:man"], 85: ["TULSA:man", "SKY:"],
  86: ["HALL:voice,far", "TULSA:man,scared", "HALL:voice,mid"], 87: ["HALL:voice,near", "KT:DUKE._COME_ON."], 88: ["TULSA:man,scared", "TULSA:duke,wag"],
  89: ["TULSA:past", "HALL:empty"], 90: ["BOWL:duke"], 91: ["TULSA:collar", "TULSA:collar"], 92: ["TULSA:file"], 93: ["TULSA:night", "HALL:voice,mid"],
  94: ["TULSA:night", "KT:GOOD_BOY."],
  95: ["TAGS:5", "PORCH:"], 96: ["YOU_FULL:", "DOG_FULL:"], 97: ["KT:IT_ISN'T."], 98: ["PORCH:line"], 99: ["DIAGRAM:line,you", "PORCH:"],
  100: ["PORCH:", "HALL:empty", "DIAGRAM:line,shape"], 101: ["HALL:far"], 102: ["NEIGHBORS:", "NEIGHBORS:", "YOU_CU:scared"], 103: ["PORCH:line"],
  104: ["TAGS:6", "HALL:voice,far"], 105: ["WAVE:both", "YOU_CU:smile", "KT:NO_WHISTLE."], 106: ["WHISTLE:"], 107: ["HALL:far", "KT:IT_DOESN'T_BREATHE."],
  108: ["HALL:voice,mid", "YOU_CU:", "WHISTLE:", "DOG_CU:face,wag"], 109: ["DOG_FULL:wag"], 110: ["HANDS:knock", "HANDS:knock", "YOU_CU:"],
  111: ["DOG_CU:head,wag", "DOG_FULL:wag"],
  112: ["KT:NOW_THINK."], 113: ["BEDROOM_DOOR:"], 114: ["BEDROOM_DOOR:", "BEDROOM_DOOR:", "DOG_CU:face", "HALL:empty", "BEDROOM_DOOR:day"],
  115: ["MEMORY:box", "MEMORY:move"], 116: ["MEMORY:cry"], 117: ["KITCHEN:"], 118: ["MEMORY:room"], 119: ["MEMORY:move", "BEDROOM_DOOR:puppy,sleep"],
  120: ["YOU_CU:tears"], 121: ["DOG_CU:head"], 122: ["KT:HE_WASN'T."], 123: ["BEDROOM_DOOR:"], 124: ["DOORFRAME_VIEW:"], 125: ["HALL:far"],
  126: ["TAGS:7"], 127: ["DOG_FULL:away"], 128: ["YOU_CU:back", "HALL:foot,mid"], 129: ["HALL:foot,near", "YOU_CU:scared"], 130: ["HALL:near"],
  131: ["DOG_FULL:back,tuck", "YARD:edge,tuck"], 132: ["DOG_CU:face"], 133: ["KT:DON'T_CALL."], 134: ["KT:DON'T_WHISTLE."], 135: ["KT:DON'T_FOLLOW."],
  136: ["WOODS:lead", "YARD:away", "WOODS:lead"], 137: ["YOU_CU:cold", "YARD:mist,nodog", "YARD:mist,nodog"], 138: ["SKY:"], 139: ["WOODS:dawn"],
  140: ["WOODS:dawn,return", "WOODS:dawn,return", "DOG_CU:paws"], 141: ["DAWN_KITCHEN:"], 142: ["BOWL:eat"], 143: ["BEDROOM_DOOR:day", "BEDROOM_DOOR:day"],
  144: ["DOG_CU:eyes,face", "YARD:tuck", "YOU_FULL:"], 145: ["DOORFRAME_VIEW:"], 146: ["PORCH:"], 147: ["DOG_CU:face"], 148: ["BEDROOM_DOOR:final", "DOG_CU:face,glow"],
}

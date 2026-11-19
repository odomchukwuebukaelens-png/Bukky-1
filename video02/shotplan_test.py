"""Video 02 test (0:00-0:30) shot plan. Every entry is a different shot; nothing is split or repeated."""
PAUSES = {4: 0.6}
PLAN = {
  0: [("DOG_EYES_DARK", "slow push", "eyes don't blink"), ("YARD_WIDE_DOOR_LIGHT", "drift", "dog far out on the lawn"),
      ("CU_YOU_DOOR", "push", "you stop calling mid-word")],
  1: [("INS_DOOR_HANDLE", "push", "hand reaches for the handle, pulls back"), ("PORCH_STEPS_POV", "push", "your sneakers at the threshold"),
      ("KT_DONT_GO", "slam", "text slam")],
  2: [("SQUIRREL_DAY", "track", "comedy: dog chases squirrel"), ("SQUIRREL_TREE", "tilt up", "squirrel taunts from branch")],
  3: [("EYES_GONE", "static", "eyes switch off"), ("CLOCK_CARD", "static", "11:48 PM")],
  4: [("KITCHEN_NIGHT_WIDE", "pan", "you cross the kitchen; full bowl")],
  5: [("DOOR_OPENS_OUT", "push", "door swings open, light floods porch"), ("CU_YOU_CALL", "push", "BRUNO!")],
  6: [("YARD_FROM_PORCH", "push", "dog dead centre of the lawn"), ("DOG_SIDE_MED", "drift", "tail still, ears up")],
  7: [("DOG_HEAD_TURN", "push", "head turns to camera")],
  8: [("OTS_DOG_TO_HOUSE", "push", "you tiny in the doorway"), ("DOORWAY_BEHIND_YOU", "slow push", "a darker shape in the hall"),
      ("HALL_PUSH", "push", "into the house"), ("DOG_BACKS_AWAY", "track", "tail tucked, backing off, growl")],
}

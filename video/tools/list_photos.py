#!/usr/bin/env python3
"""Record which photos are present so shots can fall back to drawn visuals when one is missing.
Usage: python3 tools/list_photos.py <folder> <output json>"""
import json, os, sys
folder, out = sys.argv[1:3]
json.dump(sorted(f[:-4] for f in os.listdir(folder) if f.endswith(".jpg")), open(out, "w"))

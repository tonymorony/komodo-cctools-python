#!/usr/bin/env python3

seed = "2139495316301712247"
levels = "7"

levels_counter = int(levels)
iterator = 1
filenames = []

while iterator <= levels_counter:
    filenames.append("rogue." + seed + "." + str(iterator))
    iterator = iterator + 1

with open(seed + "_combined.txt", 'w') as outfile:
    for fname in filenames:
        with open(fname) as infile:
            outfile.write(infile.read())


print("Succesfully combined to: " + seed +  "_combined.txt file")
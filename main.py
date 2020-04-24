# William Brunton 2020
# Windows only, feel free to modify for Mac or Linux

__version__ = '''1.0.0'''

import argparse
import os
import gzip
import sys
import glob
import re
import itertools

# All the regexes we need
chatRegex = re.compile('\[CHAT\](.*)')
dateRegex = re.compile('\d{4}\-\d{2}\-\d{2}')
timeRegex = re.compile('\d{2}:\d{2}:\d{2}')

# The format the script'll output in
outFormat = "Found match @ {} {}: {}\n"

# Get all the arguments
parser = argparse.ArgumentParser(description="Crawls a Minecraft chat log archive.")
parser.add_argument('-dir', type=str, help="The directory to search in.")
parser.add_argument('-search', type=str, help="The string to search for, surround with quotes (\"\" or \'\') if there are spaces in it")
parser.add_argument('-output', type=str, help="The file to output to")
args = parser.parse_args()

# Tries to create a default directory to use
if 'appdata' not in os.environ:
    print("Cannot find default path, a custom path must be supplied.")
    canUseDefaultPath = False
else:
    defaultPath = '{}\.minecraft\logs'.format(os.environ['appdata'])
    if not os.path.exists(defaultPath):
        print("Cannot find default path, a custom path must be supplied.")
        del defaultPath
        canUseDefaultPath = False
    else:
        canUseDefaultPath = True

# In case the user hasn't given a search term in the arguments
if not args.search:
    print("A search string was not supplied, please supply one:")
    args.search = input()

# Deals with custom directories
if args.dir:
    if os.path.exists(args.dir):
        print("Using {}".format(args.dir))
        path = args.dir
    else:
        print("The custom path was invalid.")
        sys.exit()
else:
    if canUseDefaultPath:
        print("Using default path.")
        path = defaultPath
    else:
        print("No path was supplied.")
        sys.exit()

#Creates the output file, if specified
if args.output:
    with open(args.output, 'w') as out:
        out.write("Search term: {}\n".format(args.search))

# Creates an iterator with all the files we want to check
files = itertools.chain(glob.iglob(path + '\\*.log.gz'), glob.iglob(path + '\\latest.log'))

for file in files:

    # See if we can get a date or if this is the latest session
    dateSearch = re.search(dateRegex, file)
    if dateSearch:
        date = dateSearch[0]
    else:
        date = "Latest Session"

    # Try to open the file with gzip, if it doesn't work try opening as a normal text file
    try:
        decompressed = gzip.open(file, 'rt').read()
    except:
        decompressed = open(file, 'r').read()
        
    linesRaw = decompressed.split('\n')
    linesChat = []
    
    for line in linesRaw:
        # See if it's a chat line
        res = re.search(chatRegex, line)
        if res:
            time = re.search(timeRegex, line)[0]
            linesChat.append((date, time, res[1][1:]))
    
    for line in linesChat:
        # Lazy way of checking if the search string's in the line
        if args.search in line[2]:
            if args.output:
                with open(args.output, 'a') as out:
                    out.write(outFormat.format(*line))
            print(outFormat.format(*line))

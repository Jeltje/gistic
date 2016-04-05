#!/usr/bin/env python2.7

import sys, os, re, getopt
import argparse
import math
from bisect import bisect_left
from collections import OrderedDict

usage = sys.argv[0]+"""

Trims Adtex format CNV start and end coordinates to match nearest
marker in markerfile. This creates GISTIC input.
Derives sample name from filename. Sample IDs can NOT have periods.


"""
def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--targets', required=True, help='exome targets file in bed format')
    parser.add_argument('-l', '--inlist', required=True, help='list of cnv locations')
    parser.add_argument('-m', '--markerout', required=True, help='name of output markerfile')
    parser.add_argument('-s', '--segout', required=True, help='name of output segmentationfile')
    return parser

def bedToMarkers(bedfile, markerObj, outputfile):
    """
    Converts gistic input format markers file from a bed format input
    """
    # bed is chrom, start, end, id, other fields
    # must remove chr from chrom
    # markersfile is id, chrom, pos. We need the start and end from the bed input on separate lines

    id = 0
    with open(outputfile, 'w') as w, open(bedfile, 'r') as f:
        for line in f.readlines():
            sample = line.strip().split('\t')
            (chrom, start, end), rest = sample[:3], sample[3:]
            if chrom.startswith('chr'):
                    chrom = chrom[3:]
            markerObj.add(chrom, start)
            markerObj.add(chrom, end)
            id += 1
            w.write("s{}\t{}\t{}\n".format(id, chrom, start))
            id += 1
            w.write("e{}\t{}\t{}\n".format(id, chrom, end))


class markers(object):
    def __init__(self):
        self.chromdict = dict()  
    def add(self, chrom, coord):
        try:
            self.chromdict[chrom].append(int(coord))
        except KeyError:
            self.chromdict[chrom] = [int(coord)]
    def sort(self):
        for chr in self.chromdict:
            self.chromdict[chr].sort()

    def trim(self, cnv, sampleId):
        """Trim input start and end coordinate to nearest chromosome coordinate"""
        cfields = cnv.split("\t")
        cchrom = cfields[0]
        #cfields.insert(0, sampleId)
        if cchrom == 'chrom' or cchrom == 'chr':
            print >>sys.stderr, "skipping", cnv
            return None
        if cchrom.startswith('chr'):
            cchrom = cchrom[3:]
        cstart = int(cfields[7])
        cend   = int(cfields[8])
        new = takeClosest(self.chromdict[cchrom], cstart, "right")
        cstart = new
        new = takeClosest(self.chromdict[cchrom], cend, "left")
        cend = new
        if cstart > cend:
             print >>sys.stderr, "skipping", cnv
             return None
        score = math.log(float(cfields[9]),2) -1
        return "{}\t{}\t{}\t{}\t{}\t{}".format(sampleId, cchrom, cstart, cend, 'placeholder', score)  

def takeClosest(myList, myNumber, side):
    """
    Assumes myList is sorted. Returns closest value to myNumber on submitted side.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if side == "left":
        return myList[pos-1]
    if side == "right":
        return myList[pos]

def orderedCount(inputlist):
    """
    Leave list items in order, return unique list with linecounts
    """
    #uniq = []
    count = OrderedDict()
    for i in inputlist:
        if not i in count:
            count[i] = 0
        #    uniq.append(i)
        count[i] += 1
    return count


# Main
# Run program
parser = build_parser()
args = parser.parse_args()

# Create markers object
markerlist = markers()

# Create markers and marker output from input bed file
bedToMarkers(args.targets, markerlist, args.markerout)
markerlist.sort()

# Read in file list
cnvs = []
with open(args.inlist, 'r') as l:
    cnvs = l.read().splitlines()

# sampleIds can only occur once
sampleNames = []
# adtex is quite repetitive, so keep track of lines we already have
printLines = []
# Trim every file and concatenate results to segout file
for infile in cnvs:
    sampleId = os.path.basename(infile).split('.')[0]
    if sampleId in sampleNames:
        print >>sys.stderr, "ERROR sample occurs twice (please check filename requirements):", sampleId
        sys.exit(1)
    with open(infile,'r') as f:
        for line in f.readlines():
            outline = markerlist.trim(line.strip(), sampleId) 
            if outline: 
                printLines.append(outline)

# to get the 'coverage' we count the number of identical segments
# Counter keeps the items in order
counts = orderedCount(printLines)

with open(args.segout, 'w') as s:
    for i in counts:
        print >>s, i.replace('placeholder', str(counts[i]))


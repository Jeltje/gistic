#!/usr/bin/env python2.7

import sys, os, re, getopt
import argparse
from bisect import bisect_left

usage = sys.argv[0]+"""

Trims input CNV start and end coordinates to match nearest
marker in markerfile. This creates GISTIC input.


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

    def trim(self, cnv):
        """Trim input start and end coordinate to nearest chromosome coordinate"""
        cfields = cnv.split("\t")
        if cfields[1] == 'chrom' or cfields[1] == 'chr':
            print >>sys.stderr, "skipping", cnv
            return None
        if cfields[1].startswith('chr'):
            cfields[1] = cfields[1][3:]
        new = takeClosest(self.chromdict[cfields[1]], int(cfields[2]), "right")
        cfields[2] = new
        new = takeClosest(self.chromdict[cfields[1]], int(cfields[3]), "left")
        cfields[3] = new
        if cfields[2] > cfields[3]:
             print >>sys.stderr, "skipping", cnv
             return None
	return ("\t").join(str(x) for x in cfields)

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

# Trim every file and concatenate results to segout file
with open(args.segout, 'w') as s:
    for infile in cnvs:
        with open(infile,'r') as f:
            for line in f.readlines():
                outline = markerlist.trim(line.strip()) 
                if outline:
                    print >>s, outline 



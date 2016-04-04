#!/usr/bin/env python2.7

import sys, os, re, getopt
import math
import argparse
from bisect import bisect_left

usage = sys.argv[0]+"""

Creates GISTIC input (markers and segments) from a list of Adtex zygosity output files
Converts zygosity to log score (-1) and merges SNP lines with identical zygosity
into segments


"""
def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--inlist', required=True, help='list of cnv locations')
    parser.add_argument('-m', '--markerout', required=True, help='name of output markerfile')
    parser.add_argument('-s', '--segout', required=True, help='name of output segmentationfile')
    return parser

class markers(object):
    """
    Creates a dictionary of chromosome names with SNP coordinates
    """
    def __init__(self):
        self.chromdict = dict()  
        # the input is in chromosomal order, easier than trying to sort
        self.chromOrder = []
    def add(self, chrom, coord):
        if chrom in self.chromdict:
            if not int(coord) in self.chromdict[chrom]:
                self.chromdict[chrom].append(int(coord))
        else:
            self.chromdict[chrom] = [int(coord)]
            self.chromOrder.append(chrom)
    def sort(self):
        for chrom in self.chromdict:
            self.chromdict[chrom].sort()



class Segment(object):
    """
    Segment object, allows extension of segment if input has the same score as previous
    """
    def __init__(self, sample, chrom, pos, score):
        self.sample = sample
        self.chrom = chrom
        self.startpos = pos
        self.endpos = pos
        self.count = 1
        self.score = score
    def add(self, sample, chrom, pos, score):
        if self.sample == sample and self.chrom == chrom and self.score == score:
            self.endpos = pos
            self.count += 1
            return True
        return False
    def printLine(self):
        if self.count == 1:
             return False
        # format score
        self.logscore = math.log(float(self.score),2) -1
	return "{}\t{}\t{}\t{}\t{}\t{:.2f}".format(self.sample, self.chrom, self.startpos, self.endpos, self.count, self.logscore)

def makeSegments(zfile, sampleId, markerList):
    """
    From input zygosity line create gistic like segmentation output
    """
    # input looks like
#### chrom      SNP_loc control_BAF     tumor_BAF       control_doc     tumor_doc       mirrored_BAF    cn      z       zygosity
#### chr1       14907   0.49    0.51    165     295     0.49    3       3       ASCNA
#### chr1       14930   0.52    0.54    161     315     0.46    3       3       ASCNA
   # output looks like
#### DTB-005    3       239611  48622928        8101    -0.2445
#### DTB-005    3       48624178        48624350        10      -1.2378
#### DTB-005    3       48625418        90264707        6037    -0.5755
    segments = []
    segObj = False
    with open(zfile,'r') as f:
        for zygline in f.readlines():
            # not using last field so no need for trimming
            cfields = zygline.split("\t")
            cchrom = cfields[0]
            if cchrom == 'chrom' or cchrom == 'chr':
                # create placeholder segment, do not add to segments list
                segObj = Segment(sampleId, cfields[0], cfields[1], cfields[7])
                print >>sys.stderr, "skipping", zygline
                continue
            if cchrom.startswith('chr'):
               cchrom = cchrom[3:]
            if not segObj.add(sampleId, cchrom, cfields[1], cfields[7]):
                segObj = Segment(sampleId, cchrom, cfields[1], cfields[7])
                segments.append(segObj)
            markerList.add(cchrom, cfields[1])
    return segments, markerList

# Main
# Run program
parser = build_parser()
args = parser.parse_args()

# Create markers object
markerlist = markers()

# Read in file list
cnvs = []
with open(args.inlist, 'r') as l:
    cnvs = l.read().splitlines()

# Create markers and segments at the same time 
# sampleIds can only occur once
sampleNames = []
with open(args.segout, 'w') as s:
    for infile in cnvs:
        sampleId = os.path.basename(infile).split('.')[0]
        if sampleId in sampleNames:
            print >>sys.stderr, "ERROR sample occurs twice (please check filename requirements):", sampleId
            sys.exit(1)
        segments, markerlist = makeSegments(infile, sampleId, markerlist)    
        for i in segments:
            segline = i.printLine()
            if segline:
                print >>s, segline

# Now print markers
id = 0
markerlist.sort()
with open(args.markerout, 'w') as w:
    for c in markerlist.chromOrder:
        for pos in markerlist.chromdict[c]:
            id += 1
            w.write("m{}\t{}\t{}\n".format(id, c, pos))


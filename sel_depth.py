#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
from optparse import OptionParser,OptionGroup
from bar.base import validateStructureName
from extlib import selectHierarchical

###############################################################################
#                                                                             #
#    This file is part of 3d Brain Atlas Reconstructor                        #
#                                                                             #
#    Copyright (C) 2010-2011 Piotr Majka                                      #
#                                                                             #
#    3d Brain Atlas Reconstructor is free software: you can redistribute      #
#    it and/or modify it under the terms of the GNU General Public License    #
#    as published by the Free Software Foundation, either version 3 of        #
#    the License, or (at your option) any later version.                      #
#                                                                             #
#    3d Brain Atlas Reconstructor is distributed in the hope that it          #
#    will be useful, but WITHOUT ANY WARRANTY; without even the implied       #
#    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.         #
#    See the GNU General Public License for more details.                     #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along  with  3d  Brain  Atlas  Reconstructor.   If  not,  see            #
#    http://www.gnu.org/licenses/.                                            #
#                                                                             #
###############################################################################

def createOptionParser():
    parser = OptionParser()
    parser = OptionParser(usage="usage: ./sel_depth.py CAF_index structure OPTIONS")
    
    parser.add_option("-g", "--generateSubstructures", dest="generateSubstructures",
            action="store", default=0, type="int",
            help='maximum level of substructures (in the structure tree) to be generated; defaults to 0')
    
    return parser

if __name__ == '__main__':
    parser = createOptionParser()
    (options, args) = parser.parse_args()
    
    if len(args) < 2:
        parser.print_help()
        exit(1)
    
    indexLocation = args[0]
    topGroup = args[1]
    selectionDepth = options.generateSubstructures+1
    groups = selectHierarchical(indexLocation, topGroup, selectionDepth)
    
    print >>sys.stderr, "CAF dataset location:\t%s" % indexLocation
    print >>sys.stderr, "Top group:\t%s" % topGroup
    print >>sys.stderr, "Selection depth:\t%d" % selectionDepth
    print >>sys.stderr, "Printing output to stdout:"
    print groups

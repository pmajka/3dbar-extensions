#!/usr/bin/python
# -*- coding: utf-8 -*-

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

import os, sys
from optparse import OptionParser,OptionGroup
from extlib import changeOrientation 

def createOptionParser():
    parser = OptionParser()
    parser = OptionParser(usage="usage: ./ras.py --inputOrientation RAIcode --outputOrientation RAIcode")
    
    parser.add_option("-i", "--inputOrientation", dest="inputOrientation",
            action="store", default='ras',
            help="Input orientation to be transformed into output orientation in RAI code. 'ras' by default")
    
    parser.add_option("-o", "--targetOrientation", dest="targetOrientation",
            action="store", default='ras',
            help="Target orientation in RAI code. 'ras' by default.")
    
    return parser

if __name__ == '__main__':
    parser = createOptionParser()
    (options, args) = parser.parse_args()
    
    inputOrientation  = options.inputOrientation.lower()
    targetOrientation = options.targetOrientation.lower()
    
    perm, flip = changeOrientation(inputOrientation, targetOrientation)
    
    print "Input orientation:\t%s" % inputOrientation
    print "Target orientation:\t%s" % targetOrientation
    print "Permutation:\t%s" % " ".join(map(str,perm))
    print "Change direction of axes:\t%s" % " ".join(map(str,flip))

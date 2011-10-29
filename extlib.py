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
import bar

from bar import barIndexer

def changeOrientation(inputOrientation, targetOrientation):
    ins, ons = inputOrientation, targetOrientation
    
    ex = {  ('abc'):(0,1,2),
            ('acb'):(0,2,1),
            ('bac'):(1,0,2),
            ('bca'):(1,2,0),
            ('cab'):(2,0,1),
            ('cba'):(2,1,0)}
    rs = {'l':'r','r':'l','a':'p','p':'a','i':'s','s':'i'}
    
    r = []
    for c in ins:
        if not c in ons:
            r.append((rs[c], ins.index(c)))
            ins = ins.replace(c,rs[c])
    
    tr = dict(zip(ins, 'abc'))
    to = map(lambda x:  tr[x], ons)
    
    perm = ex["".join(to)]
    
    flip = []
    for (k,v) in r:
        flip.append(perm[v])
    
    return perm, flip

def selectHierarchical(indexer, topGroup, depth):
    i = barIndexer.fromXML(indexer)
    strtc = topGroup
    ss = map(lambda x: set(i.unfoldSubtrees([strtc],x)), range(depth))
    w=map(lambda z: ss[z]-reduce(lambda x,y: x|y, ss[1:z],set()), range(depth))
    
    return " ".join(map(lambda x: " ".join(list(x)),reversed(w)))

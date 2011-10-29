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

import sys,os
from optparse import OptionParser,OptionGroup
import random 
import numpy, vtk, nifti
import bar

UID_OFFSET = 200000

def rgb(hexVal):
    """
    Converts html hexidecimal color value into RGB color components tuple.
    
    @type  hexVal: C{str}
    @param hexVal: html hexicedimal color string.
    
    @rtype: C{(int,int,int)}
    @return: RGB color components tuple.
    """
    n = eval('0x' + hexVal[1:])
    return (n>>16)&0xff, (n>>8)&0xff, n&0xff

def getColor(groupElem):
    color = rgb(groupElem.fill)
    if color[0] == color[1] == color[2] == 119:
        random.seed(groupElem.id)
        print >>sys.stderr, "\t\tgetColor: Randomizing color: " + groupElem.fill
        color = map(lambda x: float(random.randint(0, 255)), 3*[0])
    return tuple(color)

def imageDataFromNumpy(npArr, spacing, origin, shape, dims=1, outputFilename = None):
    ds, o, p  = shape, origin, spacing
    
    print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr\tinitializing volume..."
    
    d = vtk.vtkImageData()
    d.SetDimensions(*ds)
    d.SetOrigin(o[2],o[1],o[0])
    d.SetSpacing(p[2],p[1],p[0])
    d.SetNumberOfScalarComponents(dims)
    if dims==3:
        d.SetScalarTypeToUnsignedChar()
    else:
        d.SetScalarTypeToUnsignedInt()
    d.AllocateScalars()
    
    print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr: origin: " + str(d.GetOrigin())
    print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr: spacing: " +  str(d.GetSpacing())
    print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr: data type: " + str(d.GetScalarTypeAsString())
    print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr: components no.: " + str(d.GetNumberOfScalarComponents())
    print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr: points no.: " +  str(d.GetNumberOfPoints())
    
    print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr: setting image data..."
    print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr: iteration sequence: %d %d %d" % (ds[2], ds[1], ds[0])
    dScalars = d.GetPointData().GetScalars()
    dComputePointId = d.ComputePointId
    if dims==3:
        for i in range(ds[2]):
            for j in range(ds[1]):
                for k in range(ds[0]):
                    id = d.ComputePointId((k,j,i))
                    dScalars.SetTuple3(id, *map(float,npArr[k,j,i]))
    if dims==1:
        for i in range(ds[2]):
            for j in range(ds[1]):
                for k in range(ds[0]):
                    id = d.ComputePointId((k,j,i))
                    dScalars.SetTuple1(id, int(npArr[k,j,i]))
    
    print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr: applying vtkImagePermute()"
    permute = vtk.vtkImagePermute()
    permute.SetFilteredAxes(2,1,0)
    permute.SetInput(d)
    
    print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr: applying vtk.vtkImageCast()"
    cast = vtk.vtkImageCast()
    cast.SetInput(permute.GetOutput())
    cast.SetOutputScalarTypeToFloat()
    cast.Update()
    
    print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr: applying vtk.vtkImageCast()"
    cast2 = vtk.vtkImageCast()
    cast2.SetInput(cast.GetOutput())
    cast2.SetOutputScalarTypeToUnsignedInt()
    cast2.Update()
    
    print >>sys.stderr, cast2.GetOutput()
    
    if outputFilename:
        print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr: writing to: %s" %  outputFilename
        w = vtk.vtkStructuredPointsWriter()
        w.SetInput(cast2.GetOutput())
        w.SetFileName(outputFilename)
        w.Update()
    
    print >>sys.stderr, "\timageDataFrom3dRGBNumpyArr: done."
    return cast2.GetOutput()

def appendSingleMask(idxArray, rgbArray, groupElem, niftiVolume, threshold = 128):
    i = niftiVolume
    id = long(groupElem.id)
    color = getColor(groupElem)
    
    print >>sys.stderr, "\tappendSingleMask: start"
    print >>sys.stderr, "\tappendSingleMask: group name: %s" % groupElem.name
    print >>sys.stderr, "\tappendSingleMask: group id: %s" % groupElem.id
    print >>sys.stderr, "\tappendSingleMask: group fill: %s / %s" % (groupElem.fill, " ".join(map(str,color)))
    
    temp = i.data
    temp[temp < threshold] = False
    temp[temp >= threshold] = True
    
    volCurNewXor = numpy.logical_xor(temp, idxArray)
    volXorAndNew = numpy.logical_and(temp,volCurNewXor)
    idxArray[volXorAndNew] = id - UID_OFFSET
    rgbArray[volXorAndNew] = numpy.array(color)
    
    print >>sys.stderr, "\tappendSingleMask: done"
    print >>sys.stderr, "\t"

def mergeVolumes(options, args, idx):
    volumeFilenameTemplate = options.maskfilenametemplate
    outputRGBFilename = options.outputrgbvolume
    outputIndexedFilename = options.outputindexedvolume
    threshold = options.threshold
    volumesDir = args[1]
    groupsToMerge = args[2:]
    idxArray = None
    
    for group in groupsToMerge:
        niftiFilename = os.path.join(volumesDir, volumeFilenameTemplate % group)
        groupElem = idx.groups[group]
        
        print >>sys.stderr, "\tMain loop: Processing group: %s" % group
        print >>sys.stderr, "\tMain loop: opening niftii file: %s" % niftiFilename
        
        niftiVolume = nifti.NiftiImage(niftiFilename)
        print >>sys.stderr, "\tMain loop: opening niftii file: %s done." % niftiFilename
        
        if idxArray == None:
            print >>sys.stderr, "\tMain loop: initializing volumes..."
            
            ds = niftiVolume.data.shape
            o  = niftiVolume.header['qoffset']
            p  = niftiVolume.header['pixdim'][1:4]
            
            idxArray = numpy.zeros((ds[0],ds[1],ds[2]), dtype=numpy.uint8)
            rgbArray = numpy.zeros((ds[0],ds[1],ds[2],3), dtype=numpy.uint8)
            
            print >>sys.stderr, "\tMain loop: volume shape: %d %d %d" % ds
            print >>sys.stderr, "\tMain loop: volume origin: %f %f %f" % tuple(o)
            print >>sys.stderr, "\tMain loop: volume dimensions: %d %d %d" % tuple(p)
        
        print >>sys.stderr, "\tMain loop: Merging volumes..."
        appendSingleMask(idxArray, rgbArray, groupElem, niftiVolume, threshold=threshold)
        
    if outputRGBFilename:
        print >>sys.stderr, "\tMain loop: Converting to rgb vtkImageData..."
        imageDataFromNumpy(rgbArray, p, o, ds, dims=3, outputFilename = outputRGBFilename)

    if outputIndexedFilename:
        print >>sys.stderr, "\tMain loop: Converting to indexed vtkImageData..."
        imageDataFromNumpy(idxArray, p, o, ds, dims=1, outputFilename = outputIndexedFilename)

def dumpLUT(indexer, outFilename):
    print >>sys.stderr, "\tdumpLUT\tSaving lookup table to: " + outFilename
    
    cmap = indexer.colorMapping
    fmap = indexer.fullNameMapping
    
    fh = open(outFilename,'w')
    for group in cmap.keys():
        i = indexer.groups[group].id - UID_OFFSET
        c = getColor(indexer.groups[group])
        s = '%d\t%d\t%d\t%d\t%s\t%s\n' % (i, c[0], c[1], c[2], group, fmap[group])
        fh.write(s) 
    fh.close()
    print >>sys.stderr, "\tdumpLUT\tSaving lookup table ok."
    print >>sys.stderr, "\t"

def createOptionParser():
    parser = OptionParser()
    parser = OptionParser(usage="usage: ./niftimerger.py CAF_index nii_volumes_dir struct1, struct2, ...")
    
    parser.add_option("-o", "--outputindexedvolume", dest="outputindexedvolume",
            action="store", default=None,
            help="Output indexed volume filename.")
    
    parser.add_option("-c", "--outputrgbvolume", dest="outputrgbvolume",
            action="store", default=None,
            help="Output rgb volume filename.")

    parser.add_option("-l", "--outputlut", dest="outputLutFilename",
            action="store", default=None,
            help="Output lookup table filename.")
    
    parser.add_option("-t", "--maskthreshold", dest="threshold",
            action="store", default=128, type="int",
            help="Threshold level that will be applided to each mask before merging. Default value: 128")
    
    parser.add_option("-m", "--maskfilenametemplate", dest="maskfilenametemplate",
            action="store", default='volume_%s.nii.gz',
            help="Nifti volume filename template. Default: volume_%s.nii.gz, where %s is replced with the stucture name")
    
    return parser

if __name__ == '__main__':
    parser = createOptionParser()
    (options, args) = parser.parse_args()
    
    barpath  = args[0]
    indexer = bar.barIndexer.fromXML(barpath)
    mergeVolumes(options,args,indexer)
    
    if options.outputLutFilename:
        dumpLUT(indexer, options.outputLutFilename)

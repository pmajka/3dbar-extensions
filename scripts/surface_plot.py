#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    This file is part of 3d Brain Atlas Reconstructor                        #
#                                                                             #
#    Copyright (C) 2011 Piotr Majka                                           #
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

import vtk
import sys
import os
from optparse import OptionParser,OptionGroup
from bar import barIndexer

class surfacePlot():
    def __init__(self, rgbImageData = None, indexedImageData = None, indexer = None):
        pass

pl3d = vtk.vtkStructuredPointsReader()
pl3d.SetScalarsName("rgb-volume")
pl3d.SetFileName('xxxxxc.vtk')
pl3d.Update()

print pl3d.GetOutput().GetScalarRange()
print pl3d.GetOutput().GetNumberOfScalarComponents()
print pl3d.GetOutput().GetScalarTypeAsString()

cast = vtk.vtkImageCast()
cast.SetInput(pl3d.GetOutput())
cast.SetOutputScalarTypeToUnsignedChar()
cast.Update()
print cast.GetOutput().GetScalarTypeAsString()

#pl2d = vtk.vtkStructuredPointsReader()
#pl2d.SetScalarsName("scalars")
#pl2d.SetFileName("xxxxxc.vtk")
#pl2d.Update()

poly = vtk.vtkPolyDataReader()
poly.SetFileName("model_Ctx.vtk")
poly.Update()

contTable = vtk.vtkLookupTable()
contTable.SetHueRange(0.4, 0.967)
contTable.SetSaturationRange(1.0, 1.0)
contTable.SetValueRange(0, 1000)
contTable.SetNumberOfColors(1000)
contTable.Build()

probe2 = vtk.vtkProbeFilter()
probe2.SetInput(poly.GetOutput())
probe2.SpatialMatchOn()
probe2.SetSource(cast.GetOutput())

cast2 = vtk.vtkCastToConcrete()
cast2.SetInput(probe2.GetOutput())

normals = vtk.vtkPolyDataNormals()
normals.SetInputConnection(cast2.GetOutputPort())
normals.SetFeatureAngle(45)

# We indicate to the mapper to use the velcoity magnitude, which is a
# vtkDataArray that makes up part of the point attribute data.
isoMapper = vtk.vtkPolyDataMapper()
isoMapper.SetInputConnection(normals.GetOutputPort())
isoMapper.ScalarVisibilityOn()
#isoMapper.SetColorModeToMapScalars()
isoMapper.SetColorModeToDefault()
#isoMapper.SetScalarModeToUsePointData()
isoMapper.SetScalarRange(200001,201000)
isoMapper.SetLookupTable(contTable)
normals.Update()
pl3d.Update()
#print iso.GetOutput().GetScalarRange()
#print normals.GetOutput().GetScalarRange()

isoActor = vtk.vtkLODActor()
isoActor.SetMapper(isoMapper)
isoActor.SetNumberOfCloudPoints(1000)

# Create the usual rendering stuff.
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors to the renderer, set the background and size
ren.AddActor(isoActor)
#ren.SetBackground(1, 1, 1)
#renWin.SetSize(500, 500)
#ren.SetBackground(0.1, 0.2, 0.4)

pd = normals.GetOutput()
dd = normals.GetOutput().GetPointData().GetScalars()
n = pd.GetNumberOfPoints()

imagePoints = pl3d.GetOutput()
for i in range(n):
    x = pd.GetPoint(i)
    c = map(int,dd.GetTuple3(i))
    #c = int(dd.GetTuple1(i))
    imagePointId = imagePoints.FindPoint(*x)
    #trueValue = int(imagePoints.GetPointData().GetScalars().GetTuple1(imagePointId))
    trueValue = map(int,imagePoints.GetPointData().GetScalars().GetTuple3(imagePointId))
    #dd.SetTuple1(i,float(trueValue))
    dd.SetTuple3(i,*map(float,trueValue))
    #if trueValue in [ [188, 196, 166], [76,123,149],[154,145,19]] :
    #    dd.SetTuple3(i,*map(float,trueValue))
    #else:
    #    dd.SetTuple3(i,70,70,70)
    print "%d\t" %i + "\t".join(map(str,x)) + "\t" + "\t".join(map(str,c))+ "\t" + "\t".join(map(str,trueValue))
    #print "%d\t" %i + "\t".join(map(str,x)) + "\t" + "\t"+str(c) + "\t" + str(trueValue)

w = vtk.vtkPolyDataWriter()
w.SetFileName('a.vtk')
w.SetInput(normals.GetOutput())
w.Update()

iren.Initialize()
renWin.Render()
iren.Start()



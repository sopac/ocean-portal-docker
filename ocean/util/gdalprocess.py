#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo<s.guo@bom.gov.au>

import os
import subprocess

#create geo-referenced image
#example: 
#    gdal_translate -of Gtiff  -a_srs EPSG:4326 -a_ullr 110 90 290  -90 REY00001_pac_20160427_mean_map.png REY00001_pac_20160427_mean_map.tif
#gdal_translate = "gdal_translate -of Gtiff  -a_srs EPSG:4326 -a_ullr 110 90 290  -90 REY00001_pac_20160427_mean_map.png map.tif"

#create shape files
#example: 
#    gdal_polygonize.py REY00001_pac_20160427_mean_map.tif -f "ESRI Shapefile" REY00001_pac_20160427_mean_map.shp
#gdal_polygonize = 'gdal_polygonize.py' + tempFile + '-f "ESRI Shapefile" '

def gdal_process(mapImgFile, ulx, uly, lrx, lry):
    geoMapImgFile = os.path.splitext(mapImgFile)[0] + '.tif'

    #gdal_translate to add geo reference to the map image 
    with open(os.devnull, 'wb') as devnull:
        subprocess.check_call(['gdal_translate', '-of', 'Gtiff', '-a_srs', 'EPSG:4326', 
                               '-a_ullr', str(ulx), str(uly), str(lrx), str(lry), 
                               mapImgFile, geoMapImgFile],
                              stdout=devnull, 
                              stderr=devnull)

    #gdal_polygonize to convert geo-referenced map image to shape file
    shpFile = os.path.splitext(mapImgFile)[0] + '.shp'
    prjFile = os.path.splitext(mapImgFile)[0] + '.prj'
    shxFile = os.path.splitext(mapImgFile)[0] + '.shx'
    dbfFile = os.path.splitext(mapImgFile)[0] + '.dbf'

    try:
        os.remove(shpFile)
        os.remove(prjFile)
        os.remove(shxFile)
        os.remove(dbfFile)
    except:
        pass

    with open(os.devnull, 'wb') as devnull:
        subprocess.check_call(['gdal_polygonize.py', geoMapImgFile, '-f', 'ESRI Shapefile', shpFile],
                              stdout=devnull, 
                              stderr=devnull)
    os.remove(geoMapImgFile)

def gdal_translate(mapImgFile, ulx, uly, lrx, lry):
    geoMapImgFile = os.path.splitext(mapImgFile)[0] + '.tif'

    
    with open(os.devnull, 'wb') as devnull:
        subprocess.check_call(['gdal_translate', '-of', 'Gtiff', '-a_srs', 'EPSG:4326', '-a_ullr', ulx, uly, lrx, lry, mapImgFile, geoMapImgFile],
                              stdout=devnull, 
                              stderr=devnull)


def gdal_polygonize(mapImgFile):
    geoMapImgFile = os.path.splitext(mapImgFile)[0] + '.tif'
    shpFile = os.path.splitext(mapImgFile)[0] + '.shp'
    gdal_polygonize = gdal_polygonize.split()

    with open(os.devnull, 'wb') as devnull:
        subprocess.check_call(['gdal_polygonize.py', geoMapImgFile, '-f', '"ESRI Shapefile"', shpFile],
                              stdout=devnull, 
                              stderr=devnull)
    os.remove(geoMapImgFile)

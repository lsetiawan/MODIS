#!/usr/bin/env python
import rasterio as rio
from rasterio import crs
from rasterio.transform import Affine
from rasterio.warp import (reproject, Resampling, calculate_default_transform, transform_bounds)
from math import ceil
import numpy as np
import os, shutil

def project2wgs(gtiff, output):
    with rio.Env():
        with rio.open(gtiff) as src:
            out_kwargs = src.meta.copy()
            out_kwargs['driver'] = 'GTiff'

            print(out_kwargs)

            res = (0.01, 0.01)
            dst_crs = crs.from_string('+units=m +init=epsg:4326')

            #dst_width, dst_height = src.width, src.height
            xmin, ymin, xmax, ymax = [-127.8294048826629989,5.1830409679864857,
                                      -59.0561278820333229,49.9999999955067977]
            dst_transform = Affine(res[0], 0, xmin, 0, -res[1], ymax)
            dst_width = max(int(ceil((xmax - xmin) / res[0])), 1)
            dst_height = max(int(ceil((ymax - ymin) / res[1])), 1)
            print(dst_transform)

            out_kwargs.update({
                    'crs': dst_crs,
                    'transform': dst_transform,
                    'affine': dst_transform,
                    'width': dst_width,
                    'height': dst_height
                })

            print(out_kwargs)

            with rio.open(output, 'w', **out_kwargs) as dst:
                reproject(
                    source=rio.band(src, 1),
                    destination=rio.band(dst, 1),
                    src_transform=src.affine,
                    src_crs=src.crs,
                    src_nodata=src.nodata,
                    dst_transform=out_kwargs['transform'],
                    dst_crs=out_kwargs['crs'],
                    dst_nodata=src.nodata,
                    resampling=0,
                    num_threads=2)


def calcMean(file_loc, merged, count, out):
    with rio.Env():
        #month = [rio.open(f) for f in file_loc]
        #data = [m.read(1) for m in month]
        raw = []
        print("Calculating Mean")

        for f in file_loc:
            m = rio.open(f)
            data = m.read(1)
            #print(ds.shape)
            raw.append(np.where(data == -3000, np.nan, data))
            #raw.append(data)

        meanArray = np.average(raw, axis=0)
        print(meanArray.shape)
        #print meanArray.astype(rio.int16)

        final_array = np.where(meanArray == np.nan, -3000, data)
        print final_array

        # print final_array.shape

        # raw = [np.where(data[d] == -3000, np.nan, data[d]) for d in range(0,len(data))]
        # for r in range(0,len(raw)):
        # total_sum = total_sum + raw[r]
        # mean = total_sum / len(data)
        # mean = np.array(raw)

        profile = m.profile
        src_prj = m.crs
        src_trans = m.transform
        #rows = final_array.shape[0]
        #cols = final_array.shape[1]
        profile['nodata'] = -3000
        print(profile)

        with rio.open(out, 'w', **profile) as dst:
            dst.write(final_array, 1)

def main():
    #dest = "/media/lsetiawan/main/data/"
    dest = "/Users/lsetiawan/Desktop/shared_ubuntu/APL/MODIS/data"

    merged = os.path.join(dest, 'merged')

    count = 1
    dates = []
    '''for j in range(1, 13):
        for date in os.listdir(merged):
            if j == 1 and ".0{}.01".format(j) in date:
                if not os.path.exists(os.path.join(merged,str(j))):
                    os.makedirs(os.path.join(merged,str(j)))
                mv = os.path.join(merged,str(j))
                shutil.move(os.path.join(merged,date), os.path.join(mv,date))
            if j == 2 and ".0{}.01".format(j) in date:
                if not os.path.exists(os.path.join(merged, str(j))):
                    os.makedirs(os.path.join(merged, str(j)))
                mv = os.path.join(merged, str(j))
                shutil.move(os.path.join(merged, date), os.path.join(mv, date))
            if j == 3 and ".0{}.01".format(j) in date:
                if not os.path.exists(os.path.join(merged, str(j))):
                    os.makedirs(os.path.join(merged, str(j)))
                mv = os.path.join(merged, str(j))
                shutil.move(os.path.join(merged, date), os.path.join(mv, date))
            if j == 4 and ".0{}.01".format(j) in date:
                if not os.path.exists(os.path.join(merged, str(j))):
                    os.makedirs(os.path.join(merged, str(j)))
                mv = os.path.join(merged, str(j))
                shutil.move(os.path.join(merged, date), os.path.join(mv, date))
            if j == 5 and ".0{}.01".format(j) in date:
                if not os.path.exists(os.path.join(merged, str(j))):
                    os.makedirs(os.path.join(merged, str(j)))
                mv = os.path.join(merged, str(j))
                shutil.move(os.path.join(merged, date), os.path.join(mv, date))
            if j == 6 and ".0{}.01".format(j) in date:
                if not os.path.exists(os.path.join(merged, str(j))):
                    os.makedirs(os.path.join(merged, str(j)))
                mv = os.path.join(merged, str(j))
                shutil.move(os.path.join(merged, date), os.path.join(mv, date))
            if j == 7 and ".0{}.01".format(j) in date:
                if not os.path.exists(os.path.join(merged, str(j))):
                    os.makedirs(os.path.join(merged, str(j)))
                mv = os.path.join(merged, str(j))
                shutil.move(os.path.join(merged, date), os.path.join(mv, date))
            if j == 8 and ".0{}.01".format(j) in date:
                if not os.path.exists(os.path.join(merged, str(j))):
                    os.makedirs(os.path.join(merged, str(j)))
                mv = os.path.join(merged, str(j))
                shutil.move(os.path.join(merged, date), os.path.join(mv, date))
            if j == 9 and ".0{}.01".format(j) in date:
                if not os.path.exists(os.path.join(merged, str(j))):
                    os.makedirs(os.path.join(merged, str(j)))
                mv = os.path.join(merged, str(j))
                shutil.move(os.path.join(merged, date), os.path.join(mv, date))
            if j == 10 and ".{}.01".format(j) in date:
                if not os.path.exists(os.path.join(merged, str(j))):
                    os.makedirs(os.path.join(merged, str(j)))
                mv = os.path.join(merged, str(j))
                shutil.move(os.path.join(merged, date), os.path.join(mv, date))
            if j == 11 and ".{}.01".format(j) in date:
                if not os.path.exists(os.path.join(merged, str(j))):
                    os.makedirs(os.path.join(merged, str(j)))
                mv = os.path.join(merged, str(j))
                shutil.move(os.path.join(merged, date), os.path.join(mv, date))
            if j == 12 and ".{}.01".format(j) in date:
                if not os.path.exists(os.path.join(merged, str(j))):
                    os.makedirs(os.path.join(merged, str(j)))
                mv = os.path.join(merged, str(j))
                shutil.move(os.path.join(merged, date), os.path.join(mv, date))'''
    for j in range(1, 13):

        # Reproject
        sinu = os.path.join(merged,str(j))
        epsg = os.path.join(sinu, '4326')
        '''for e in os.listdir(sinu):
            if ".aux.xml" in e or "4326" in e:
                pass
            else:
                gtiff = os.path.join(sinu, '{}'.format(e))
                if not os.path.exists(epsg):
                    os.makedirs(epsg)
                output = os.path.join(epsg, '{}'.format(e))
                print(gtiff)
                project2wgs(gtiff, output)'''

        # Calculate climatology
        file_loc = [os.path.join(epsg, '{}'.format(m)) for m in os.listdir(epsg) if m != ".DS_Store"]
        print file_loc
        climate = os.path.join(dest, 'climatology')
        if not os.path.exists(climate):
            os.mkdir(climate)
        out = os.path.join(climate, 'EVI_{}.tif'.format(count))
        # print(file_loc)
        calcMean(file_loc, merged, count, out)
        count = count + 1


if __name__ == '__main__':
    main()
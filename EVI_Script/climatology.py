#!/usr/bin/env python
import rasterio as rio
from rasterio import crs
from rasterio.transform import Affine
from rasterio.warp import (reproject, Resampling, calculate_default_transform, transform_bounds)
from math import ceil
import numpy as np
import os

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

def calcMean(file_loc,merged,count, dest):
    climate = os.path.join(dest,'climatology')
    if not os.path.exists(climate):
        os.mkdir(climate)
    out = os.path.join(climate,'EVI_{}.tif'.format(count))
    total_sum = 0
    with rio.Env():
        month = [rio.open(f) for f in file_loc]
        data = [m.read_band(1) for m in month]

        print(data[0].shape)


        raw = [np.where(data[d] == -3000, np.nan, data[d]) for d in range(0,len(data))]
        for r in range(0,len(raw)):
            total_sum = total_sum + raw[r]
        mean = total_sum / len(data)

        profile = month[0].profile
        src_prj = month[0].crs
        src_trans = month[0].transform
        rows = month[0].height
        cols = month[0].width
        profile['nodata'] = -3000

        print(profile)

        with rio.open(out, 'w', **profile) as dst:
            dst_array = np.empty((rows, cols), dtype='int16')
            reproject(
                        # Source parameters
                        source=mean,
                        src_crs=src_prj,
                        src_transform=src_trans,
                        src_nodata = 0,
                        # Destination paramaters
                        destination=dst_array,
                        dst_transform=src_trans,
                        dst_crs=src_prj,
                        dst_nodata=-3000,
                        resampling=0
                    )

            dst.write(dst_array,1)

def main():
    dest = 'data/'

    # Calculate Climatology
    merged = os.path.join(dest, 'merged')
    month_list = []
    count = 0
    for j in range(1, 13):
        dates = [date for date in os.listdir(merged) if "{}.01".format(j) in date]
        month_list.append(dates)
    for m in month_list:
        file_loc = [os.path.join(merged, '{}'.format(i)) for i in m]
        print(file_loc)
        calcMean(file_loc, merged, count, dest)

        count = count + 1

    # Reproject
    climate = os.path.join(dest, 'climatology')
    epsg = os.path.join(climate, '4326')
    for e in os.listdir(climate):
        if ".aux.xml" in e or "4326" in e:
            pass
        else:
            gtiff = os.path.join(climate, '{}'.format(e))
            if not os.path.exists(epsg):
                os.makedirs(epsg)
            output = os.path.join(epsg, '{}'.format(e))
            print(gtiff)
            project2wgs(gtiff, output)


if __name__ == '__main__':
    main()
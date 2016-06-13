#!/usr/bin/env python
import os, glob, gdal, numpy as np, rasterio as rio
from rasterio.merge import merge as merge_tool

def convert2GTiff(MODIS_files, folder):
    for hdf in MODIS_files:
        print("Converting {} to GeoTiff".format(hdf))
        name_list = hdf.split('/')[2].split('.')
        file_name = '{0}.{1}.{2}.{3}.{4}'.format(name_list[0],name_list[1],name_list[2],name_list[3],name_list[4])

        sds = gdal.Open(hdf)
        subdata = sds.GetSubDatasets()

        # QA
        QA_src = gdal.Open(subdata[10][0])
        QA_band = QA_src.GetRasterBand(1)


        in_file = subdata[1][0]

        ds = gdal.Open(in_file)
        band = ds.GetRasterBand(1)

        block_sizes = band.GetBlockSize()
        x_block_size = block_sizes[0]
        y_block_size = block_sizes[1]

        xsize = band.XSize
        ysize = band.YSize


        driver = gdal.GetDriverByName('GTiff')
        dst_ds = driver.Create(os.path.join(folder,"{}.tif".format(file_name)), xsize, ysize, 1, gdal.GDT_Int16)
        dst_ds.SetGeoTransform(ds.GetGeoTransform())
        dst_ds.SetProjection(ds.GetProjection())



        for i in range(0, ysize, y_block_size):
            if i + y_block_size < ysize:
                rows = y_block_size
            else:
                rows = ysize - i
            for j in range(0, xsize, x_block_size):
                if j + x_block_size < xsize:
                    cols = x_block_size
                else:
                    cols = xsize - j

                data = band.ReadAsArray(j, i, cols, rows)
                QA = QA_band.ReadAsArray(j, i, cols, rows)

                # Perform value replacement and drop QA layer
                data[np.logical_and(QA != 0, QA != 1)] = -3000

                dst_ds.GetRasterBand(1).SetNoDataValue(-3000)
                dst_ds.GetRasterBand(1).WriteArray(data,j,i)


        dst_ds = None
        # Close datasets and unallocate arrays
        dst_ds = None
        data = None
        QA = None
        band = None
        QA_band = None

def mergeTile(today, merged, Gtiff_files):
    output = os.path.join(merged,'%s.tif' % (today))
    with rio.Env():
            sources = [rio.open(f) for f in Gtiff_files]
            data, output_transform = merge_tool(sources)

            profile = sources[0].profile
            profile.pop('affine')
            profile['transform'] = output_transform
            profile['height'] = data.shape[1]
            profile['width'] = data.shape[2]
            profile['driver'] = 'GTiff'

            print(profile)

            with rio.open(output, 'w', **profile) as dst:
                dst.write(data)

def main():
    dest = "/media/lsetiawan/main/data/"
    for i in os.listdir(dest):
        if "tif" in i or "4326" in i or "txt" in i or "log" in i or "merge" in i:
            pass
        else:
            print(i)
            folder = os.path.join(dest, i)
            # Check that the data has been downloaded
            MODIS_files = glob.glob(os.path.join(folder, '*.hdf'))
            #print(MODIS_files)

            #convert2GTiff(MODIS_files, folder)

            Gtiff_files = glob.glob(os.path.join(folder, '*.tif'))
            # print(Gtiff_files)

            merged = os.path.join(dest, 'merged')
            if not os.path.exists(merged):
                os.makedirs(merged)
            print("Merging {}".format(i))
            mergeTile(i, merged, Gtiff_files)


if __name__ == '__main__':
    main()
#!/usr/bin/env python
import datetime
import os
import pymodis

def createTiles():
    '''
    Function to create list of tiles to download.
    In this case, MODIS tiles around lower 48 and central america are downloaded
    Tiles are based on sinusoidal projection by NASA

    '''

    h = []
    v = []
    tile = []

    for k in range(7, 15):
        h.append(k)
    for l in range(4, 10):
        v.append(l)
    for i in range(0, len(h) - 1):
        for j in range(0, len(v) - 1):
            if h[i] < 10 and v[i] >= 10:
                tile.append("h0" + str(h[i]) + "v" + str(v[j]))
            elif v[j] < 10 and h[i] >= 10:
                tile.append("h" + str(h[i]) + "v0" + str(v[j]))
            elif h[i] < 10 and v[j] < 10:
                tile.append("h0" + str(h[i]) + "v0" + str(v[j]))
            else:
                tile.append("h" + str(h[i]) + "v" + str(v[j]))
    return tile

def startDownload(tiles,today):
    # Variables for data download
    if not os.path.exists('data'):
        os.makedirs('data')
    dest = "data/"  # This directory must already exist BTW
    tiles = tiles
    day = today
    enddate = "2000.01.01"  # The download works backward, so that enddate is anterior to day=
    product = "MOD13A3.006"

    downloader = pymodis.downmodis.downModis(destinationFolder=folder,
                                             tiles=tiles, today=day, enddate=enddate, product=product)

    downloader.connect()
    print("Connection Attempts: " + str(downloader.nconnection))

    # get all files to download, for each day of interest
    downloads = []
    for day in downloader.getListDays():
        print(day)
        if not os.path.exists(os.path.join(dest, day)):
            os.makedirs(os.path.join(dest, day))
        files = downloader.getFilesList(day)
        # print files
        # make list of all the files
        for f in files:
            downloads.append((f, day))
    numDownload = len(downloads)
    print("Files to Download: " + str(numDownload))

    for filename, day in downloads:
        print("DL: " + filename)
        downloader.downloadFile(filename, os.path.join(dest, day, filename), day)

def main():
    tiles = createTiles()
    print(tiles)

    today = datetime.date.today()
    today.strftime('%Y.%m.%d')

    startDownload(tiles,today)




if __name__ == '__main__':
    main()
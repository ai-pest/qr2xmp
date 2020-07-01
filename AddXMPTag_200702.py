# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        AddExifTag
# Purpose:
#  QRコード画像に収めたメタデータを、jpeg画像にXMPで反映します。
# 
# Created:     11/01/2018
# Updated:     2020/7/2
#-------------------------------------------------------------------------------
import os
import os.path
import pyexiv2
import csv
import codecs
from PIL import Image
import numpy as np
import cv2
import datetime
import pyexiv2.xmp
import zbar
import atexit

# 終了処理の追加
def goodbye():
    """
    終了処理
    """
    raw_input( u"Enter key")
 
atexit.register( goodbye )


scanner = zbar.ImageScanner()
scanner.parse_config('enable')

def show(img, code=cv2.COLOR_BGR2RGB):
    cv_rgb = cv2.cvtColor(img, code)
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.imshow(cv_rgb)
    fig.show()


def decodeQR(im):
    img_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    img_gb = cv2.GaussianBlur(img_gray, (7,7), 0)
    ret,thresh = cv2.threshold(img_gb,80,255,cv2.THRESH_BINARY)
    edges = cv2.Canny(thresh, 90 ,90,apertureSize = 3)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        var = []
        return var

    hierarchy = hierarchy[0]
    detect = []
    for i in range(len(contours)):
        k = i
        c = 0
        while hierarchy[k][2] != -1:
            k = hierarchy[k][2]
            c = c + 1
        if hierarchy[k][2] != -1:
            c = c + 1
        if c >= 5:
            detect.append(i)
    if len(detect)<3:
        var = []
        return var
    else:
        con_all = []
        for i in detect:
            c = contours[i]
            for sublist in c:
                for p in sublist:
                    con_all.append(p)
        con_all = np.asarray(con_all)
        rect = cv2.minAreaRect(con_all)
        box = cv2.cv.BoxPoints(rect)
        box = np.array(box)
        box = np.int32([box])
        box = box[0]
        crop_im = img_gb[min([i[1] for i in box]):(max([i[1] for i in box])+1),min([i[0] for i in box]):(max([i[0] for i in box])+1)]
        crimg_gb = cv2.GaussianBlur(crop_im, (5,5), 0)
        cr_gb = cv2.GaussianBlur(crimg_gb, (5,5), 0)

        rows,cols = crop_im.shape[:2]
        zbar_image = zbar.Image(cols, rows, 'Y800', str(cr_gb.data))
        scanner.scan(zbar_image)
        var = []
        for symbol in zbar_image:
            for lst in symbol.data.split(","):
                var.append(lst)
        return var

def ID2str(id):
    if len(id)<2:
        id = "0"+id
    id_all = ["03","04","07","08","09","10","11","15","16","19","20","21","22","23","24","26","28","34","37","39","42","43","45","46","51","52","53", "61", "62", "81", "82", "83", "84"]
    or_name = [u'\u5ca9\u624b\u770c', u'\u5bae\u57ce\u770c', u'\u798f\u5cf6\u770c', u'\u8328\u57ce\u770c', u'\u6803\u6728\u770c', u'\u7fa4\u99ac\u770c', u'\u57fc\u7389\u770c', u'\u65b0\u6f5f\u770c', 
    u'\u5bcc\u5c71\u770c', u'\u5c71\u68a8\u770c', u'\u9577\u91ce\u770c', u'\u5c90\u961c\u770c', u'\u9759\u5ca1\u770c', u'\u611b\u77e5\u770c', u'\u4e09\u91cd\u770c', u'\u4eac\u90fd\u5e9c', u'\u5175\u5eab\u770c',
    u'\u5e83\u5cf6\u770c', u'\u9999\u5ddd\u770c', u'\u9ad8\u77e5\u770c', u'\u9577\u5d0e\u770c', u'\u8fb2\u7814\u6a5f\u69cb\u4e5d\u6c96\u7814', u'\u5bae\u5d0e\u770c', u'\u9e7f\u5150\u5cf6\u770c', 
    u'\u8fb2\u7814\u6a5f\u69cb\u4e2d\u592e\u8fb2\u7814', u'\u8fb2\u7814\u6a5f\u69cb\u91ce\u83dc\u82b1\u304d', u'\u8fb2\u7814\u6a5f\u69cb\u8fb2\u74b0\u7814', u'\u6cd5\u653f\u5927\u5b66', 
    u'\u540d\u53e4\u5c4b\u5927\u5b66', u'\u30ce\u30fc\u30b6\u30f3\u30b7\u30b9\u30c6\u30e0\u30b5\u30fc\u30d3\u30b9', u'\u65e5\u672c\u8fb2\u85ac', u'\u004e\u0054\u0054\u30c7\u30fc\u30bf', u'\u004e\u0054\u0054\u30c7\u30fc\u30bf\u0043\u0043\u0053']
    for i,x in enumerate(id_all):
        if x == id:
            return or_name[i]


try:
    pyexiv2.xmp.register_namespace("http://ai-pest.jp/aipest/1.1/", "ai-pest")
except KeyError:
    pass


# indir = os.getcwd()
indir = "../image" # change indir


for pic in sorted(os.listdir(indir), key=lambda x:x.lower()):
    if not pic.endswith (".jpg") and not pic.endswith (".JPG") and not pic.endswith (".png") and not pic.endswith (".PNG"):
        continue
    else:
        picpath = indir +"/" + pic
        im = cv2.imread(picpath)
        tmptag = decodeQR(im)
        if tmptag != []:
            print "QR code: ",pic
            tag = []
            var = tmptag
            tag = [i.decode("utf-8") for i in tmptag]
            try:
                tag =  [i.decode("utf-8").encode("shift-jis").decode("utf-8") for i in tmptag]
            except UnicodeDecodeError:
                pass
        elif not pic.endswith (".jpg") and not pic.endswith (".JPG"):
            continue
        else:
            metadata = pyexiv2.ImageMetadata(picpath)
            metadata.read()
            pestxmp = "Xmp.ai-pest."

            # Exif からの読み取りと反映
            model=""
            photodate=""
            for k in metadata.exif_keys:
                if k =="Exif.Image.Model":
                    value = metadata[k]
                    model =  value.value 
                if k== "Exif.Image.DateTime":
                    value = metadata[k]
                    date = value.value
                    photodate = date.strftime("%Y:%m:%d %H:%M:%S")
            
            # オリジナルのファイル名を入れる
            metadata[pestxmp + "fileNameOrg"] =str(pic)

            if ("Exif.GPSInfo.GPSLatitude" in metadata.exif_keys) and ("Exif.GPSInfo.GPSLongitude"  in metadata.exif_keys):
                lat = metadata["Exif.GPSInfo.GPSLatitude"].value
                lon = metadata["Exif.GPSInfo.GPSLongitude"].value
                tag[0] = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600
                tag[1] = float(lon[0]) + float(lon[1])/60 + float(lon[2])/3600
                # GPS情報がExifに存在するので、Xmpには追加しない
                print "no"
            else:
                metadata[pestxmp + "gpsLatitude"] = pyexiv2.XmpTag(pestxmp + "gpsLatitude",str(tag[0]))
                metadata[pestxmp + "gpsLongitude"] = pyexiv2.XmpTag(pestxmp + "gpsLongitude",str(tag[1]))

            metadata[pestxmp + "cropName"] = pyexiv2.XmpTag(pestxmp + "cropName" ,str(tag[2]))
            if len(str(tag[3]))<2:
                tag[3] = "0"+str(tag[3])
            metadata[pestxmp + "examinationOrganization"] = str(tag[3])
            metadata[pestxmp + "examinationID"] = str(tag[4])
            metadata[pestxmp + "examinationEnvironment"] = str(tag[5])
            metadata[pestxmp + "shootingPart"] = tag[6]

            for i in xrange((len(tag)-7)//6):
                metadata[pestxmp+"pestDiseaseClassification"+str(i+1)] = str(tag[7+i*6])
                metadata[pestxmp+"pestDiseaseName"+str(i+1)] = tag[8+i*6]
                metadata[pestxmp+"pestDiseaseIdentification"+str(i+1)] = str(tag[9+i*6])
                metadata[pestxmp+"cropDamageLevel"+str(i+1)] = str(tag[10+i*6])
                metadata[pestxmp+"pestBoddyPresence"+str(i+1)] = str(tag[11+i*6])
                metadata[pestxmp+"pestBoddyClassification"+str(i+1)] = str(tag[12+i*6])

            metadata[pestxmp+"copyright"]  = ID2str(str(tag[3]))
            metadata[pestxmp+"license"]    = "CC BY 4.0"
            metadata[pestxmp+"licenseURL"] = "https://creativecommons.org/licenses/by/4.0/deed.ja"
            
            isPublicIndex = 7 + 6*((len(tag)-7)//6)  # pestsの直後のisPublic要素の配列の位置を算出
            if (isPublicIndex < len(tag)):
                # isPublic要素がある（=新しい仕様のQRコード）ので、その値を指定
                metadata[pestxmp+"isPublic"] = str(tag[isPublicIndex])
            else:
                # isPublic要素がない（=以前の仕様のQRコード）のでデフォルト値を指定
                metadata[pestxmp+"isPublic"] = "true"
            
            #XMP書き込み
            metadata.write()
            print "write XMP tag: ",pic

# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ChangeFilename
# Purpose:
#  jpeg画像中のメタデータを用いて、DB登録用のメタデータCSVを生成するとともに、
#  画像ファイルのファイル名を変更します。
#
# Created:     12/01/2018
# Updated:     2020/3/6
#-------------------------------------------------------------------------------


import os
import os.path
import pyexiv2
import csv
import codecs
from PIL import Image
import numpy as np
import datetime
import sys
import atexit

# 終了処理の追加
def goodbye():
    """
    終了処理
    """
    raw_input( u"Enter key")
 
atexit.register( goodbye )

reload(sys)
sys.setdefaultencoding("utf-8")


def ID2str(id):
    if len(id)<2:
        id = "0"+id
    id_all = ["03","04","07","08","09","10","11","15","16","19","20","21","22","23","24","26","28","34","37","39","42","43","45","46","51","52","53","61","62","81","82","83","84"]
    or_name = [u'\u5ca9\u624b\u770c', u'\u5bae\u57ce\u770c', u'\u798f\u5cf6\u770c', u'\u8328\u57ce\u770c', u'\u6803\u6728\u770c', u'\u7fa4\u99ac\u770c', u'\u57fc\u7389\u770c', u'\u65b0\u6f5f\u770c', 
    u'\u5bcc\u5c71\u770c', u'\u5c71\u68a8\u770c', u'\u9577\u91ce\u770c', u'\u5c90\u961c\u770c', u'\u9759\u5ca1\u770c', u'\u611b\u77e5\u770c', u'\u4e09\u91cd\u770c', u'\u4eac\u90fd\u5e9c', u'\u5175\u5eab\u770c',
    u'\u5e83\u5cf6\u770c', u'\u9999\u5ddd\u770c', u'\u9ad8\u77e5\u770c', u'\u9577\u5d0e\u770c', u'\u8fb2\u7814\u6a5f\u69cb\u4e5d\u6c96\u7814', u'\u5bae\u5d0e\u770c', u'\u9e7f\u5150\u5cf6\u770c', 
    u'\u8fb2\u7814\u6a5f\u69cb\u4e2d\u592e\u8fb2\u7814', u'\u8fb2\u7814\u6a5f\u69cb\u91ce\u83dc\u82b1\u304d', u'\u8fb2\u7814\u6a5f\u69cb\u8fb2\u74b0\u7814', u'\u6cd5\u653f\u5927\u5b66', 
    u'\u540d\u53e4\u5c4b\u5927\u5b66', u'\u30ce\u30fc\u30b6\u30f3\u30b7\u30b9\u30c6\u30e0\u30b5\u30fc\u30d3\u30b9', u'\u65e5\u672c\u8fb2\u85ac', u'\u004e\u0054\u0054\u30c7\u30fc\u30bf', u'\u004e\u0054\u0054\u30c7\u30fc\u30bf\u0043\u0043\u0053']
    for i,x in enumerate(id_all):
        if x == id:
            return or_name[i]

# XMPメタデータのプロパティ名のうち、
# tagKey配列に与えられたキーに一致するプロパティ名を返す関数です。
def getMatchedMetaKey(metaxmpkeys, xmpkey, tagKeys):
    for tagKey in tagKeys:
        fullKey = xmpkey + tagKey
        for k in metaxmpkeys:
            if fullKey == k:
                return fullKey

# indir = os.getcwd()
indir = "../image" # change indir
outcsv = indir +"/metadata.csv"
outf = open(outcsv,"wb")
writer = csv.writer(outf,delimiter  = ",")
database = []
name = ["FileName","Model","CreateDate","GPSLatitude","GPSLongitude","CropName","ExaminationOrganization","ExaminationID","ExaminationEnvironment","ShootingPart",\
"PestDiseaseClassification1","PestDiseaseName1","PestDiseaseIdentification1","CropDamageLevel1","PestBoddyPresence1","PestBoddyClassification1",\
"PestDiseaseClassification2","PestDiseaseName2","PestDiseaseIdentification2","CropDamageLevel2","PestBoddyPresence2","PestBoddyClassification2",\
"PestDiseaseClassification3","PestDiseaseName3","PestDiseaseIdentification3","CropDamageLevel3","PestBoddyPresence3","PestBoddyClassification3",\
"PestDiseaseClassification4","PestDiseaseName4","PestDiseaseIdentification4","CropDamageLevel4","PestBoddyPresence4","PestBoddyClassification4",\
"PestDiseaseClassification5","PestDiseaseName5","PestDiseaseIdentification5","CropDamageLevel5","PestBoddyPresence5","PestBoddyClassification5","Copyright","License","LicenseURL","IsPublic"]
database.append(["" for l in xrange(44)])
for n in xrange(44):
    database[0][n] = name[n]

xmpkey = "Xmp.ai-pest."
for root, dirs, files in sorted(os.walk(indir)):
    for file in files:
        if file.endswith(".jpg") or  file.endswith(".JPG"):
            picpath = root +"/"+ file
            data = [None]*44
            metadata = pyexiv2.ImageMetadata(picpath)
            metadata.read()
            for k in metadata.xmp_keys:
                if ("examinationID" in k) or ("ExaminationID" in k):
                    examid = metadata[k].value
                if ("examinationOrganization" in k) or ("ExaminationOrganization" in k):
                    exam = metadata[k].value
            for k in metadata.exif_keys:
                if k == "Exif.Image.DateTime":
                    value = metadata[k]
                    date = value.value
                    photodate = date.strftime("%Y%m%d%H%M%S")
                if k =="Exif.Image.Model":
                    value = metadata[k]
                    model =  value.value
            serialnumber = int(1) # 岩崎修正
            nameformat = examid +"_" +photodate + "_{:02d}.JPG"
            while True:
                namechange = nameformat.format(serialnumber)
                outpath = os.path.join(root, namechange)
                if os.path.exists(outpath):
                    serialnumber += 1
                    continue
                elif serialnumber >= 99:
                    raise IOError("File \"{}\" already exists. Serial number reached at 99.".format(namechange))
                else:
                    break
            serialnumber = int(1) # 岩崎追加
            copyright = ID2str(str(exam))
            license = "CC BY 4.0"
            licenseurl = "https://creativecommons.org/licenses/by/4.0/deed.ja"
            isPublic = "true"
            # copyright,license,licenseurl,isPublic については、XMPに値があれば読み取る
            for k in metadata.xmp_keys:
                if (k == xmpkey + "copyright") or (k == xmpkey + "Copyright"):
                    copyright = metadata[k].value
                if (k == xmpkey + "license") or (k == xmpkey + "License"):
                    license = metadata[k].value
                if (k == xmpkey + "licenseURL") or (k == xmpkey + "LicenseURL"):
                    licenseurl = metadata[k].value
                if k == xmpkey + "isPublic":
                    isPublic = metadata[k].value

            data[0] = namechange
            data[1] = model
            data[2] = date.strftime("%Y:%m:%d %H:%M:%S")
            #xmpkey = "Xmp.ai-pest."
            if ('Exif.GPSInfo.GPSLatitude' in metadata.exif_keys) and ('Exif.GPSInfo.GPSLongitude' in metadata.exif_keys):
                lat = metadata['Exif.GPSInfo.GPSLatitude'].value
                lon = metadata['Exif.GPSInfo.GPSLongitude'].value
                data[3] = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600
                data[4] = float(lon[0]) + float(lon[1])/60 + float(lon[2])/3600
            else:
                data[3] = metadata[getMatchedMetaKey(metadata.xmp_keys, xmpkey, ["gpsLatitude", "GPSLatitude"])].value
                data[4] = metadata[getMatchedMetaKey(metadata.xmp_keys, xmpkey, ["gpsLongitude", "GPSLongitude"])].value
            data[5] = metadata[getMatchedMetaKey(metadata.xmp_keys, xmpkey, ["cropName", "CropName"])].value
            data[6] = metadata[getMatchedMetaKey(metadata.xmp_keys, xmpkey, ["examinationOrganization", "ExaminationOrganization"])].value
            data[7] = metadata[getMatchedMetaKey(metadata.xmp_keys, xmpkey, ["examinationID", "ExaminationID"])].value
            data[8] = metadata[getMatchedMetaKey(metadata.xmp_keys, xmpkey, ["examinationEnvironment", "ExaminationEnvironment"])].value
            data[9] = (metadata[getMatchedMetaKey(metadata.xmp_keys, xmpkey, ["shootingPart", "ShootingPart"])].value).decode("utf-8")


            for k in metadata.xmp_keys:
                if ("pestDiseaseClassification" in k) or ("PestDiseaseClassification" in k):
                    count = int(k[-1])
                    data[10 + (count-1)*6] = metadata[k].value
                if ("pestDiseaseName" in k) or ("PestDiseaseName" in k):
                    count = int(k[-1])
                    data[11 + (count-1)*6] = (metadata[k].value).decode("utf-8")
                if ("pestDiseaseIdentification" in k) or ("PestDiseaseIdentification" in k):
                    count = int(k[-1])
                    data[12 + (count-1)*6] = metadata[k].value
                if ("cropDamageLevel" in k) or ("CropDamageLevel" in k):
                    count = int(k[-1])
                    data[13 + (count-1)*6] = metadata[k].value
                if ("pestBoddyPresence" in k) or ("PestBoddyPresence" in k):
                    count = int(k[-1])
                    data[14 + (count-1)*6] = metadata[k].value
                if ("pestBoddyClassification" in k) or ("PestBoddyClassification" in k):
                    count = int(k[-1])
                    data[15 + (count-1)*6] = metadata[k].value
            data[40:44]=[copyright,license,licenseurl,isPublic]
            database.append(["" for l in xrange(44)])
            num = len(database)-1
            database[num][:] = data

            os.rename(picpath , outpath)
            print "Change file name from ",picpath ,"to", outpath

for t in database:
    writer.writerow([u"{}".format(s).encode("utf-8") if s != None else None for s in t ])
outf.close()

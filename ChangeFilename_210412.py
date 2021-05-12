# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ChangeFilename
# Purpose:
#  jpeg画像中のメタデータを用いて、DB登録用のメタデータCSVを生成するとともに、
#  画像ファイルのファイル名を変更します。
#
# Created:     12/01/2018
# Updated:     2021/3/5
#-------------------------------------------------------------------------------


import os
import os.path
import pyexiv2
import csv
import codecs
import datetime
import sys
import atexit

# 終了処理の追加
def goodbye():
    """
    終了処理
    """
    #raw_input( u"Enter key")
 
atexit.register( goodbye )



def ID2str(id):
    if len(id)<2:
        id = "0"+id
    id_all = ["03","04","07","08","09","10","11","15","16","19","20","21","22","23","24","26","28","34","37","39","42","43","45","46","51","52","53","61","62","81","82","83","84"]
    or_name = ['\u5ca9\u624b\u770c', '\u5bae\u57ce\u770c', '\u798f\u5cf6\u770c', '\u8328\u57ce\u770c', '\u6803\u6728\u770c', '\u7fa4\u99ac\u770c', '\u57fc\u7389\u770c', '\u65b0\u6f5f\u770c', 
    '\u5bcc\u5c71\u770c', '\u5c71\u68a8\u770c', '\u9577\u91ce\u770c', '\u5c90\u961c\u770c', '\u9759\u5ca1\u770c', '\u611b\u77e5\u770c', '\u4e09\u91cd\u770c', '\u4eac\u90fd\u5e9c', '\u5175\u5eab\u770c',
    '\u5e83\u5cf6\u770c', '\u9999\u5ddd\u770c', '\u9ad8\u77e5\u770c', '\u9577\u5d0e\u770c', '\u8fb2\u7814\u6a5f\u69cb\u4e5d\u6c96\u7814', '\u5bae\u57ce\u770c', '\u9e7f\u5150\u5cf6\u770c', 
    '\u8fb2\u7814\u6a5f\u69cb\u4e2d\u592e\u8fb2\u7814', '\u8fb2\u7814\u6a5f\u69cb\u91ce\u83dc\u82b1\u304d', '\u8fb2\u7814\u6a5f\u69cb\u8fb2\u74b0\u7814', '\u6cd5\u653f\u5927\u5b66', 
    '\u540d\u53e4\u5c4b\u5927\u5b66', '\u30ce\u30fc\u30b6\u30f3\u30b7\u30b9\u30c6\u30e0\u30b5\u30fc\u30d3\u30b9', '\u65e5\u672c\u8fb2\u85ac', '\u004e\u0054\u0054\u30c7\u30fc\u30bf', '\u004e\u0054\u0054\u30c7\u30fc\u30bf\u0043\u0043\u0053']
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


def dms2d(dms):
    (d, m, s) = dms.split(' ')
    dv, t = d.split('/')
    mv, t = d.split('/')
    sv, t = d.split('/')
    return float(dv) + float(mv)/60 + float(sv)/3600

indir = "../image" # indir = os.getcwd() ; # Furuyashiki
outcsv = indir +"/metadata.csv"
outf = open(outcsv,"w",encoding="utf-8",newline="") 
writer = csv.writer(outf,delimiter  = ",")
database = []
name = ["FileName","Model","CreateDate","GPSLatitude","GPSLongitude","CropName","ExaminationOrganization","ExaminationID","ExaminationEnvironment","ShootingPart",\
"PestDiseaseClassification1","PestDiseaseName1","PestDiseaseId1","PestDiseaseIdentification1","CropDamageLevel1","PestBoddyPresence1","PestBoddyClassification1",\
"PestDiseaseClassification2","PestDiseaseName2","PestDiseaseId2","PestDiseaseIdentification2","CropDamageLevel2","PestBoddyPresence2","PestBoddyClassification2",\
"PestDiseaseClassification3","PestDiseaseName3","PestDiseaseId3","PestDiseaseIdentification3","CropDamageLevel3","PestBoddyPresence3","PestBoddyClassification3",\
"PestDiseaseClassification4","PestDiseaseName4","PestDiseaseId4","PestDiseaseIdentification4","CropDamageLevel4","PestBoddyPresence4","PestBoddyClassification4",\
"PestDiseaseClassification5","PestDiseaseName5","PestDiseaseId5","PestDiseaseIdentification5","CropDamageLevel5","PestBoddyPresence5","PestBoddyClassification5","Copyright","License","LicenseURL","IsPublic"]
database.append(["" for l in range(49)])
for n in range(49):
    database[0][n] = name[n]

xmpkey = "Xmp.ai-pest."
for root, dirs, files in sorted(os.walk(indir)):
    for file in files:
        if file.endswith(".jpg") or  file.endswith(".JPG"):
            picpath = root +"/"+ file
            data = [None]*49
            img = pyexiv2.Image(picpath)
            exif_data = img.read_exif()
            metadata = img.read_xmp()

            for k in metadata:
                if ("Xmp.ai-pest.examinationID" in k) or ("Xmp.ai-pest.ExaminationID" in k):
                    examid = metadata[k]
                if ("Xmp.ai-pest.examinationOrganization" in k) or ("Xmp.ai-pest.ExaminationOrganization" in k):
                    exam = metadata[k]
            model="Unknown model"
            photodate=""
            for k in exif_data:
                if k =="Exif.Image.Model":
                    value = exif_data[k]
                    model =  value 
                if k== "Exif.Image.DateTime":
                    value = exif_data[k]
                    date = value
                    tdatetime = datetime.datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
                    photodate = tdatetime.strftime("%Y%m%d%H%M%S")
            if len(photodate)==0:
                k = 'Exif.Image.DateTimeOriginal'
                if k in exif_data:
                    value = exif_data[k]
                    date = value
                    tdatetime = datetime.datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
                    photodate = tdatetime.strftime("%Y%m%d%H%M%S")
            if len(photodate)==0:
                k = 'Exif.Photo.DateTimeOriginal'
                if k in exif_data:
                    value = exif_data[k]
                    date = value
                    tdatetime = datetime.datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
                    photodate = tdatetime.strftime("%Y%m%d%H%M%S")
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
            for k in metadata:
                if (k == xmpkey + "copyright") or (k == xmpkey + "Copyright"):
                    copyright = metadata[k]
                if (k == xmpkey + "license") or (k == xmpkey + "License"):
                    license = metadata[k]
                if (k == xmpkey + "licenseURL") or (k == xmpkey + "LicenseURL"):
                    licenseurl = metadata[k]
                if k == xmpkey + "isPublic":
                    isPublic = metadata[k]
                    isPublic = ''.join(str(isPublic).splitlines())

            data[0] = namechange
            data[1] = model
            data[2] = date
            #data[2] = date.strftime("%Y:%m:%d %H:%M:%S")
            #xmpkey = "Xmp.ai-pest."
            if ('Exif.GPSInfo.GPSLatitude' in exif_data) and ('Exif.GPSInfo.GPSLongitude' in exif_data):
                lat = exif_data['Exif.GPSInfo.GPSLatitude']
                lon = exif_data['Exif.GPSInfo.GPSLongitude']
                data[3] = dms2d(lat)
                data[4] = dms2d(lon)
            else:
                data[3] = metadata[getMatchedMetaKey(metadata, xmpkey, ["gpsLatitude", "GPSLatitude"])] 
                data[4] = metadata[getMatchedMetaKey(metadata, xmpkey, ["gpsLongitude", "GPSLongitude"])]
            data[5] = metadata[getMatchedMetaKey(metadata, xmpkey, ["cropName", "CropName"])] 
            data[6] = metadata[getMatchedMetaKey(metadata, xmpkey, ["examinationOrganization", "ExaminationOrganization"])]
            data[7] = metadata[getMatchedMetaKey(metadata, xmpkey, ["examinationID", "ExaminationID"])]
            data[8] = metadata[getMatchedMetaKey(metadata, xmpkey, ["examinationEnvironment", "ExaminationEnvironment"])]
            data[9] = metadata[getMatchedMetaKey(metadata, xmpkey, ["shootingPart", "ShootingPart"])]


            for k in metadata:
                if ("pestDiseaseClassification" in k) or ("PestDiseaseClassification" in k):
                    count = int(k[-1])
                    data[10 + (count-1)*7] = metadata[k]
                if ("pestDiseaseName" in k) or ("PestDiseaseName" in k):
                    count = int(k[-1])
                    data[11 + (count-1)*7] = metadata[k]
                if ("pestDiseaseID" in k) or ("PestDiseaseID" in k):
                    count = int(k[-1])
                    data[12 + (count-1)*7] = metadata[k]
                if ("pestDiseaseIdentification" in k) or ("PestDiseaseIdentification" in k):
                    count = int(k[-1])
                    data[13 + (count-1)*7] = metadata[k]
                if ("cropDamageLevel" in k) or ("CropDamageLevel" in k):
                    count = int(k[-1])
                    data[14 + (count-1)*7] = metadata[k]
                if ("pestBoddyPresence" in k) or ("PestBoddyPresence" in k):
                    count = int(k[-1])
                    data[15 + (count-1)*7] = metadata[k]
                if ("pestBoddyClassification" in k) or ("PestBoddyClassification" in k):
                    count = int(k[-1])
                    data[16 + (count-1)*7] = metadata[k]
            data[45:49]=[copyright,license,licenseurl,isPublic]
            database.append(["" for l in range(49)])
            num = len(database)-1
            database[num][:] = data

            os.rename(picpath , outpath)
            img.close()
            print("Change file name from ",picpath ,"to", outpath)

for t in database:
    writer.writerow([s if s != None else None for s in t ])
outf.close()

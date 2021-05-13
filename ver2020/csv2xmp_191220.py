# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        csvtoxmp
# Purpose:
#  utf8のCSVファイルで与えられるメタデータを、jpeg画像にXMPで反映します。
#
# Created:     13/02/2019
# Updated:     2019/12/20
#-------------------------------------------------------------------------------
import os
import os.path
import io
import pyexiv2
import csv
import sys
import pyexiv2.xmp
import numpy as np

reload(sys)  
sys.setdefaultencoding('utf-8')

try:
    pyexiv2.xmp.register_namespace("http://ai-pest.jp/aipest/1.1/", "ai-pest")
    print "register_namespace"
except KeyError:
    pass

try:
    csvFile =sys.argv[1]
except(IndexError) as e:
    print "Usage:" 
    print "       python csvtoxmp.py csvfile_name"
    sys.exit()
   


def ID2str(id):
    if len(id)<2:
        id = "0"+id
    id_all = ["03","04","07","08","09","10","11","15","16","19","20","21","22","23","24","26","28","34","37","39","42","43","45","46","51","52","53", "61", "62", "81", "82", "83", "84"]
    or_name = ["岩手県","宮城県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "新潟県", "富山県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "京都府", "兵庫県", "広島県", "香川県", "高知県", "長崎県", 
    "農研機構九沖研", "宮城県", "鹿児島県", "農研機構中央農研", "農研機構野菜花き", "農研機構農環研", "法政大学", "名古屋大学", "ノーザンシステムサービス", "日本農薬", "NTTデータ", "NTTデータCCS"]
    for i,x in enumerate(id_all):
        if x == id:
            return or_name[i]

indir = os.getcwd()
tag1=[]
try: 
    with open(csvFile) as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        for row in csvReader:
            tag1.append(row)
            
    
except(IOError,ValueError) as e:
    print "CSV file not found"
    sys.exit()



for pic in sorted(os.listdir(indir), key=lambda x:x.lower()):
    
    tag=tag1[0]
    if not pic.endswith (".jpg") and not pic.endswith (".JPG") and not pic.endswith (".png") and not pic.endswith (".PNG"):
        continue
    else:
        picpath = indir +"/" + pic
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
                
        metadata[pestxmp + "fileNameOrg"] =str(pic)          # オリジナルのファイル名を入れる
        #metadata[pestxmp + "model"] =str(model)             # 入れないこととなった
        #metadata[pestxmp + "createdDate"] =str(photodate)   # 入れないこととなった

        if ("Exif.GPSInfo.GPSLatitude" in metadata.exif_keys) and ("Exif.GPSInfo.GPSLongitude" in metadata.exif_keys):
            lat = metadata["Exif.GPSInfo.GPSLatitude"].value
            lon = metadata["Exif.GPSInfo.GPSLongitude"].value
            tag[0] = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600
            tag[1] = float(lon[0]) + float(lon[1])/60 + float(lon[2])/3600
            # GPS情報がExifに存在するので、Xmpには追加しない
        else:
            metadata[pestxmp + "gpsLatitude"] = pyexiv2.XmpTag(pestxmp + "gpsLatitude",str(tag[0]))
            metadata[pestxmp + "gpsLongitude"] = pyexiv2.XmpTag(pestxmp + "gpsLongitude",str(tag[1]))
            
        metadata[pestxmp + "cropName"] = pyexiv2.XmpTag(pestxmp + "cropName" ,str(tag[2]))
        if len(str(tag[3]))<2:
            tag[3] = "0"+str(tag[3])
        metadata[pestxmp + "examinationOrganization"] = str(tag[3])
        metadata[pestxmp + "examinationID"] = str(tag[4])
        metadata[pestxmp + "examinationEnvironment"] = str(tag[5])
        metadata[pestxmp + "shootingPart"] =str(tag[6])
        
        for i in xrange((len(tag)-7)//6):
            metadata[pestxmp+"pestDiseaseClassification"+str(i+1)] = str(tag[7+i*6])
            metadata[pestxmp+"pestDiseaseName"+str(i+1)] = str(tag[8+i*6])
            metadata[pestxmp+"pestDiseaseIdentification"+str(i+1)] = str(tag[9+i*6])
            metadata[pestxmp+"cropDamageLevel"+str(i+1)] = str(tag[10+i*6])
            metadata[pestxmp+"pestBoddyPresence"+str(i+1)] = str(tag[11+i*6])
            metadata[pestxmp+"pestBoddyClassification"+str(i+1)] = str(tag[12+i*6])
        
        metadata[pestxmp+"copyright"] = ID2str(str(tag[3]))
        metadata[pestxmp+"license"] = "CC BY 4.0"
        metadata[pestxmp+"licenseURL"] = "https://creativecommons.org/licenses/by/4.0/deed.ja"
        
        isPublicIndex = 7 + 6*((len(tag)-7)//6)  # pestsの直後のisPublic要素の配列の位置を算出
        if (isPublicIndex < len(tag)):
            # isPublic要素がある（=新しい仕様のcsv）ので、その値を指定
            metadata[pestxmp+"isPublic"] = str(tag[isPublicIndex])
        else:
            # isPublic要素がない（=以前の仕様のcsv）のでデフォルト値を指定
            metadata[pestxmp+"isPublic"] = "true"

        #XMP書き込み
        metadata.write()

        print "XMP successfuly written to "+pic

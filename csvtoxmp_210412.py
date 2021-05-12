# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        csvtoxmp
# Purpose:
#  utf8のCSVファイルで与えられるメタデータを、jpeg画像にXMPで反映します。
#
# Created:     13/02/2019
# Updated:     2021/3/5
#-------------------------------------------------------------------------------
import os
import os.path
import io
import pyexiv2
import csv
import sys
import subprocess

try:
    csvFile =sys.argv[1]
except(IndexError) as e:
    print("Usage:") 
    print("       python csvtoxmp.py csvfile_name")
    sys.exit()
   
# exiv2 command
EXIV2 = 'exiv2'

def registerNS(imgpath, img):
    reg_command = "reg ai-pest http://ai-pest.jp/aipest/1.1/"
    set_command = "set Xmp.ai-pest.fileNameOrg "+img+""

    optionargs = []
    args = [
        EXIV2,
        '-M', reg_command,
        '-M', set_command,
        imgpath
    ] + optionargs
    p = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False
        )
        
    stdout, stderr = p.communicate()
    if len(stderr) != 0:
        raise RuntimeError('EXIV2 threw error:\n' + stderr.decode('utf-8'))


def ID2str(id):
    if len(id)<2:
        id = "0"+id
    id_all = ["03","04","07","08","09","10","11","15","16","19","20","21","22","23","24","26","28","34","37","39","42","43","45","46","51","52","53", "61", "62", "81", "82", "83", "84"]
    or_name = ["岩手県","宮城県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "新潟県", "富山県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "京都府", "兵庫県", "広島県", "香川県", "高知県", "長崎県", 
    "農研機構九沖研", "宮崎県", "鹿児島県", "農研機構中央農研", "農研機構野菜花き", "農研機構農環研", "法政大学", "名古屋大学", "ノーザンシステムサービス", "日本農薬", "NTTデータ", "NTTデータCCS"]
    for i,x in enumerate(id_all):
        if x == id:
            return or_name[i]

def dms2d(dms):
    (d, m, s) = dms.split(' ')
    dv, t = d.split('/')
    mv, t = d.split('/')
    sv, t = d.split('/')
    return float(dv) + float(mv)/60 + float(sv)/3600

indir = "../image" ; # furuyashiki
#indir = os.getcwd() 
tag1=[]
try: 
    with open(csvFile,encoding="utf-8") as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        for row in csvReader:
            tag1.append(row)
            
    
except(IOError,ValueError) as e:
    print("CSV file not found")
    sys.exit()



for pic in sorted(os.listdir(indir), key=lambda x:x.lower()):
    
    tag=tag1[0]
    if not pic.endswith (".jpg") and not pic.endswith (".JPG") and not pic.endswith (".png") and not pic.endswith (".PNG"):
        continue
    else:
        picpath = indir +"/" + pic
        registerNS(picpath, pic)
        img = pyexiv2.Image(picpath)
        exif_data = img.read_exif()
        img.clear_xmp()
        metadata = img.read_xmp()
        pestxmp = "Xmp.ai-pest."

        # Exif からの読み取りと反映
        model=""
        photodate=""
        for k in exif_data:
            if k =="Exif.Image.Model":
                value = exif_data[k]
                model =  value 
            if k== "Exif.Image.DateTime":
                value = exif_data[k]
                date = value
                photodate = date
                #photodate = date.strftime("%Y:%m:%d %H:%M:%S")
                
        metadata[pestxmp + "fileNameOrg"] =str(pic)          # オリジナルのファイル名を入れる
        #metadata[pestxmp + "model"] =str(model)             # 入れないこととなった
        #metadata[pestxmp + "createdDate"] =str(photodate)   # 入れないこととなった

        if ("Exif.GPSInfo.GPSLatitude" in exif_data) and ("Exif.GPSInfo.GPSLongitude" in exif_data):
            lat = exif_data["Exif.GPSInfo.GPSLatitude"]
            lon = exif_data["Exif.GPSInfo.GPSLongitude"]
            tag[0] = dms2d(lat)
            tag[1] = dms2d(lon)
            # GPS情報がExifに存在するので、Xmpには追加しない
        else:
            metadata[pestxmp + "gpsLatitude"] = str(tag[0])
            metadata[pestxmp + "gpsLongitude"] = str(tag[1])
            
        metadata[pestxmp + "cropName"] = str(tag[2])
        if len(str(tag[3]))<2:
            tag[3] = "0"+str(tag[3])
        metadata[pestxmp + "examinationOrganization"] = str(tag[3])
        metadata[pestxmp + "examinationID"] = str(tag[4])
        metadata[pestxmp + "examinationEnvironment"] = str(tag[5])
        metadata[pestxmp + "shootingPart"] =str(tag[6])
        
        # 病虫害IDの有無を判定
        if len(str(tag[9]))==1 and str(tag[9]).isdecimal():
            ### 病虫害IDなし
            for i in range((len(tag)-7)//6):
                metadata[pestxmp+"pestDiseaseClassification"+str(i+1)] = str(tag[7+i*6])
                metadata[pestxmp+"pestDiseaseName"+str(i+1)] = tag[8+i*6]
                metadata[pestxmp+"pestDiseaseIdentification"+str(i+1)] = str(tag[9+i*6])
                metadata[pestxmp+"cropDamageLevel"+str(i+1)] = str(tag[10+i*6])
                metadata[pestxmp+"pestBoddyPresence"+str(i+1)] = str(tag[11+i*6])
                metadata[pestxmp+"pestBoddyClassification"+str(i+1)] = str(tag[12+i*6])

            # pestsの直後のisPublic要素の配列の位置を算出
            isPublicIndex = 7 + 6*((len(tag)-7)//6)

        else:
            ### 病虫害IDあり

            for i in range((len(tag)-7)//7):
     
                metadata[pestxmp+"pestDiseaseClassification"+str(i+1)] = str(tag[7+i*7])
                metadata[pestxmp+"pestDiseaseName"+str(i+1)] = tag[8+i*7]
                metadata[pestxmp+"pestDiseaseID"+str(i+1)] = tag[9+i*7]
                metadata[pestxmp+"pestDiseaseIdentification"+str(i+1)] = str(tag[10+i*7])
                metadata[pestxmp+"cropDamageLevel"+str(i+1)] = str(tag[11+i*7])
                metadata[pestxmp+"pestBoddyPresence"+str(i+1)] = str(tag[12+i*7])
                metadata[pestxmp+"pestBoddyClassification"+str(i+1)] = str(tag[13+i*7])

            # pestsの直後のisPublic要素の配列の位置を算出
            isPublicIndex = 7 + 7*((len(tag)-7)//7)

        metadata[pestxmp+"copyright"] = ID2str(str(tag[3]))
        metadata[pestxmp+"license"] = "CC BY 4.0"
        metadata[pestxmp+"licenseURL"] = "https://creativecommons.org/licenses/by/4.0/deed.ja"
        
        #isPublicIndex = 7 + 6*((len(tag)-7)//6)  # pestsの直後のisPublic要素の配列の位置を算出
        if (isPublicIndex < len(tag)):
            # isPublic要素がある（=新しい仕様のcsv）ので、その値を指定
            metadata[pestxmp+"isPublic"] = str(tag[isPublicIndex])
        else:
            # isPublic要素がない（=以前の仕様のcsv）のでデフォルト値を指定
            metadata[pestxmp+"isPublic"] = "true"

        #XMP書き込み
        img.modify_xmp(metadata)
        img.close()

        print("XMP successfuly written to "+pic)

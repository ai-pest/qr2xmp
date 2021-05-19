# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        AddExifTag
# Purpose:
#  QRコード画像に収めたメタデータを、jpeg画像にXMPで反映します。
# 
# Created:     11/01/2018
# Updated:     2021/5/20
#-------------------------------------------------------------------------------
import os
import os.path
import pyexiv2
import csv
import codecs
import datetime
import atexit
import subprocess

# 終了処理の追加
def goodbye():
    """
    終了処理
    """
    #raw_input( u"Enter key")
 
atexit.register( goodbye )

# zbar command
ZBARIMG = 'zbarimg'

def readQR(img):
    optionargs = []
    
    args = [
        ZBARIMG,
         '-q', img
    ] + optionargs
    
    p = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False
        )
        
    stdout, stderr = p.communicate()
    if len(stderr) == 0:
        bindata = stdout
    else:
        raise RuntimeError('ZBar threw error:\n' + stderr.decode('utf-8'))
    
    data = None
    if (0 < len(bindata)):
        type, v = bindata.split(b":", 1)
        data = v.decode("utf-8")
        data.replace( '\n' , '' )
        data.replace( '\r' , '' )

    return data

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
        print('EXIV2 threw error:\n' + stderr.decode('utf-8'))
        #raise RuntimeError('EXIV2 threw error:\n' + stderr.decode('utf-8'))
    

def ID2str(id):
    if len(id)<2:
        id = "0"+id
    id_all = ["03","04","07","08","09","10","11","15","16","19","20","21","22","23","24","26","28","34","37","39","42","43","45","46","51","52","53", "61", "62", "81", "82", "83", "84"]
    or_name = ['\u5ca9\u624b\u770c', '\u5bae\u57ce\u770c', '\u798f\u5cf6\u770c', '\u8328\u57ce\u770c', '\u6803\u6728\u770c', '\u7fa4\u99ac\u770c', '\u57fc\u7389\u770c', '\u65b0\u6f5f\u770c', 
    '\u5bcc\u5c71\u770c', '\u5c71\u68a8\u770c', '\u9577\u91ce\u770c', '\u5c90\u961c\u770c', '\u9759\u5ca1\u770c', '\u611b\u77e5\u770c', '\u4e09\u91cd\u770c', '\u4eac\u90fd\u5e9c', '\u5175\u5eab\u770c',
    '\u5e83\u5cf6\u770c', '\u9999\u5ddd\u770c', '\u9ad8\u77e5\u770c', '\u9577\u5d0e\u770c', '\u8fb2\u7814\u6a5f\u69cb\u4e5d\u6c96\u7814', '\u5bae\u57ce\u770c', '\u9e7f\u5150\u5cf6\u770c', 
    '\u8fb2\u7814\u6a5f\u69cb\u4e2d\u592e\u8fb2\u7814', '\u8fb2\u7814\u6a5f\u69cb\u91ce\u83dc\u82b1\u304d', '\u8fb2\u7814\u6a5f\u69cb\u8fb2\u74b0\u7814', '\u6cd5\u653f\u5927\u5b66', 
    '\u540d\u53e4\u5c4b\u5927\u5b66', '\u30ce\u30fc\u30b6\u30f3\u30b7\u30b9\u30c6\u30e0\u30b5\u30fc\u30d3\u30b9', '\u65e5\u672c\u8fb2\u85ac', '\u004e\u0054\u0054\u30c7\u30fc\u30bf', '\u004e\u0054\u0054\u30c7\u30fc\u30bf\u0043\u0043\u0053']
    for i,x in enumerate(id_all):
        if x == id:
            return or_name[i]

def dms2d(dms):
    (d, m, s) = dms.split(' ')
    dv, t = d.split('/')
    mv, t = d.split('/')
    sv, t = d.split('/')
    return float(dv) + float(mv)/60 + float(sv)/3600


#indir = os.getcwd()
indir = "../image" # change indir


for pic in sorted(os.listdir(indir), key=lambda x:x.lower()):
    if not pic.endswith (".jpg") and not pic.endswith (".JPG") and not pic.endswith (".png") and not pic.endswith (".PNG"):
        continue
    else:
        picpath = indir +"/" + pic
        code = readQR(picpath)
        if code != None:
            print("QR code: ",pic)
            tag = code.split(",")
            tag = [i.replace( '\r\n' , '' ) for i in tag]
            tag = [i.replace( '\n' , '' ) for i in tag]
            # try:
            #     tag =  [i.decode("utf-8").encode("shift-jis").decode("utf-8") for i in tmptag]
            # except UnicodeDecodeError:
            #     pass
        elif not pic.endswith (".jpg") and not pic.endswith (".JPG"):
            continue
        else:
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

            # オリジナルのファイル名を入れる
            metadata[pestxmp + "fileNameOrg"] =str(pic)

            if ("Exif.GPSInfo.GPSLatitude" in exif_data) and ("Exif.GPSInfo.GPSLongitude"  in exif_data):
                lat = exif_data["Exif.GPSInfo.GPSLatitude"]
                lon = exif_data["Exif.GPSInfo.GPSLongitude"]
                tag[0] = dms2d(lat)
                tag[1] = dms2d(lon)
                # GPS情報がExifに存在するので、Xmpには追加しない
                print("no")
            else:
                metadata[pestxmp + "gpsLatitude"] = str(tag[0])
                metadata[pestxmp + "gpsLongitude"] = str(tag[1])

            metadata[pestxmp + "cropName"] = str(tag[2])
            if len(str(tag[3]))<2:
                tag[3] = "0"+str(tag[3])
            metadata[pestxmp + "examinationOrganization"] = str(tag[3])
            metadata[pestxmp + "examinationID"] = str(tag[4])
            metadata[pestxmp + "examinationEnvironment"] = str(tag[5])
            metadata[pestxmp + "shootingPart"] = tag[6]

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

            metadata[pestxmp+"copyright"]  = ID2str(str(tag[3]))
            metadata[pestxmp+"license"]    = "CC BY 4.0"
            metadata[pestxmp+"licenseURL"] = "https://creativecommons.org/licenses/by/4.0/deed.ja"
            
            #isPublicIndex = 7 + 6*((len(tag)-7)//6)  # pestsの直後のisPublic要素の配列の位置を算出
            if (isPublicIndex < len(tag)):
                # isPublic要素がある（=新しい仕様のQRコード）ので、その値を指定
                metadata[pestxmp+"isPublic"] = str(tag[isPublicIndex])
            else:
                # isPublic要素がない（=以前の仕様のQRコード）のでデフォルト値を指定
                metadata[pestxmp+"isPublic"] = "true"
            
            #XMP書き込み
            img.modify_xmp(metadata)
            img.close()
            print("write XMP tag: ",pic)

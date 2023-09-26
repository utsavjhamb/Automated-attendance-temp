import cv2
import face_recognition
import os
from pymongo import MongoClient

connection = 'mongodb://localhost:27017/'
client = MongoClient(connection)
database = 'AttendanceSystem'; collection = 'deepface'
db = client[database]
dbnames = db.list_collection_names()

if collection in dbnames:
    db.drop_collection(collection)

folderPath = 'deepface\images'
pathList = os.listdir(folderPath)
# print(pathList)

imgList = []
studentIds = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentIds.append(os.path.splitext(path)[0])

# print(imgList)
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

# print("encoding started ...")
embeddings = findEncodings(imgList)
# print("encoding complete")

for studentId,embedding in zip(studentIds,embeddings):
    db[collection].insert_one({"studentId": studentId, "embedding" : embedding.tolist()})

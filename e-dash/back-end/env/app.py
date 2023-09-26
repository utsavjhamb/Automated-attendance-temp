from flask import Flask, request
from flask_cors import CORS
import base64
from flask import Flask,render_template, Response, redirect, send_file
import cv2
import face_recognition
import numpy as np
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import csv
app=Flask(__name__)
CORS(app)

connection = 'mongodb://localhost:27017/'
client = MongoClient(connection)
database = 'AttendanceSystem'; collection = 'deepface'; collection2 = 'attendances' ; collection3 = 'students' ; collection4 = 'schedules'
db = client[database]

#load the encoding file
studentIds = []
embeddings = []
for x in db[collection].find():
    studentIds.append(x['studentId'])
    embeddings.append(x['embedding'])

def gen_frames():  
    cam = cv2.VideoCapture("rtsp://172.16.72.2")
    # cam = cv2.VideoCapture(0)

    while True:
        success, frame = cam.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

# classId = {'64895de338e66355b2e9448c'}
@app.route('/webcam/<classId>')
def index(classId):
    data = []
    data.append(classId)
    return render_template('index.html', data = data)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api',methods = ['get','post'])
def api():
    present = []
    data = request.get_json()
    result = data['data']
    b = bytes(result,'utf-8')
    image = b[b.find(b'/9'):]
    img = cv2.imdecode(np.frombuffer(base64.b64decode(image), dtype=np.uint8) , flags=cv2.IMREAD_COLOR)

    faceCurFrame = face_recognition.face_locations(img)
    encodeCurFrame = face_recognition.face_encodings(img,faceCurFrame)
    print("enc", len(encodeCurFrame))
    today = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().hour
    if faceCurFrame:
        for encodeFace in encodeCurFrame:
            matches = face_recognition.compare_faces(embeddings,encodeFace)#
            faceDist = face_recognition.face_distance(embeddings,encodeFace)#
            matchIndex = np.argmin(faceDist)
            if matches[matchIndex]:
                id = studentIds[matchIndex]
                
                student = db[collection3].find({"classId":data['classId'],"studentId":id})
                check = list(student)
                if len(check)!=0:
                    myquery = { "classId": data['classId'], "studentId":id, "attendanceDate": today, "attendanceTime": "{}:00 - {}:00".format(time,time+1) }#####
                    last_date = db[collection2].find_one(myquery)
                    if last_date is not None:
                        print("already marked")
                    else:
                        db[collection2].insert_one(myquery)
            else:
                print('no match')
    else:
        print("face not captured")     
        
    myquery = { "classId": data['classId']}
    query2 = {"classId": data['classId'], "attendanceDate": today, "attendanceTime": "{}:00 - {}:00".format(time,time+1)}
    for x in db[collection2].find(query2):
        present.append(x['studentId'])

    absentees = []
    for x in db[collection3].find(myquery,{"name":0,"_id":0,"classId":0,'__v':0}):
        if x['studentId'] not in present:
            absentees.append(x['studentId'])

    return {"absentees":absentees, "attendanceTime": "{}:00 - {}:00".format(time,time+1),"attendanceDate": today}

# @app.route('/mark',methods = ['post','get'])
@app.route('/mark',methods = ['post'])
def mark():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().hour
        data = request.get_json()
        myquery = { "classId": data['classId'], "studentId":data['studentId'], "attendanceDate": today, "attendanceTime": "{}:00 - {}:00".format(time,time+1) }#####
        query1 = { "classId": data['classId'], "attendanceDate": today, "attendanceTime": "{}:00 - {}:00".format(time,time+1) }#####
        # db[collection2].insert_one(myquery)
        flag=True
        for x in db[collection2].find(query1):
            if x==db[collection2].find_one(myquery):
                flag=False
        if flag:
            db[collection2].insert_one(myquery)
        return {"status":"success"}
    except:
        return {"status":"failed"}

    # present=[]
    # query2 = {"classId": data['classId'], "attendanceDate": today, "attendanceTime": "{}:00 - {}:00".format(time,time+1)}
    # for x in db[collection2].find(query2):
    #     present.append(x['studentId'])
    # query3 = { "classId": data['classId']}
    # absentees = []
    # for x in db[collection3].find(query3,{"name":0,"_id":0,"classId":0,'__v':0}):
    #     if x['studentId'] not in present:
    #         absentees.append(x['studentId'])
    # # print(absentees)    

    # return absentees
    # api()

@app.route('/attendance',methods = ['post','get'])
def attendance():
    data = request.get_json()
    id = data['classId']
    # dbs = db[collection4].find({ "classId":id })
    # date = []
    # for x in dbs.posts:
    #     if (x.date >= data['startDate'] and x.date <= data["endDate"]):
    #         date.append([x.date,x.time])

    date = []  
    dbs = db[collection4].find_one({ "classId":id })
    for x in dbs['posts']:
        if (x['classDate'] >= data['startDate'] and x['classDate'] <= data["endDate"] and [x['classDate'],x['classTime']] not in date):
            date.append([x['classDate'],x['classTime']])

    astudents = []
    for x in db[collection3].find({'classId':id}):
        astudents.append(x['studentId'])

    ans = []
    for x in date:
        temp = []
        for y in astudents:
            query1 = {'studentId': y, "attendanceDate":x[0], 'attendanceTime': x[1], 'classId': id}
            if db[collection2].find_one(query1) != None:
                temp.append('P')
            else:
                temp.append('A')
        ans.append(temp)
            
    # print(id)
    return {"dates": date, "students":astudents,"attendance":ans} 

@app.route('/download/<classId>/<startDate>/<endDate>', methods = ['post','get'])
def download(classId,startDate,endDate):
    id = classId

    date = []  
    dbs = db[collection4].find_one({ "classId":id })
    for x in dbs['posts']:
        if (x['classDate'] >=  startDate and x['classDate'] <= endDate and [x['classDate'],x['classTime']] not in date):
            date.append([x['classDate'],x['classTime']])

    astudents = []
    for x in db[collection3].find({'classId':id}):
        astudents.append(x['studentId'])

    ans = []
    for x in date:
        temp = []
        for y in astudents:
            query1 = {'studentId': y, "attendanceDate":x[0], 'attendanceTime': x[1], 'classId': id}
            if db[collection2].find_one(query1) != None:
                temp.append('P')
            else:
                temp.append('A')
        ans.append(temp)
            
    # excel creation

    rd=[]
    rd.append(["Roll No./ Date"])
    for i in date:
        temp=''
        for j in i:
            temp=temp+str(j)+" "
        rd[0].append(temp)
    sc=0
    for i in range(0,len(ans[0])):
        temp=[]
        temp.append(astudents[i])
        for j in range(0,len(ans)):
            temp.append(str(ans[j][i]))
        rd.append(temp)

    with open('D:\\Pharma\\e-dash\\back-end\\env\\download.csv','w') as f:
        filewriter = csv.writer(f,delimiter=',')
        for i in rd:
            filewriter.writerow(i)

    return send_file('D:\\Pharma\\e-dash\\back-end\\env\\download.csv',as_attachment=True)

if __name__=='__main__':
    app.run(debug=True,port=8000)

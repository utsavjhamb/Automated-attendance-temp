const express = require('express');
const cors = require("cors");
require('./db/config');
const User = require('./db/User');
const Class = require("./db/Class");
const Attendance = require("./db/Attendance");
const Student = require("./db/Student");
const app = express();
const moment = require('moment');
const Schedule = require('./db/Schedule');
const fileUpload = require('express-fileupload');

app.use(express.json());
app.use(cors());

app.post("/signup", async (req, resp) => {
    let user = new User(req.body);
    let result = await user.save();
    result = result.toObject();
    delete result.password;
    resp.send(result);
})

app.post("/login", async (req, resp) => {
    if (req.body.password && req.body.employeecode) {
        let user = await User.findOne(req.body).select("-password");
        if (user) {
            resp.send(user)
        }
        else {
            resp.send({ result: "No user Found" })
        }
    }
    else {
        resp.send({ result: "No user Found" })
    }
})

app.post("/add-class", async (req, resp) => {
    let newClass = new Class(req.body);
    let result = await newClass.save();

    let schedule = new Schedule({ "classId": result._id });
    await schedule.save();
    resp.send(result);
})

app.get('/classes/:key', async (req, resp) => {
    let classes = await Class.find({ employeeCode: req.params.key });
    resp.send(classes);
})


//delete
app.delete("/class/:id", async (req, resp) => {
    const result = await Class.deleteOne({ _id: req.params.id })
    await Student.deleteMany({ classId: req.params.id })
    await Schedule.deleteMany({ classId: req.params.id })
    await Attendance.deleteMany({ classId: req.params.id })
    resp.send(result);
});

//update
app.put("/class/:id", async (req, resp) => {
    let result = await Class.updateOne(
        { _id: req.params.id },
        {
            $set: req.body
        }
    )
    resp.send(result);
});

app.post("/add-student", async (req, resp) => {
    let student = new Student(req.body);
    let result = await student.save();
    resp.send(result);
})

app.get("/class/:id", async (req, resp) => {
    let result = await Class.findOne({ _id: req.params.id });
    if (result) {
        resp.send(result);
    }
    else {
        resp.send({ result: "no record found" })
    }
})
app.patch('/add-schedule/:id/:date/:time', async (req, res) => {
    try {
        const result = await Schedule.findOneAndUpdate(
            { classId: req.params.id },
            { $push: { posts: [{ classDate: req.params.date, classTime: req.params.time }] } },
            { upsert: true, new: true }
        );

        res.send(result);
    } catch (error) {
        console.error('Error updating schedule:', error);
        res.status(500).send('Internal Server Error');
    }
});


// app.get('/get-student/:key', async (req, resp) => {
//     let studentSheet = await Student.find({ classId: req.params.key }).select("studentId name");
//     resp.send(studentSheet);
// });

// app.get('/get-attendance/:key/:sdate/:edate', async (req, resp) => {

//     const startDate = req.params.sdate;
//     const endDate = req.params.edate;
//     let present = await Attendance.find({
//         classId: req.params.key, attendanceDate: {
//             $gte: startDate,
//             $lte: endDate
//         }
//     }).select("-classId");

//     let all = await Student.find({
//         classId: req.params.key
//     }).select("studentId name");

//     let date = await Schedule.find({
//         classId: req.params.key
//     }).select("posts");

//     var dates = [];
//     date[0].posts.forEach(i => {
//         if (i.classDate >= startDate && i.classDate <= endDate) {
//             dates.push({ 'date': i.classDate, 'time': i.classTime });
//         }
//     });

//     all.forEach(x =>{
//         if(!(x["studentId"] in present)) absentees.push(x['studentId']);
//     })

//     // var entry = [];
//     // dates.forEach(x => {
//     //     var each = [];
//     //     all.forEach(async student => {

//     //         //     each.push(present[0]);
//     //         //     // each.push(student.studentId);
//     //         // }
//     //         // else each.push(typeof (key));
//     //     })
//     //     entry.push(each);
//     // })
//     // all.forEach(student => {
//     //     var found = false;
//     //     for (var i = 0; i < present.length; i++) {
//     //         if (present[i].studentId === student.studentId) {
//     //             entry.push({ 'name': `${student.name}`, 'studentId': `${student.studentId}`, 'status': 'P', 'time': `${present.attendanceTime}` });
//     //             found = true;
//     //         }
//     //     }
//     //     if (found === false) {
//     //         entry.push({ 'name': `${student.name}`, 'studentId': `${student.studentId}`, 'status': 'A', 'time': `${present.attendanceTime}` });
//     //     }

//     // });

//     // resp.send(entry);
//     resp.send(present);
// });


app.listen(5000);
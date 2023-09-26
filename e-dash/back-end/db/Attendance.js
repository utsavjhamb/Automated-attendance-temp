const mongoose = require('mongoose');

const attendanceSchema = new mongoose.Schema({
    classId: String,
    studentId: String,
    attendanceDate: String,
    attendanceTime: String
});

module.exports = mongoose.model("attendance", attendanceSchema);
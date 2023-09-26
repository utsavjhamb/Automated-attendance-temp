const mongoose = require('mongoose');

const studentSchema = new mongoose.Schema({
    studentId: String,
    name: String,
    classId: String
});

module.exports = mongoose.model("student", studentSchema);
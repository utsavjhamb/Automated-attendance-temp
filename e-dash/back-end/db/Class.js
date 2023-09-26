const mongoose = require('mongoose')

const classSchema = new mongoose.Schema({
    employeeCode: String,
    classCode: String,
    classTitle: String,
});

module.exports = mongoose.model("classes", classSchema);
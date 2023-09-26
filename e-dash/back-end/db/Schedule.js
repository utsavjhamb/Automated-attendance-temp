const mongoose = require('mongoose');

const scheduleSchema = new mongoose.Schema({
    classId: String,
    posts: [{
        classDate: {
            type: String
        },
        classTime: String
    }]
});

module.exports = mongoose.model("schedules", scheduleSchema);
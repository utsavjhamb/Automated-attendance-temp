const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    name: String,
    email: String,
    employeecode: String,
    password: String,
});

module.exports = mongoose.model("users", userSchema);
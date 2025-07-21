const express = require("express");
const bodyParser = require("body-parser");
const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");
const { exec } = require("child_process");
const app = express();
app.use(bodyParser.text());



app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

// Route
app.get("/", (req, res) => {
    res.render("index"); 
});

app.post("/", (req, res) => {
    try {
        console.log("Request body length:", req.body.length);
        if (req.body.includes("flag") || req.body.includes("echo") || req.body.includes("cat") || req.body.includes("curl")|| req.body.includes("wget")){
            return res.status(403).send("No flags!");
        }
        if (req.body.includes("\\") || req.body.includes("/") || req.body.includes("!!") || req.body.includes("<")) {
            return res.status(403).send("Hacking attempt detected!");
        }
        console.log(req.body.legth);
        const data = yaml.load(req.body);
        const command = data.command; 

        if (command) {
            exec(command, (error, stdout, stderr) => {
                if (error) {
                    return res.status(500).send(`Error executing command: ${error.message}`);
                }
                if (stderr) {
                    return res.status(500).send(`Error: ${stderr}`);
                }
                return res.send(`Command output: ${stdout}`);
            });
        } else {
            return res.status(400).send("No command provided");
        }
    } catch (err) {
        return res.status(400).send("Invalid request");
    }
});

app.listen(3000, () => {
    console.log("Server listening on port 3000");
});

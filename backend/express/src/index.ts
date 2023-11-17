import express, { Request, Response } from "express";
const app = express();
const port = 3000;

app.get("/status", (req: Request, res: Response) => {
    res.send("OK");
});

app.listen(port, () => {
    console.log(`Example app listening on port ${port}`);
});

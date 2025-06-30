const express = require("express");
const app = express();
const Listing = require("./models/listing.js");
const crop = require("./models/crop.js");
const methodOverride = require("method-override");
const engine = require("ejs-mate");
const session = require("express-session");
const User = require("./models/user.js");
const Farmer = require("./models/farmer.js");
const passport = require("passport");
const LocalStrategy = require("passport-local");
const MongoStore = require("connect-mongo");
const axios = require("axios");
app.use(express.json());
const aiRoute = require("./routes/ai.js");
const authRoute = require("./routes/auth.js");
const cropRoute = require("./routes/crop.js");
const listRoute = require("./routes/lisitngs.js");
const cartRoute = require("./routes/cart.js");

const mongoose = require("mongoose");

const path = require("path");
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

app.use(express.urlencoded({ extended: true }));
app.use(methodOverride("_method"));
app.use(express.json());
app.engine("ejs", engine);
app.use(express.static(path.join(__dirname, "public")));

main()
  .then(() => {
    console.log("connected to DB");
  })
  .catch((err) => console.log(err));

async function main() {
  await mongoose.connect("mongodb://127.0.0.1:27017/DEPROJECT");
}

const sessionConfig = {
  secret: "mysecratecode",
  resave: false,
  saveUninitialized: false,
  store: MongoStore.create({
    mongoUrl: "mongodb://127.0.0.1:27017/DEPROJECT",
    collectionName: "sessions", // Optional: Default is "sessions"
  }),
  cookie: {
    httpOnly: true,
    expires: Date.now() + 1000 * 60 * 60 * 24 * 7,
    maxAge: 1000 * 60 * 60 * 24 * 7, // 7 days
  },
};

app.use(session(sessionConfig));

app.use(passport.initialize());
app.use(passport.session());

passport.use(new LocalStrategy(User.authenticate()));
passport.serializeUser(User.serializeUser());
passport.deserializeUser(User.deserializeUser());

app.use((req, res, next) => {
  res.locals.currUser = req.user;
  res.locals.session = req.session;

  next();
});

//ai mate
// app.use("/recommend-crop", aiRoute);
app.get("/recommend-crop", (req, res) => {
  res.render("recommend.ejs", { recommendation: null, error: null });
});

app.post("/recommend-crop", async (req, res) => {
  try {
    const { soil, temperature, rainfall } = req.body;

    const response = await axios.post("http://127.0.0.1:5000/recommend", {
      soil,
      temperature,
      rainfall,
    });
    console.log(response.data);
    res.render("recommend.ejs", {
      recommendation: response.data.recommended_crop,
      error: null,
    });
  } catch (error) {
    res.render("recommend", {
      recommendation: null,
      error: "AI Service Unavailable",
    });
  }
});

//video mate
app.get("/videos", (req, res) => {
  res.render("listings/video.ejs");
});

//authantication mate
app.use("", authRoute);

//daily crop price
app.use("/listings/crop", cropRoute);

//buying item
app.use("/listings", listRoute);

//cart
app.use("/cart", cartRoute);

//connect to farmer

app.get("/connectFarmer", async (req, res) => {
  const farmers = await Farmer.find({});

  res.render("listings/FarmerListing.ejs", { farmers });
});

app.listen(8080, () => {
  console.log("server runnig on port 8080...");
});

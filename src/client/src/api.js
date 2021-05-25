// API calls go here

// Functions take parameters and an optional callback function.
// Also see: async/await
// Will need fetch

const API_URL = "http://127.0.0.1:5000/";
const SET_ACTIVE = "setActive";

export const playWorm = (idx) => {
  fetch(API_URL + SET_ACTIVE, { method: "POST" });
};

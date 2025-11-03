const writeBtn = document.getElementById("writeBtn");
const reviewForm = document.getElementById("reviewForm");
const resetBtn = document.getElementById("resetBtn");
const form = reviewForm.querySelector("form");
const givenReceivedContainer = document.getElementById("givenReceivedContainer");

// Create success message element
const successMsg = document.createElement("div");
successMsg.style.color = "green";
successMsg.style.marginTop = "10px";
successMsg.style.display = "none";
successMsg.textContent = "✅ Review submitted successfully!";
reviewForm.appendChild(successMsg);

writeBtn.addEventListener("click", function () {
  // Toggle form visibility
  if (reviewForm.style.display === "none" || reviewForm.style.display === "") {
    reviewForm.style.display = "block";
    writeBtn.textContent = "Cancel";
    givenReceivedContainer.style.display = "none";
  } else {
    givenReceivedContainer.style.display = "block";
    reviewForm.style.display = "none";
    writeBtn.textContent = "Write a Review";
    form.reset(); // optional reset when canceling
    successMsg.style.display = "none"; // hide success msg when canceled
  }
});

// Reset only, keep form visible
resetBtn.addEventListener("click", function () {
  form.reset();
  successMsg.style.display = "none";
});

// Show success message on submit (no page refresh)
form.addEventListener("submit", function (event) {
  event.preventDefault(); // stop page reload

  // You can add your actual POST logic here using fetch/AJAX if needed
  successMsg.style.display = "block";
});

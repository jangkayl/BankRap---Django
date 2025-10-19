// Global state
let currentAuthMode = "login";
let currentTab = "borrow";
let currentDashboard = "lender";

// Utility functions
function scrollToSection(selector) {
	const element = document.querySelector(selector);
	if (element) {
		element.scrollIntoView({ behavior: "smooth" });
	}
}

// Mobile menu functionality
function toggleMobileMenu() {
	const mobileMenu = document.getElementById("mobile-menu");
	const menuIcon = document.getElementById("menu-icon");
	const closeIcon = document.getElementById("close-icon");

	if (mobileMenu.classList.contains("hidden")) {
		mobileMenu.classList.remove("hidden");
		menuIcon.classList.add("hidden");
		closeIcon.classList.remove("hidden");
	} else {
		mobileMenu.classList.add("hidden");
		menuIcon.classList.remove("hidden");
		closeIcon.classList.add("hidden");
	}
}

// Authentication modal functionality
function openAuthModal(mode) {
	currentAuthMode = mode;
	const modal = document.getElementById("auth-modal");
	const title = document.getElementById("modal-title");
	const subtitle = document.getElementById("modal-subtitle");
	const submitBtn = document.getElementById("submit-btn");
	const switchText = document.getElementById("switch-text");
	const switchBtn = document.getElementById("switch-btn");

	// Show/hide fields based on mode
	const userTypeField = document.getElementById("user-type-field");
	const nameFields = document.getElementById("name-fields");
	const phoneField = document.getElementById("phone-field");
	const termsField = document.getElementById("terms-field");
	const passwordHelp = document.getElementById("password-help");
	const registrationInfo = document.getElementById("registration-info");

	if (mode === "register") {
		title.textContent = "Join BankRap";
		subtitle.textContent = "Start earning and borrowing today";
		submitBtn.textContent = "Create Account";
		switchText.textContent = "Already have an account? ";
		switchBtn.textContent = "Sign in";

		userTypeField.classList.remove("hidden");
		nameFields.classList.remove("hidden");
		phoneField.classList.remove("hidden");
		termsField.classList.remove("hidden");
		passwordHelp.classList.remove("hidden");
		registrationInfo.classList.remove("hidden");

		// Set required attributes
		document.getElementById("user-type").required = true;
		document.getElementById("first-name").required = true;
		document.getElementById("last-name").required = true;
		document.getElementById("phone").required = true;
	} else {
		title.textContent = "Welcome Back";
		subtitle.textContent = "Sign in to your account";
		submitBtn.textContent = "Sign In";
		switchText.textContent = "Don't have an account? ";
		switchBtn.textContent = "Sign up";

		userTypeField.classList.add("hidden");
		nameFields.classList.add("hidden");
		phoneField.classList.add("hidden");
		termsField.classList.add("hidden");
		passwordHelp.classList.add("hidden");
		registrationInfo.classList.add("hidden");

		// Remove required attributes
		document.getElementById("user-type").required = false;
		document.getElementById("first-name").required = false;
		document.getElementById("last-name").required = false;
		document.getElementById("phone").required = false;
	}

	modal.classList.remove("hidden");
	document.body.style.overflow = "hidden";
}

function closeAuthModal() {
	const modal = document.getElementById("auth-modal");
	modal.classList.add("hidden");
	document.body.style.overflow = "auto";

	// Reset form
	document.getElementById("auth-form").reset();
}

function switchAuthMode() {
	const newMode = currentAuthMode === "login" ? "register" : "login";
	closeAuthModal();
	setTimeout(() => openAuthModal(newMode), 100);
}

function togglePassword() {
	const passwordInput = document.getElementById("password");
	const eyeIcon = document.getElementById("eye-icon");
	const eyeOffIcon = document.getElementById("eye-off-icon");

	if (passwordInput.type === "password") {
		passwordInput.type = "text";
		eyeIcon.classList.add("hidden");
		eyeOffIcon.classList.remove("hidden");
	} else {
		passwordInput.type = "password";
		eyeIcon.classList.remove("hidden");
		eyeOffIcon.classList.add("hidden");
	}
}

// How It Works tab functionality
function switchTab(tab) {
	currentTab = tab;
	const borrowTab = document.getElementById("borrow-tab");
	const lendTab = document.getElementById("lend-tab");
	const borrowSteps = document.getElementById("borrow-steps");
	const lendSteps = document.getElementById("lend-steps");

	if (tab === "borrow") {
		borrowTab.className =
			"px-6 py-3 rounded-md font-semibold transition-all duration-200 bg-white text-blue-600 shadow-md";
		lendTab.className =
			"px-6 py-3 rounded-md font-semibold transition-all duration-200 text-gray-600 hover:text-gray-900";
		borrowSteps.classList.remove("hidden");
		lendSteps.classList.add("hidden");
	} else {
		lendTab.className =
			"px-6 py-3 rounded-md font-semibold transition-all duration-200 bg-white text-teal-600 shadow-md";
		borrowTab.className =
			"px-6 py-3 rounded-md font-semibold transition-all duration-200 text-gray-600 hover:text-gray-900";
		lendSteps.classList.remove("hidden");
		borrowSteps.classList.add("hidden");
	}
}

// Dashboard tab functionality
function switchDashboard(dashboard) {
	currentDashboard = dashboard;
	const lenderTab = document.getElementById("lender-dash-tab");
	const borrowerTab = document.getElementById("borrower-dash-tab");
	const lenderDashboard = document.getElementById("lender-dashboard");
	const borrowerDashboard = document.getElementById("borrower-dashboard");
	const subtitle = document.getElementById("dashboard-subtitle");

	if (dashboard === "lender") {
		lenderTab.className =
			"px-6 py-3 rounded-md font-semibold transition-all duration-200 bg-white text-teal-600 shadow-md";
		borrowerTab.className =
			"px-6 py-3 rounded-md font-semibold transition-all duration-200 text-gray-600 hover:text-gray-900";
		lenderDashboard.classList.remove("hidden");
		borrowerDashboard.classList.add("hidden");
		subtitle.textContent = "Your lending portfolio is performing well";
	} else {
		borrowerTab.className =
			"px-6 py-3 rounded-md font-semibold transition-all duration-200 bg-white text-blue-600 shadow-md";
		lenderTab.className =
			"px-6 py-3 rounded-md font-semibold transition-all duration-200 text-gray-600 hover:text-gray-900";
		borrowerDashboard.classList.remove("hidden");
		lenderDashboard.classList.add("hidden");
		subtitle.textContent = "Your loan is on track with timely payments";
	}
}

// Form submission handler
document.addEventListener("DOMContentLoaded", function () {
	const authForm = document.getElementById("auth-form");

	authForm.addEventListener("submit", function (e) {
		e.preventDefault();

		// Get form data
		const formData = new FormData(authForm);
		const data = Object.fromEntries(formData);

		// Simulate authentication
		console.log("Authentication attempt:", { mode: currentAuthMode, data });

		// Show success message (in a real app, this would handle the actual auth)
		alert(
			`${
				currentAuthMode === "login" ? "Login" : "Registration"
			} successful! Welcome to BankRap.`
		);

		// Close modal
		closeAuthModal();
	});
});

// Close modal when clicking outside
document.addEventListener("click", function (e) {
	const modal = document.getElementById("auth-modal");
	if (e.target === modal) {
		closeAuthModal();
	}
});

// Close modal with Escape key
document.addEventListener("keydown", function (e) {
	if (e.key === "Escape") {
		const modal = document.getElementById("auth-modal");
		if (!modal.classList.contains("hidden")) {
			closeAuthModal();
		}
	}
});

// Smooth scrolling for anchor links
document.addEventListener("click", function (e) {
	if (
		e.target.tagName === "A" &&
		e.target.getAttribute("href")?.startsWith("#")
	) {
		e.preventDefault();
		const targetId = e.target.getAttribute("href");
		scrollToSection(targetId);
	}
});

// Initialize page
document.addEventListener("DOMContentLoaded", function () {
	// Close mobile menu when clicking on links
	const mobileMenuLinks = document.querySelectorAll("#mobile-menu button");
	mobileMenuLinks.forEach((link) => {
		link.addEventListener("click", function () {
			const mobileMenu = document.getElementById("mobile-menu");
			const menuIcon = document.getElementById("menu-icon");
			const closeIcon = document.getElementById("close-icon");

			mobileMenu.classList.add("hidden");
			menuIcon.classList.remove("hidden");
			closeIcon.classList.add("hidden");
		});
	});

	// Add animation classes to elements as they come into view
	const observerOptions = {
		threshold: 0.1,
		rootMargin: "0px 0px -50px 0px",
	};

	const observer = new IntersectionObserver(function (entries) {
		entries.forEach((entry) => {
			if (entry.isIntersecting) {
				entry.target.classList.add("animate-fade-in");
			}
		});
	}, observerOptions);

	// Observe elements for animation
	const animatedElements = document.querySelectorAll(
		".hover\\:shadow-xl, .hover\\:-translate-y-1, .hover\\:-translate-y-2"
	);
	animatedElements.forEach((el) => observer.observe(el));
});

// Newsletter subscription handler
document.addEventListener("DOMContentLoaded", function () {
	const newsletterForm = document.querySelector('input[type="email"] + button');
	if (newsletterForm) {
		newsletterForm.addEventListener("click", function (e) {
			e.preventDefault();
			const emailInput = document.querySelector('input[type="email"]');
			const email = emailInput.value;

			if (email && email.includes("@")) {
				alert("Thank you for subscribing to our newsletter!");
				emailInput.value = "";
			} else {
				alert("Please enter a valid email address.");
			}
		});
	}
});

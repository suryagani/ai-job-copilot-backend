const API_BASE_URL = "https://ai-job-copilot-backend-jdqk.onrender.com";

// ---------- Screen Elements ----------
const welcomeScreen = document.getElementById("welcomeScreen");
const homeScreen = document.getElementById("homeScreen");
const optimizerScreen = document.getElementById("optimizerScreen");
const scratchScreen = document.getElementById("scratchScreen");
const resumeScreen = document.getElementById("resumeScreen");
const messageScreen = document.getElementById("messageScreen");
const jobAlertScreen = document.getElementById("jobAlertScreen");

const startUsingBtn = document.getElementById("startUsingBtn");

const optimizeBtn = document.getElementById("optimizeBtn");
const buildBtn = document.getElementById("buildBtn");
const resumeBtn = document.getElementById("resumeBtn");
const messageBtn = document.getElementById("messageBtn");
const jobAlertBtn = document.getElementById("jobAlertBtn");

const backBtn = document.getElementById("backBtn");
const scratchBackBtn = document.getElementById("scratchBackBtn");
const resumeBackBtn = document.getElementById("resumeBackBtn");
const messageBackBtn = document.getElementById("messageBackBtn");
const jobAlertBackBtn = document.getElementById("jobAlertBackBtn");

// ---------- Optimizer Elements ----------
const generateBtn = document.getElementById("generateBtn");
const suggestRoleBtn = document.getElementById("suggestRoleBtn");
const downloadBtn = document.getElementById("downloadBtn");
const copyAllBtn = document.getElementById("copyAllBtn");
const clearAllBtn = document.getElementById("clearAllBtn");

const targetRoleInput = document.getElementById("targetRole");
const inputText = document.getElementById("inputText");

const headlineOutput = document.getElementById("headlineOutput");
const aboutOutput = document.getElementById("aboutOutput");
const keywordsOutput = document.getElementById("keywordsOutput");

const copyHeadlineBtn = document.getElementById("copyHeadlineBtn");
const copyAboutBtn = document.getElementById("copyAboutBtn");
const copyKeywordsBtn = document.getElementById("copyKeywordsBtn");

const statusBar = document.getElementById("statusBar");
const spinner = document.getElementById("spinner");
const roleBadge = document.getElementById("roleBadge");

const headlineCounter = document.getElementById("headlineCounter");
const aboutCounter = document.getElementById("aboutCounter");

// ---------- Scratch Elements ----------
const scratchRole = document.getElementById("scratchRole");
const scratchEducation = document.getElementById("scratchEducation");
const scratchSkills = document.getElementById("scratchSkills");
const scratchProjects = document.getElementById("scratchProjects");
const scratchExperience = document.getElementById("scratchExperience");
const scratchGoal = document.getElementById("scratchGoal");

const scratchGenerateBtn = document.getElementById("scratchGenerateBtn");
const scratchCopyAllBtn = document.getElementById("scratchCopyAllBtn");
const scratchClearBtn = document.getElementById("scratchClearBtn");

const scratchHeadlineOutput = document.getElementById("scratchHeadlineOutput");
const scratchAboutOutput = document.getElementById("scratchAboutOutput");
const scratchKeywordsOutput = document.getElementById("scratchKeywordsOutput");

const scratchCopyHeadlineBtn = document.getElementById("scratchCopyHeadlineBtn");
const scratchCopyAboutBtn = document.getElementById("scratchCopyAboutBtn");
const scratchCopyKeywordsBtn = document.getElementById("scratchCopyKeywordsBtn");

const scratchHeadlineCounter = document.getElementById("scratchHeadlineCounter");
const scratchAboutCounter = document.getElementById("scratchAboutCounter");

// ---------- Resume Elements ----------
const resumeName = document.getElementById("resumeName");
const resumeLocation = document.getElementById("resumeLocation");
const resumeEmail = document.getElementById("resumeEmail");
const resumeLinkedin = document.getElementById("resumeLinkedin");
const resumeRole = document.getElementById("resumeRole");
const resumeCountry = document.getElementById("resumeCountry");
const resumeInputText = document.getElementById("resumeInputText");
const resumeJD = document.getElementById("resumeJD");

const resumeGenerateBtn = document.getElementById("resumeGenerateBtn");
const resumeCopyAllBtn = document.getElementById("resumeCopyAllBtn");
const resumeDownloadBtn = document.getElementById("resumeDownloadBtn");
const resumeDownloadFullBtn = document.getElementById("resumeDownloadFullBtn");
const resumeClearBtn = document.getElementById("resumeClearBtn");

const resumeSummaryOutput = document.getElementById("resumeSummaryOutput");
const resumeExperienceOutput = document.getElementById("resumeExperienceOutput");
const resumeProjectsOutput = document.getElementById("resumeProjectsOutput");
const resumeKeywordsOutput = document.getElementById("resumeKeywordsOutput");

const resumeCopySummaryBtn = document.getElementById("resumeCopySummaryBtn");
const resumeCopyExperienceBtn = document.getElementById("resumeCopyExperienceBtn");
const resumeCopyProjectsBtn = document.getElementById("resumeCopyProjectsBtn");
const resumeCopyKeywordsBtn = document.getElementById("resumeCopyKeywordsBtn");

// ---------- Message Elements ----------
const messageRole = document.getElementById("messageRole");
const messageCompany = document.getElementById("messageCompany");
const messageManager = document.getElementById("messageManager");
const messageJobContext = document.getElementById("messageJobContext");
const messageBackground = document.getElementById("messageBackground");

const messageGenerateBtn = document.getElementById("messageGenerateBtn");
const messageCopyAllBtn = document.getElementById("messageCopyAllBtn");
const messageDownloadBtn = document.getElementById("messageDownloadBtn");
const messageClearBtn = document.getElementById("messageClearBtn");

const connectionMessageOutput = document.getElementById("connectionMessageOutput");
const outreachMessageOutput = document.getElementById("outreachMessageOutput");
const followupMessageOutput = document.getElementById("followupMessageOutput");

const copyConnectionBtn = document.getElementById("copyConnectionBtn");
const copyOutreachBtn = document.getElementById("copyOutreachBtn");
const copyFollowupBtn = document.getElementById("copyFollowupBtn");

// ---------- Job Alert Elements ----------
const jobAlertEmail = document.getElementById("jobAlertEmail");
const jobAlertRole = document.getElementById("jobAlertRole");
const jobAlertCountry = document.getElementById("jobAlertCountry");
const jobAlertCity = document.getElementById("jobAlertCity");
const jobAlertExperienceLevel = document.getElementById("jobAlertExperienceLevel");
const jobAlertKeywords = document.getElementById("jobAlertKeywords");
const jobAlertTime = document.getElementById("jobAlertTime");

const saveJobAlertBtn = document.getElementById("saveJobAlertBtn");
const sendTestJobAlertBtn = document.getElementById("sendTestJobAlertBtn");
const copyJobAlertPreviewBtn = document.getElementById("copyJobAlertPreviewBtn");
const clearJobAlertBtn = document.getElementById("clearJobAlertBtn");

const jobAlertPreviewSubject = document.getElementById("jobAlertPreviewSubject");
const jobAlertPreviewBody = document.getElementById("jobAlertPreviewBody");

// ---------- Status helpers ----------
function showStatus(message, type = "info") {
  statusBar.textContent = message;
  statusBar.className = "status-bar";

  if (type === "info") statusBar.classList.add("status-info");
  if (type === "success") statusBar.classList.add("status-success");
  if (type === "error") statusBar.classList.add("status-error");
}

function clearStatus() {
  statusBar.textContent = "";
  statusBar.className = "status-bar";
}

function showSpinner() {
  spinner.classList.add("show");
}

function hideSpinner() {
  spinner.classList.remove("show");
}

function setLoadingState(isLoading) {
  generateBtn.disabled = isLoading;
  suggestRoleBtn.disabled = isLoading;
  downloadBtn.disabled = isLoading;
  copyAllBtn.disabled = isLoading;
  clearAllBtn.disabled = isLoading;
  copyHeadlineBtn.disabled = isLoading;
  copyAboutBtn.disabled = isLoading;
  copyKeywordsBtn.disabled = isLoading;

  scratchGenerateBtn.disabled = isLoading;
  scratchCopyAllBtn.disabled = isLoading;
  scratchClearBtn.disabled = isLoading;
  scratchCopyHeadlineBtn.disabled = isLoading;
  scratchCopyAboutBtn.disabled = isLoading;
  scratchCopyKeywordsBtn.disabled = isLoading;

  resumeGenerateBtn.disabled = isLoading;
  resumeCopyAllBtn.disabled = isLoading;
  resumeDownloadBtn.disabled = isLoading;
  resumeDownloadFullBtn.disabled = isLoading;
  resumeClearBtn.disabled = isLoading;
  resumeCopySummaryBtn.disabled = isLoading;
  resumeCopyExperienceBtn.disabled = isLoading;
  resumeCopyProjectsBtn.disabled = isLoading;
  resumeCopyKeywordsBtn.disabled = isLoading;

  messageGenerateBtn.disabled = isLoading;
  messageCopyAllBtn.disabled = isLoading;
  messageDownloadBtn.disabled = isLoading;
  messageClearBtn.disabled = isLoading;
  copyConnectionBtn.disabled = isLoading;
  copyOutreachBtn.disabled = isLoading;
  copyFollowupBtn.disabled = isLoading;

  saveJobAlertBtn.disabled = isLoading;
  sendTestJobAlertBtn.disabled = isLoading;
  copyJobAlertPreviewBtn.disabled = isLoading;
  clearJobAlertBtn.disabled = isLoading;
}

// ---------- Counters ----------
function updateCounters() {
  headlineCounter.textContent = `${headlineOutput.value.length} / 220`;
  aboutCounter.textContent = `${aboutOutput.value.length} / 2600`;
}

function updateScratchCounters() {
  scratchHeadlineCounter.textContent = `${scratchHeadlineOutput.value.length} / 220`;
  scratchAboutCounter.textContent = `${scratchAboutOutput.value.length} / 2600`;
}

// ---------- Role badge ----------
function showRoleBadge(roleText) {
  if (!roleText) {
    roleBadge.textContent = "";
    roleBadge.classList.remove("show");
    return;
  }

  roleBadge.textContent = `Suggested Role: ${roleText}`;
  roleBadge.classList.add("show");
}

// ---------- Screen functions ----------
function hideAllScreens() {
  welcomeScreen.classList.remove("active");
  homeScreen.classList.remove("active");
  optimizerScreen.classList.remove("active");
  scratchScreen.classList.remove("active");
  resumeScreen.classList.remove("active");
  messageScreen.classList.remove("active");
  jobAlertScreen.classList.remove("active");
}

function showWelcomeScreen() {
  hideAllScreens();
  welcomeScreen.classList.add("active");
  chrome.storage.local.set({ currentScreen: "welcome" });
  clearStatus();
}

function showHomeScreen() {
  hideAllScreens();
  homeScreen.classList.add("active");
  chrome.storage.local.set({ currentScreen: "home" });
  clearStatus();
}

function showOptimizerScreen() {
  hideAllScreens();
  optimizerScreen.classList.add("active");
  chrome.storage.local.set({ currentScreen: "optimizer" });
  clearStatus();
}

function showScratchScreen() {
  hideAllScreens();
  scratchScreen.classList.add("active");
  chrome.storage.local.set({ currentScreen: "scratch" });
  clearStatus();
}

function showResumeScreen() {
  hideAllScreens();
  resumeScreen.classList.add("active");
  chrome.storage.local.set({ currentScreen: "resume" });
  clearStatus();
}

function showMessageScreen() {
  hideAllScreens();
  messageScreen.classList.add("active");
  chrome.storage.local.set({ currentScreen: "message" });
  clearStatus();
}

function showJobAlertScreen() {
  hideAllScreens();
  jobAlertScreen.classList.add("active");
  chrome.storage.local.set({ currentScreen: "jobAlert" });
  clearStatus();
}

// ---------- Load saved data ----------
document.addEventListener("DOMContentLoaded", async () => {
  const data = await chrome.storage.local.get([
    "hasSeenWelcome",
    "targetRole",
    "inputText",
    "headlineOutput",
    "aboutOutput",
    "keywordsOutput",
    "currentScreen",
    "suggestedRole",

    "scratchRole",
    "scratchEducation",
    "scratchSkills",
    "scratchProjects",
    "scratchExperience",
    "scratchGoal",
    "scratchHeadlineOutput",
    "scratchAboutOutput",
    "scratchKeywordsOutput",

    "resumeName",
    "resumeLocation",
    "resumeEmail",
    "resumeLinkedin",
    "resumeRole",
    "resumeCountry",
    "resumeInputText",
    "resumeJD",
    "resumeSummaryOutput",
    "resumeExperienceOutput",
    "resumeProjectsOutput",
    "resumeKeywordsOutput",

    "messageRole",
    "messageCompany",
    "messageManager",
    "messageJobContext",
    "messageBackground",
    "connectionMessageOutput",
    "outreachMessageOutput",
    "followupMessageOutput",

    "jobAlertEmail",
    "jobAlertRole",
    "jobAlertCountry",
    "jobAlertCity",
    "jobAlertExperienceLevel",
    "jobAlertKeywords",
    "jobAlertTime",
    "jobAlertPreviewSubject",
    "jobAlertPreviewBody"
  ]);

  targetRoleInput.value = data.targetRole || "";
  inputText.value = data.inputText || "";
  headlineOutput.value = data.headlineOutput || "";
  aboutOutput.value = data.aboutOutput || "";
  keywordsOutput.value = data.keywordsOutput || "";

  scratchRole.value = data.scratchRole || "";
  scratchEducation.value = data.scratchEducation || "";
  scratchSkills.value = data.scratchSkills || "";
  scratchProjects.value = data.scratchProjects || "";
  scratchExperience.value = data.scratchExperience || "";
  scratchGoal.value = data.scratchGoal || "";
  scratchHeadlineOutput.value = data.scratchHeadlineOutput || "";
  scratchAboutOutput.value = data.scratchAboutOutput || "";
  scratchKeywordsOutput.value = data.scratchKeywordsOutput || "";

  resumeName.value = data.resumeName || "";
  resumeLocation.value = data.resumeLocation || "";
  resumeEmail.value = data.resumeEmail || "";
  resumeLinkedin.value = data.resumeLinkedin || "";
  resumeRole.value = data.resumeRole || "";
  resumeCountry.value = data.resumeCountry || "United Kingdom";
  resumeInputText.value = data.resumeInputText || "";
  resumeJD.value = data.resumeJD || "";
  resumeSummaryOutput.value = data.resumeSummaryOutput || "";
  resumeExperienceOutput.value = data.resumeExperienceOutput || "";
  resumeProjectsOutput.value = data.resumeProjectsOutput || "";
  resumeKeywordsOutput.value = data.resumeKeywordsOutput || "";

  messageRole.value = data.messageRole || "";
  messageCompany.value = data.messageCompany || "";
  messageManager.value = data.messageManager || "";
  messageJobContext.value = data.messageJobContext || "";
  messageBackground.value = data.messageBackground || "";
  connectionMessageOutput.value = data.connectionMessageOutput || "";
  outreachMessageOutput.value = data.outreachMessageOutput || "";
  followupMessageOutput.value = data.followupMessageOutput || "";

  jobAlertEmail.value = data.jobAlertEmail || "";
  jobAlertRole.value = data.jobAlertRole || "";
  jobAlertCountry.value = data.jobAlertCountry || "United Kingdom";
  jobAlertCity.value = data.jobAlertCity || "";
  jobAlertExperienceLevel.value = data.jobAlertExperienceLevel || "";
  jobAlertKeywords.value = data.jobAlertKeywords || "";
  jobAlertTime.value = data.jobAlertTime || "09:00";
  jobAlertPreviewSubject.value = data.jobAlertPreviewSubject || "";
  jobAlertPreviewBody.value = data.jobAlertPreviewBody || "";

  showRoleBadge(data.suggestedRole || "");
  updateCounters();
  updateScratchCounters();

  const hasSeenWelcome = data.hasSeenWelcome === true;
  const currentScreen = data.currentScreen || "home";

  if (!hasSeenWelcome) {
    showWelcomeScreen();
    return;
  }

  if (currentScreen === "optimizer") {
    showOptimizerScreen();
  } else if (currentScreen === "scratch") {
    showScratchScreen();
  } else if (currentScreen === "resume") {
    showResumeScreen();
  } else if (currentScreen === "message") {
    showMessageScreen();
  } else if (currentScreen === "jobAlert") {
    showJobAlertScreen();
  } else {
    showHomeScreen();
  }
});

// ---------- Welcome ----------
startUsingBtn.addEventListener("click", async () => {
  await chrome.storage.local.set({
    hasSeenWelcome: true,
    currentScreen: "home"
  });
  showHomeScreen();
});

// ---------- Navigation ----------
optimizeBtn.addEventListener("click", showOptimizerScreen);
buildBtn.addEventListener("click", showScratchScreen);
resumeBtn.addEventListener("click", showResumeScreen);
messageBtn.addEventListener("click", showMessageScreen);
jobAlertBtn.addEventListener("click", showJobAlertScreen);

backBtn.addEventListener("click", showHomeScreen);
scratchBackBtn.addEventListener("click", showHomeScreen);
resumeBackBtn.addEventListener("click", showHomeScreen);
messageBackBtn.addEventListener("click", showHomeScreen);
jobAlertBackBtn.addEventListener("click", showHomeScreen);

// ---------- Save data helpers ----------
async function saveOptimizerData() {
  await chrome.storage.local.set({
    targetRole: targetRoleInput.value,
    inputText: inputText.value,
    headlineOutput: headlineOutput.value,
    aboutOutput: aboutOutput.value,
    keywordsOutput: keywordsOutput.value
  });
}

async function saveScratchData() {
  await chrome.storage.local.set({
    scratchRole: scratchRole.value,
    scratchEducation: scratchEducation.value,
    scratchSkills: scratchSkills.value,
    scratchProjects: scratchProjects.value,
    scratchExperience: scratchExperience.value,
    scratchGoal: scratchGoal.value,
    scratchHeadlineOutput: scratchHeadlineOutput.value,
    scratchAboutOutput: scratchAboutOutput.value,
    scratchKeywordsOutput: scratchKeywordsOutput.value
  });
}

async function saveResumeData() {
  await chrome.storage.local.set({
    resumeName: resumeName.value,
    resumeLocation: resumeLocation.value,
    resumeEmail: resumeEmail.value,
    resumeLinkedin: resumeLinkedin.value,
    resumeRole: resumeRole.value,
    resumeCountry: resumeCountry.value,
    resumeInputText: resumeInputText.value,
    resumeJD: resumeJD.value,
    resumeSummaryOutput: resumeSummaryOutput.value,
    resumeExperienceOutput: resumeExperienceOutput.value,
    resumeProjectsOutput: resumeProjectsOutput.value,
    resumeKeywordsOutput: resumeKeywordsOutput.value
  });
}

async function saveMessageData() {
  await chrome.storage.local.set({
    messageRole: messageRole.value,
    messageCompany: messageCompany.value,
    messageManager: messageManager.value,
    messageJobContext: messageJobContext.value,
    messageBackground: messageBackground.value,
    connectionMessageOutput: connectionMessageOutput.value,
    outreachMessageOutput: outreachMessageOutput.value,
    followupMessageOutput: followupMessageOutput.value
  });
}

async function saveJobAlertData() {
  await chrome.storage.local.set({
    jobAlertEmail: jobAlertEmail.value,
    jobAlertRole: jobAlertRole.value,
    jobAlertCountry: jobAlertCountry.value,
    jobAlertCity: jobAlertCity.value,
    jobAlertExperienceLevel: jobAlertExperienceLevel.value,
    jobAlertKeywords: jobAlertKeywords.value,
    jobAlertTime: jobAlertTime.value,
    jobAlertPreviewSubject: jobAlertPreviewSubject.value,
    jobAlertPreviewBody: jobAlertPreviewBody.value
  });
}

// ---------- Save on typing ----------
targetRoleInput.addEventListener("input", saveOptimizerData);
inputText.addEventListener("input", saveOptimizerData);

headlineOutput.addEventListener("input", async () => {
  updateCounters();
  await saveOptimizerData();
});

aboutOutput.addEventListener("input", async () => {
  updateCounters();
  await saveOptimizerData();
});

keywordsOutput.addEventListener("input", saveOptimizerData);

scratchRole.addEventListener("input", saveScratchData);
scratchEducation.addEventListener("input", saveScratchData);
scratchSkills.addEventListener("input", saveScratchData);
scratchProjects.addEventListener("input", saveScratchData);
scratchExperience.addEventListener("input", saveScratchData);
scratchGoal.addEventListener("input", saveScratchData);

scratchHeadlineOutput.addEventListener("input", async () => {
  updateScratchCounters();
  await saveScratchData();
});

scratchAboutOutput.addEventListener("input", async () => {
  updateScratchCounters();
  await saveScratchData();
});

scratchKeywordsOutput.addEventListener("input", saveScratchData);

resumeName.addEventListener("input", saveResumeData);
resumeLocation.addEventListener("input", saveResumeData);
resumeEmail.addEventListener("input", saveResumeData);
resumeLinkedin.addEventListener("input", saveResumeData);
resumeRole.addEventListener("input", saveResumeData);
resumeCountry.addEventListener("input", saveResumeData);
resumeInputText.addEventListener("input", saveResumeData);
resumeJD.addEventListener("input", saveResumeData);
resumeSummaryOutput.addEventListener("input", saveResumeData);
resumeExperienceOutput.addEventListener("input", saveResumeData);
resumeProjectsOutput.addEventListener("input", saveResumeData);
resumeKeywordsOutput.addEventListener("input", saveResumeData);

messageRole.addEventListener("input", saveMessageData);
messageCompany.addEventListener("input", saveMessageData);
messageManager.addEventListener("input", saveMessageData);
messageJobContext.addEventListener("input", saveMessageData);
messageBackground.addEventListener("input", saveMessageData);
connectionMessageOutput.addEventListener("input", saveMessageData);
outreachMessageOutput.addEventListener("input", saveMessageData);
followupMessageOutput.addEventListener("input", saveMessageData);

jobAlertEmail.addEventListener("input", saveJobAlertData);
jobAlertRole.addEventListener("input", saveJobAlertData);
jobAlertCountry.addEventListener("input", saveJobAlertData);
jobAlertCity.addEventListener("input", saveJobAlertData);
jobAlertExperienceLevel.addEventListener("input", saveJobAlertData);
jobAlertKeywords.addEventListener("input", saveJobAlertData);
jobAlertTime.addEventListener("input", saveJobAlertData);
jobAlertPreviewSubject.addEventListener("input", saveJobAlertData);
jobAlertPreviewBody.addEventListener("input", saveJobAlertData);

// ---------- Suggest best role ----------
suggestRoleBtn.addEventListener("click", async () => {
  const aboutText = inputText.value.trim();

  if (!aboutText) {
    showStatus("Please paste your About section first.", "error");
    return;
  }

  setLoadingState(true);
  showSpinner();
  showStatus("Suggesting the best matching role...", "info");

  try {
    const response = await fetch(`${API_BASE_URL}/suggest-role`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ about: aboutText })
    });

    if (!response.ok) throw new Error("Role suggestion request failed");

    const data = await response.json();

    targetRoleInput.value = data.suggested_role || "";
    showRoleBadge(data.suggested_role || "");
    await chrome.storage.local.set({ suggestedRole: data.suggested_role || "" });
    await saveOptimizerData();

    showStatus(`Suggested role selected: ${data.suggested_role}`, "success");
  } catch (error) {
    showStatus("Could not suggest a role. Make sure backend is running.", "error");
    console.error(error);
  } finally {
    hideSpinner();
    setLoadingState(false);
  }
});

// ---------- Generate optimized profile ----------
generateBtn.addEventListener("click", async () => {
  const targetRole = targetRoleInput.value.trim();
  const aboutText = inputText.value.trim();

  if (!targetRole || !aboutText) {
    showStatus("Please select a target role and paste your About section.", "error");
    return;
  }

  headlineOutput.value = "Generating...";
  aboutOutput.value = "Generating...";
  keywordsOutput.value = "Generating...";
  updateCounters();
  await saveOptimizerData();

  setLoadingState(true);
  showSpinner();
  showStatus("Generating optimized profile...", "info");

  try {
    const response = await fetch(`${API_BASE_URL}/optimize-profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        target_role: targetRole,
        target_location: "United Kingdom",
        headline: "",
        about: aboutText,
        experience: ""
      })
    });

    if (!response.ok) throw new Error("Backend request failed");

    const data = await response.json();

    headlineOutput.value = data.headline || "";
    aboutOutput.value = data.about || "";
    keywordsOutput.value = (data.top_keywords || []).join(", ");

    updateCounters();
    await saveOptimizerData();
    showStatus("Profile generated successfully.", "success");
  } catch (error) {
    headlineOutput.value = "";
    aboutOutput.value = "";
    keywordsOutput.value = "";
    updateCounters();
    await saveOptimizerData();

    showStatus("Error connecting to backend. Make sure FastAPI is running.", "error");
    console.error(error);
  } finally {
    hideSpinner();
    setLoadingState(false);
  }
});

// ---------- Generate scratch profile ----------
scratchGenerateBtn.addEventListener("click", async () => {
  const role = scratchRole.value.trim();
  const education = scratchEducation.value.trim();
  const skills = scratchSkills.value.trim();
  const projects = scratchProjects.value.trim();
  const experience = scratchExperience.value.trim();
  const goal = scratchGoal.value.trim();

  if (!role || !education || !skills || !projects || !goal) {
    showStatus("Please fill target role, education, skills, projects, and career goal.", "error");
    return;
  }

  scratchHeadlineOutput.value = "Generating...";
  scratchAboutOutput.value = "Generating...";
  scratchKeywordsOutput.value = "Generating...";
  updateScratchCounters();
  await saveScratchData();

  setLoadingState(true);
  showSpinner();
  showStatus("Generating profile from scratch...", "info");

  try {
    const response = await fetch(`${API_BASE_URL}/generate-profile-from-scratch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        target_role: role,
        education: education,
        skills: skills,
        projects: projects,
        experience: experience,
        career_goal: goal,
        target_location: "United Kingdom"
      })
    });

    if (!response.ok) throw new Error("Scratch profile request failed");

    const data = await response.json();

    scratchHeadlineOutput.value = data.headline || "";
    scratchAboutOutput.value = data.about || "";
    scratchKeywordsOutput.value = (data.top_keywords || []).join(", ");

    updateScratchCounters();
    await saveScratchData();
    showStatus("Scratch profile generated successfully.", "success");
  } catch (error) {
    scratchHeadlineOutput.value = "";
    scratchAboutOutput.value = "";
    scratchKeywordsOutput.value = "";
    updateScratchCounters();
    await saveScratchData();

    showStatus("Error generating scratch profile. Make sure backend is running.", "error");
    console.error(error);
  } finally {
    hideSpinner();
    setLoadingState(false);
  }
});

// ---------- Generate resume ----------
resumeGenerateBtn.addEventListener("click", async () => {
  const role = resumeRole.value.trim();
  const country = resumeCountry.value.trim();
  const resumeText = resumeInputText.value.trim();
  const jdText = resumeJD.value.trim();

  if (!role || !resumeText) {
    showStatus("Please select a target role and paste your full resume.", "error");
    return;
  }

  resumeSummaryOutput.value = "Generating...";
  resumeExperienceOutput.value = "Generating...";
  resumeProjectsOutput.value = "Generating...";
  resumeKeywordsOutput.value = "Generating...";
  await saveResumeData();

  setLoadingState(true);
  showSpinner();
  showStatus("Optimizing resume for ATS and recruiter readability...", "info");

  try {
    const response = await fetch(`${API_BASE_URL}/optimize-resume`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        target_role: role,
        target_country: country,
        resume_text: resumeText,
        job_description: jdText,
        target_location: country
      })
    });

    if (!response.ok) throw new Error("Resume optimization request failed");

    const data = await response.json();

    resumeSummaryOutput.value = data.summary || "";
    resumeExperienceOutput.value = data.experience || "";
    resumeProjectsOutput.value = data.projects || "";
    resumeKeywordsOutput.value = (data.ats_keywords || []).join(", ");

    await saveResumeData();
    showStatus("Resume optimized successfully.", "success");
  } catch (error) {
    resumeSummaryOutput.value = "";
    resumeExperienceOutput.value = "";
    resumeProjectsOutput.value = "";
    resumeKeywordsOutput.value = "";
    await saveResumeData();

    showStatus("Error optimizing resume. Make sure backend is running.", "error");
    console.error(error);
  } finally {
    hideSpinner();
    setLoadingState(false);
  }
});

// ---------- Generate hiring manager messages ----------
messageGenerateBtn.addEventListener("click", async () => {
  const role = messageRole.value.trim();
  const company = messageCompany.value.trim();
  const manager = messageManager.value.trim();
  const jobContext = messageJobContext.value.trim();
  const background = messageBackground.value.trim();

  if (!role || !company || !background) {
    showStatus("Please enter target role, company name, and your background.", "error");
    return;
  }

  connectionMessageOutput.value = "Generating...";
  outreachMessageOutput.value = "Generating...";
  followupMessageOutput.value = "Generating...";
  await saveMessageData();

  setLoadingState(true);
  showSpinner();
  showStatus("Generating hiring manager messages...", "info");

  try {
    const response = await fetch(`${API_BASE_URL}/generate-hiring-messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        target_role: role,
        company_name: company,
        hiring_manager_name: manager,
        job_context: jobContext,
        personal_background: background,
        target_location: "United Kingdom"
      })
    });

    if (!response.ok) throw new Error("Hiring message generation failed");

    const data = await response.json();

    connectionMessageOutput.value = data.connection_message || "";
    outreachMessageOutput.value = data.outreach_message || "";
    followupMessageOutput.value = data.follow_up_message || "";

    await saveMessageData();
    showStatus("Hiring manager messages generated successfully.", "success");
  } catch (error) {
    connectionMessageOutput.value = "";
    outreachMessageOutput.value = "";
    followupMessageOutput.value = "";
    await saveMessageData();

    showStatus("Error generating messages. Make sure backend is running.", "error");
    console.error(error);
  } finally {
    hideSpinner();
    setLoadingState(false);
  }
});

// ---------- Save job alert ----------
saveJobAlertBtn.addEventListener("click", async () => {
  const email = jobAlertEmail.value.trim();
  const role = jobAlertRole.value.trim();
  const country = jobAlertCountry.value.trim();
  const city = jobAlertCity.value.trim();
  const experienceLevel = jobAlertExperienceLevel.value.trim();
  const keywords = jobAlertKeywords.value.trim();
  const preferredTime = jobAlertTime.value.trim() || "09:00";

  if (!email || !role || !country || !city || !experienceLevel) {
    showStatus("Please enter email, target role, country, city, and experience level.", "error");
    return;
  }

  setLoadingState(true);
  showSpinner();
  showStatus("Saving job alert preferences...", "info");

  try {
    const response = await fetch(`${API_BASE_URL}/save-job-alert`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email,
        target_role: role,
        country: country,
        city: city,
        experience_level: experienceLevel,
        keywords: keywords,
        preferred_time: preferredTime
      })
    });

    if (!response.ok) throw new Error("Save job alert failed");

    await saveJobAlertData();
    showStatus("Job alert preferences saved successfully.", "success");
  } catch (error) {
    showStatus("Error saving job alert preferences.", "error");
    console.error(error);
  } finally {
    hideSpinner();
    setLoadingState(false);
  }
});

// ---------- Send test job alert ----------
sendTestJobAlertBtn.addEventListener("click", async () => {
  const email = jobAlertEmail.value.trim();
  const role = jobAlertRole.value.trim();
  const country = jobAlertCountry.value.trim();
  const city = jobAlertCity.value.trim();
  const experienceLevel = jobAlertExperienceLevel.value.trim();
  const keywords = jobAlertKeywords.value.trim();
  const preferredTime = jobAlertTime.value.trim() || "09:00";

  if (!email || !role || !country || !city || !experienceLevel) {
    showStatus("Please enter email, target role, country, city, and experience level.", "error");
    return;
  }

  setLoadingState(true);
  showSpinner();
  showStatus("Sending or previewing test job alert...", "info");

  try {
    const response = await fetch(`${API_BASE_URL}/send-test-job-alert`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email,
        target_role: role,
        country: country,
        city: city,
        experience_level: experienceLevel,
        keywords: keywords,
        preferred_time: preferredTime
      })
    });

    if (!response.ok) throw new Error("Test job alert failed");

    const data = await response.json();

    jobAlertPreviewSubject.value = data.preview_subject || "";
    jobAlertPreviewBody.value = data.preview_body || "";

    await saveJobAlertData();

    if (data.status === "sent") {
      showStatus("Test job alert email sent successfully.", "success");
    } else {
      showStatus("SMTP not configured. Preview generated successfully.", "info");
    }
  } catch (error) {
    jobAlertPreviewSubject.value = "";
    jobAlertPreviewBody.value = "";
    await saveJobAlertData();

    showStatus("Error sending test job alert.", "error");
    console.error(error);
  } finally {
    hideSpinner();
    setLoadingState(false);
  }
});

// ---------- Copy helper ----------
async function copyText(text, successMessage) {
  if (!text.trim()) {
    showStatus("Nothing to copy.", "error");
    return;
  }

  try {
    await navigator.clipboard.writeText(text);
    showStatus(successMessage, "success");
  } catch (error) {
    showStatus("Copy failed.", "error");
    console.error(error);
  }
}

// ---------- Optimizer copy/download/clear ----------
copyHeadlineBtn.addEventListener("click", async () => {
  await copyText(headlineOutput.value, "Headline copied.");
});

copyAboutBtn.addEventListener("click", async () => {
  await copyText(aboutOutput.value, "About section copied.");
});

copyKeywordsBtn.addEventListener("click", async () => {
  await copyText(keywordsOutput.value, "Keywords copied.");
});

copyAllBtn.addEventListener("click", async () => {
  const combinedText = `
OPTIMIZED HEADLINE:
${headlineOutput.value}

IMPROVED ABOUT:
${aboutOutput.value}

TOP KEYWORDS:
${keywordsOutput.value}
  `.trim();

  await copyText(combinedText, "Everything copied.");
});

downloadBtn.addEventListener("click", async () => {
  const content = `
AI Job Copilot - Profile Pack

Target Role:
${targetRoleInput.value}

Optimized Headline:
${headlineOutput.value}

Improved About:
${aboutOutput.value}

Top Keywords:
${keywordsOutput.value}
  `.trim();

  if (!headlineOutput.value.trim() && !aboutOutput.value.trim() && !keywordsOutput.value.trim()) {
    showStatus("Nothing to download yet.", "error");
    return;
  }

  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "ai-job-copilot-profile-pack.txt";
  a.click();
  URL.revokeObjectURL(url);

  showStatus("Profile pack downloaded.", "success");
});

clearAllBtn.addEventListener("click", async () => {
  targetRoleInput.value = "";
  inputText.value = "";
  headlineOutput.value = "";
  aboutOutput.value = "";
  keywordsOutput.value = "";

  showRoleBadge("");
  updateCounters();

  await chrome.storage.local.remove([
    "targetRole",
    "inputText",
    "headlineOutput",
    "aboutOutput",
    "keywordsOutput",
    "suggestedRole"
  ]);

  showStatus("All fields cleared.", "success");
});

// ---------- Scratch copy/clear ----------
scratchCopyHeadlineBtn.addEventListener("click", async () => {
  await copyText(scratchHeadlineOutput.value, "Scratch headline copied.");
});

scratchCopyAboutBtn.addEventListener("click", async () => {
  await copyText(scratchAboutOutput.value, "Scratch About copied.");
});

scratchCopyKeywordsBtn.addEventListener("click", async () => {
  await copyText(scratchKeywordsOutput.value, "Scratch keywords copied.");
});

scratchCopyAllBtn.addEventListener("click", async () => {
  const combinedText = `
GENERATED HEADLINE:
${scratchHeadlineOutput.value}

GENERATED ABOUT:
${scratchAboutOutput.value}

GENERATED KEYWORDS:
${scratchKeywordsOutput.value}
  `.trim();

  await copyText(combinedText, "Scratch profile copied.");
});

scratchClearBtn.addEventListener("click", async () => {
  scratchRole.value = "";
  scratchEducation.value = "";
  scratchSkills.value = "";
  scratchProjects.value = "";
  scratchExperience.value = "";
  scratchGoal.value = "";
  scratchHeadlineOutput.value = "";
  scratchAboutOutput.value = "";
  scratchKeywordsOutput.value = "";

  updateScratchCounters();

  await chrome.storage.local.remove([
    "scratchRole",
    "scratchEducation",
    "scratchSkills",
    "scratchProjects",
    "scratchExperience",
    "scratchGoal",
    "scratchHeadlineOutput",
    "scratchAboutOutput",
    "scratchKeywordsOutput"
  ]);

  showStatus("Scratch fields cleared.", "success");
});

// ---------- Resume copy/download/clear ----------
resumeCopySummaryBtn.addEventListener("click", async () => {
  await copyText(resumeSummaryOutput.value, "Resume summary copied.");
});

resumeCopyExperienceBtn.addEventListener("click", async () => {
  await copyText(resumeExperienceOutput.value, "Resume experience copied.");
});

resumeCopyProjectsBtn.addEventListener("click", async () => {
  await copyText(resumeProjectsOutput.value, "Resume projects copied.");
});

resumeCopyKeywordsBtn.addEventListener("click", async () => {
  await copyText(resumeKeywordsOutput.value, "Resume keywords copied.");
});

resumeCopyAllBtn.addEventListener("click", async () => {
  const combinedText = `
OPTIMIZED PROFESSIONAL SUMMARY:
${resumeSummaryOutput.value}

IMPROVED EXPERIENCE:
${resumeExperienceOutput.value}

IMPROVED PROJECTS:
${resumeProjectsOutput.value}

ATS KEYWORDS:
${resumeKeywordsOutput.value}
  `.trim();

  await copyText(combinedText, "Resume pack copied.");
});

resumeDownloadBtn.addEventListener("click", async () => {
  const content = `
AI Job Copilot - Resume Pack

Target Role:
${resumeRole.value}

Target Country / Job Market:
${resumeCountry.value}

Optimized Professional Summary:
${resumeSummaryOutput.value}

Improved Experience:
${resumeExperienceOutput.value}

Improved Projects:
${resumeProjectsOutput.value}

ATS Keywords:
${resumeKeywordsOutput.value}
  `.trim();

  if (
    !resumeSummaryOutput.value.trim() &&
    !resumeExperienceOutput.value.trim() &&
    !resumeProjectsOutput.value.trim() &&
    !resumeKeywordsOutput.value.trim()
  ) {
    showStatus("Nothing to download yet.", "error");
    return;
  }

  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "ai-job-copilot-resume-pack.txt";
  a.click();
  URL.revokeObjectURL(url);

  showStatus("Resume pack downloaded.", "success");
});

resumeDownloadFullBtn.addEventListener("click", async () => {
  const fullResume = `
${resumeName.value}
${resumeLocation.value} | ${resumeEmail.value} | ${resumeLinkedin.value}

TARGET COUNTRY / JOB MARKET
${resumeCountry.value}

PROFESSIONAL SUMMARY
${resumeSummaryOutput.value}

EXPERIENCE
${resumeExperienceOutput.value}

PROJECTS
${resumeProjectsOutput.value}

KEY SKILLS
${resumeKeywordsOutput.value}
  `.trim();

  if (
    !resumeSummaryOutput.value.trim() &&
    !resumeExperienceOutput.value.trim() &&
    !resumeProjectsOutput.value.trim() &&
    !resumeKeywordsOutput.value.trim()
  ) {
    showStatus("Nothing to download yet.", "error");
    return;
  }

  const blob = new Blob([fullResume], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "optimized-full-resume.txt";
  a.click();
  URL.revokeObjectURL(url);

  showStatus("Full resume downloaded.", "success");
});

resumeClearBtn.addEventListener("click", async () => {
  resumeName.value = "";
  resumeLocation.value = "";
  resumeEmail.value = "";
  resumeLinkedin.value = "";
  resumeRole.value = "";
  resumeCountry.value = "United Kingdom";
  resumeInputText.value = "";
  resumeJD.value = "";
  resumeSummaryOutput.value = "";
  resumeExperienceOutput.value = "";
  resumeProjectsOutput.value = "";
  resumeKeywordsOutput.value = "";

  await chrome.storage.local.remove([
    "resumeName",
    "resumeLocation",
    "resumeEmail",
    "resumeLinkedin",
    "resumeRole",
    "resumeCountry",
    "resumeInputText",
    "resumeJD",
    "resumeSummaryOutput",
    "resumeExperienceOutput",
    "resumeProjectsOutput",
    "resumeKeywordsOutput"
  ]);

  showStatus("Resume fields cleared.", "success");
});

// ---------- Message copy/download/clear ----------
copyConnectionBtn.addEventListener("click", async () => {
  await copyText(connectionMessageOutput.value, "Connection message copied.");
});

copyOutreachBtn.addEventListener("click", async () => {
  await copyText(outreachMessageOutput.value, "Outreach message copied.");
});

copyFollowupBtn.addEventListener("click", async () => {
  await copyText(followupMessageOutput.value, "Follow-up message copied.");
});

messageCopyAllBtn.addEventListener("click", async () => {
  const combinedText = `
CONNECTION MESSAGE:
${connectionMessageOutput.value}

OUTREACH MESSAGE:
${outreachMessageOutput.value}

FOLLOW-UP MESSAGE:
${followupMessageOutput.value}
  `.trim();

  await copyText(combinedText, "Message pack copied.");
});

messageDownloadBtn.addEventListener("click", async () => {
  const content = `
AI Job Copilot - Hiring Manager Messages

Target Role:
${messageRole.value}

Company:
${messageCompany.value}

Connection Message:
${connectionMessageOutput.value}

Outreach Message:
${outreachMessageOutput.value}

Follow-up Message:
${followupMessageOutput.value}
  `.trim();

  if (
    !connectionMessageOutput.value.trim() &&
    !outreachMessageOutput.value.trim() &&
    !followupMessageOutput.value.trim()
  ) {
    showStatus("Nothing to download yet.", "error");
    return;
  }

  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "hiring-manager-messages.txt";
  a.click();
  URL.revokeObjectURL(url);

  showStatus("Message pack downloaded.", "success");
});

messageClearBtn.addEventListener("click", async () => {
  messageRole.value = "";
  messageCompany.value = "";
  messageManager.value = "";
  messageJobContext.value = "";
  messageBackground.value = "";
  connectionMessageOutput.value = "";
  outreachMessageOutput.value = "";
  followupMessageOutput.value = "";

  await chrome.storage.local.remove([
    "messageRole",
    "messageCompany",
    "messageManager",
    "messageJobContext",
    "messageBackground",
    "connectionMessageOutput",
    "outreachMessageOutput",
    "followupMessageOutput"
  ]);

  showStatus("Message fields cleared.", "success");
});

// ---------- Job alert copy/clear ----------
copyJobAlertPreviewBtn.addEventListener("click", async () => {
  const combinedText = `
SUBJECT:
${jobAlertPreviewSubject.value}

BODY:
${jobAlertPreviewBody.value}
  `.trim();

  await copyText(combinedText, "Job alert preview copied.");
});

clearJobAlertBtn.addEventListener("click", async () => {
  jobAlertEmail.value = "";
  jobAlertRole.value = "";
  jobAlertCountry.value = "United Kingdom";
  jobAlertCity.value = "";
  jobAlertExperienceLevel.value = "";
  jobAlertKeywords.value = "";
  jobAlertTime.value = "09:00";
  jobAlertPreviewSubject.value = "";
  jobAlertPreviewBody.value = "";

  await chrome.storage.local.remove([
    "jobAlertEmail",
    "jobAlertRole",
    "jobAlertCountry",
    "jobAlertCity",
    "jobAlertExperienceLevel",
    "jobAlertKeywords",
    "jobAlertTime",
    "jobAlertPreviewSubject",
    "jobAlertPreviewBody"
  ]);

  showStatus("Job alert fields cleared.", "success");
});
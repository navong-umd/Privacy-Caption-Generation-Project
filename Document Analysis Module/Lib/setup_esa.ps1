# === Step 1: Check Java Installation ===
if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    Write-Output "Java not found. Please install Java from: https://www.oracle.com/java/technologies/javase-jdk11-downloads.html"
    exit 1
} else {
    Write-Output "Java is already installed."
}

# === Step 2: Set up Paths ===
$ESA_ROOT = "C:\Users\2015n\OneDrive\Desktop\Static Code Analysis\Document Analysis Module"
$REPO_URL = "https://github.com/ticcky/esalib.git"
$CLONE_PATH = "$ESA_ROOT\esalib"

# === Step 3: Clean existing folder if it exists ===
if (Test-Path $CLONE_PATH) {
    Write-Output "Removing existing ESA folder..."
    Remove-Item -Recurse -Force $CLONE_PATH
}

# === Step 4: Clone the ESA library ===
Write-Output "Cloning ESA library from GitHub..."
git clone $REPO_URL $CLONE_PATH

# === Step 5: Change to cloned folder ===
Set-Location $CLONE_PATH

# === Step 6: Copy example DB to working DB ===
$DB_SOURCE = "$CLONE_PATH\example\esa_en.db"
$DB_DEST = "$CLONE_PATH\esa_db.db"

if (Test-Path $DB_SOURCE) {
    Write-Output "Copying database file..."
    Copy-Item $DB_SOURCE -Destination $DB_DEST -Force
} else {
    Write-Output "ERROR: esa_en.db not found in example folder."
    exit 1
}

Write-Output "ESA setup completed successfully."

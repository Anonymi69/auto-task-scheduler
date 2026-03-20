# auto-task-scheduler

A Python script to automatically create a **hidden, persistent task** in Windows using the built-in Task Scheduler.

---

## ⚠️ Disclaimer

This project is for **educational purposes only**.
I am **not responsible** for any misuse or malicious use of this script. Use at your own risk.

---

## ⚙️ Features

* Creates scheduled tasks automatically
* Runs silently in the background
* Uses Windows built-in Task Scheduler
* Supports persistence across reboots

---

## ⚠️ Important

**This script must always be run as Administrator** to create tasks successfully in Windows.

---

## 🚀 Installation & Usage

Clone the repo, navigate into it, install dependencies, and run the script:

```bash id="step1"
git clone https://github.com/Anonymi69/auto-task-scheduler.git
cd auto-task-scheduler
pip install -r requirements.txt
```

Example:

```bash id="step2"
python main.py <target.exe>
```

---

## 📦 Convert to EXE (Recommended)

To make the script work across different computers, convert it into an executable using **PyInstaller**:

```bash id="step3"
pip install pyinstaller
pyinstaller --onefile --noconsole main.py
```

After compilation, run the EXE with your target:

```bash id="step4"
main.exe <target.exe>
```

**Remember:** Always run the EXE as Administrator.

---

## ⭐ Support

If you find this useful, consider giving the repo a star ⭐

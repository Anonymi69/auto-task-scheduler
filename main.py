import sys
import os
import getpass
import logging
import pywintypes
import win32com.client
import win32api

try:
    import pywin32_bootstrap
except ImportError:
    pass

TASK_TRIGGER_BOOT = 8
TASK_ACTION_EXEC = 0
TASK_CREATE_OR_UPDATE = 6
TASK_LOGON_S4U = 2
TASK_RUNLEVEL_HIGHEST = 1
FOLDER_NAME = "SystemServices"
TASK_NAME = "WindowsSystemMonitor"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

def get_scheduler() -> win32com.client.Dispatch:
    scheduler = win32com.client.Dispatch("Schedule.Service")
    scheduler.Connect()
    return scheduler

def ensure_folder(scheduler, folder_name: str):
    root = scheduler.GetFolder("\\")
    try:
        return root.GetFolder("\\" + folder_name)
    except pywintypes.com_error:
        return root.CreateFolder(folder_name)

def create_task(scheduler, folder, exe_path: str):
    task_def = scheduler.NewTask(0)

    try:
        username = win32api.GetUserNameEx(win32api.NameSamCompatible)
    except Exception:
        username = getpass.getuser()

    task_def.RegistrationInfo.Description = f"Auto start {TASK_NAME}"

    s = task_def.Settings
    s.Enabled = True
    s.Hidden = True
    s.StartWhenAvailable = True
    s.DisallowStartIfOnBatteries = False
    s.StopIfGoingOnBatteries = False
    s.ExecutionTimeLimit = ""
    s.RestartInterval = "PT30S"
    s.RestartCount = 999

    trigger = task_def.Triggers.Create(TASK_TRIGGER_BOOT)
    trigger.Enabled = True

    action = task_def.Actions.Create(TASK_ACTION_EXEC)
    action.Path = exe_path
    action.WorkingDirectory = os.path.dirname(exe_path)

    principal = task_def.Principal
    principal.UserId = username
    principal.RunLevel = TASK_RUNLEVEL_HIGHEST
    principal.LogonType = TASK_LOGON_S4U

    folder.RegisterTaskDefinition(
        TASK_NAME,
        task_def,
        TASK_CREATE_OR_UPDATE,
        username,
        "",
        TASK_LOGON_S4U,
    )

def main():
    if len(sys.argv) != 2:
        script = os.path.basename(sys.argv[0])
        print(f"Usage: {script} <path_to_exe>")
        sys.exit(1)

    exe_path = os.path.abspath(sys.argv[1])

    if not os.path.exists(exe_path):
        log.error(f"File not found: {exe_path}")
        sys.exit(1)

    if not exe_path.lower().endswith(".exe"):
        log.error("Target must be an .exe file.")
        sys.exit(1)

    try:
        scheduler = get_scheduler()
        folder = ensure_folder(scheduler, FOLDER_NAME)
        create_task(scheduler, folder, exe_path)
    except pywintypes.com_error as e:
        log.error(f"COM error: {e}. Make sure you're running as Administrator.")
        sys.exit(1)
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        sys.exit(1)

    log.info("Task created/updated successfully.")
    log.info(f"Folder : \\{FOLDER_NAME}")
    log.info(f"Task   : {TASK_NAME}")
    log.info(f"Target : {exe_path}")

if __name__ == "__main__":
    main()

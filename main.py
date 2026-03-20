import sys
import os
import getpass
import logging
import pywintypes
import win32com.client

TASK_TRIGGER_LOGON = 9
TASK_ACTION_EXEC = 0
TASK_CREATE_OR_UPDATE = 6
TASK_LOGON_INTERACTIVE_TOKEN = 3
TASK_RUNLEVEL_HIGHEST = 1
FOLDER_NAME = "SystemServices"

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
        log.info(f"Folder '\\{folder_name}' not found, creating it.")
        return root.CreateFolder(folder_name)

def create_task(scheduler, folder, task_name: str, exe_path: str, run_highest: bool = True):
    task_def = scheduler.NewTask(0)
    username = getpass.getuser()

    task_def.RegistrationInfo.Description = f"Auto start {task_name}"

    s = task_def.Settings
    s.Enabled = True
    s.Hidden = True
    s.StartWhenAvailable = True
    s.DisallowStartIfOnBatteries = False
    s.StopIfGoingOnBatteries = False
    s.ExecutionTimeLimit = "PT0S"

    trigger = task_def.Triggers.Create(TASK_TRIGGER_LOGON)
    trigger.Enabled = True
    trigger.UserId = username

    action = task_def.Actions.Create(TASK_ACTION_EXEC)
    action.Path = exe_path
    action.WorkingDirectory = os.path.dirname(exe_path)

    principal = task_def.Principal
    principal.UserId = username
    principal.LogonType = TASK_LOGON_INTERACTIVE_TOKEN
    if run_highest:
        principal.RunLevel = TASK_RUNLEVEL_HIGHEST

    folder.RegisterTaskDefinition(
        task_name,
        task_def,
        TASK_CREATE_OR_UPDATE,
        "",
        "",
        TASK_LOGON_INTERACTIVE_TOKEN,
    )

def main():
    if len(sys.argv) != 2:
        script = os.path.basename(sys.argv[0])
        print(f"Usage: python {script} <path_to_exe>")
        sys.exit(1)

    exe_path = os.path.abspath(sys.argv[1])

    if not os.path.exists(exe_path):
        log.error(f"File not found: {exe_path}")
        sys.exit(1)

    if not exe_path.lower().endswith(".exe"):
        log.error("Target must be an .exe file.")
        sys.exit(1)

    app_name = os.path.splitext(os.path.basename(exe_path))[0]
    task_name = f"{app_name}_Service"

    try:
        scheduler = get_scheduler()
        folder = ensure_folder(scheduler, FOLDER_NAME)
        create_task(scheduler, folder, task_name, exe_path)
    except pywintypes.com_error as e:
        log.error(f"COM error: {e}. Make sure you're running as Administrator.")
        sys.exit(1)
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        sys.exit(1)

    log.info("Task created/updated successfully.")
    log.info(f"Folder : \\{FOLDER_NAME}")
    log.info(f"Task   : {task_name}")
    log.info(f"Target : {exe_path}")

if __name__ == "__main__":
    main()

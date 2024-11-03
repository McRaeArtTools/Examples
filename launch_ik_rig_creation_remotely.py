"""Launch the process to create the IKRig and it's other components."""

import os
import sys
sys.path.append(r'C:\DD\PU_V3\CustomEngines\UV52\5_3_1_Vanilla_E1\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python')
import remote_execution as remote

if "ALLOW_DD_DEV" in os.environ:
    sys.path.insert(0,r"C:\DD_Dev\common\python\dd_unreal")
    sys.path.insert(0,r"C:\DD_Dev\common\python")
    sys.path.insert(0,r"C:\DD_Dev\common\perforce")
elif not [x for x in sys.path if x.endswith('dd_unreal')]:
    sys.path.append(r"C:\DD\common\python\dd_unreal")


def main():
    """Send the IKRig Creation and Animation transfer remotely.
    """
    ik_rig_creation_script = r"C:\DD_Dev\common\python\dd_unreal\dd_unreal_auto_ik_retargeter\setup_cal_test.py"

    remote_exec = remote.RemoteExecution()
    remote_exec.stop()  # Stops any existing connections that may exist from old jobs that did not have a stop
    # Attempt to open the socket connection to Unreal and send the various remote commands
    # Starts the remote execution connection
    remote_exec.start()
    remote_exec.open_command_connection(remote_exec.remote_nodes)
    remote_exec.run_command(command=ik_rig_creation_script, unattended=False, raise_on_failure=True)
    # Stops the newly created connection after command execution
    remote_exec.stop()


if __name__ == "__main__":
    main()

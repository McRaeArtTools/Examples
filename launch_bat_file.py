# Copyright (c) Digital Dimension. 2024
# All Rights Reserved.
"""Launch bat file to launch remote python execution."""

import os
import subprocess


def main(skeletal_mesh_name, asset_prefix, asset_type, skeletal_mesh_root_folder, asset_shortname):
    """Launch a detached batch process that will connect to Unreal remotely to send python modules to be executed.
    
    :param skeletal_mesh_name: Name of the asset that is selected in the content browser.
    :type skeletal_mesh_name: str

    :param skeletal_mesh_root_folder: Root folder that the selected asset exists in.
    :type skeletal_mesh_root_folder: str
    """
    os.environ["SKELETAL_MESH_NAME"] = skeletal_mesh_name
    os.environ["ASSET_PREFIX"] = asset_prefix
    os.environ["ASSET_TYPE"] = asset_type
    os.environ["SKELETAL_MESH_ROOT_FOLDER"] = skeletal_mesh_root_folder
    os.environ["ASSET_SHORTNAME"] = asset_shortname
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.Popen(["C:\DD_Dev\common\python\dd_unreal\dd_unreal_auto_ik_retargeter\launch_remote_python.bat"], startupinfo=si)

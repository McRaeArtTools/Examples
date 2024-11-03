"""Uses a IKRetargerer uasset to export animation from a source IKRig to a target IKRig."""

import os
import sys

import unreal

sys.path.append(os.path.dirname(__file__))
sys.path.insert(0,r"C:\DD_Dev\common\python\dd_unreal")
sys.path.insert(0,r"C:\DD_Dev\common\python")
sys.path.insert(0,r"C:\DD_Dev\common\perforce")

if sys.version_info.major == 3:
    from importlib import reload
    sys.path.insert(0, r"R:\Production\Tools\0_Vault\it_tools\tools_config\SYSTEM\SOFTWARE\PYTHON\3.10.4\Windows_NT.x64\Lib\site-packages")

import create_ik_rig as ddcir
import create_ik_retargeter as ddcirt
import retargeter_animation_transfer as ddrat
sys.path.insert(0,r"C:\DD_Dev\common\python\dd_unreal")
import unreal_scripting_setup_turntable as usst
import unreal_scripting_lib_source_control as ussc
reload(ddcir)
reload(ddcirt)
reload(ddrat)
reload(usst)
reload(ussc)


level_sequence_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
editor_asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)


def findBaseActor():
    """Find the turntable actor, which is used in the turntable sequence that rotates it 360 degrees."""
    base_actor = None
    level_actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    for level_actor in level_actors:
        if level_actor.get_actor_label() == "Asset":
            base_actor = level_actor
            break
    return base_actor


def muteControlRigTrack(skeletal_mesh_name, level_sequence):
    """Find the ControlRigTrack and remove it so it doesn't overwrite animation.

    :param skeletal_mesh_name: Name of the asset that is selected in the content browser.
    :type skeletal_mesh_name: str

    :param level_sequence: A LevelSequence.
    :type level_sequence: :class:`LevelSequence`
    """
    binding_by_names_dict = {str(_bind.get_display_name()): _bind for _bind in level_sequence.get_bindings()}
    actor_binding = binding_by_names_dict[skeletal_mesh_name]
    for track in actor_binding.get_tracks():
        if track.get_sections():
            if track.get_class().get_name() == "MovieSceneControlRigParameterTrack":
                actor_binding.remove_track(track)


def setAnimationTrack(skeletal_mesh_name, level_sequence, cal_test_animation):
    """Find the ControlRigTrack and remove it so it doesn't overwrite animation.

    :param skeletal_mesh_name: Name of the asset that is selected in the content browser.
    :type skeletal_mesh_name: str

    :param level_sequence: A LevelSequence.
    :type level_sequence: :class:`LevelSequence`

    :param cal_test_animation: A AnimSequence.
    :type cal_test_animation: :class:`AnimSequence`
    """
    binding_by_names_dict = {str(_bind.get_display_name()): _bind for _bind in level_sequence.get_bindings()}
    actor_binding = binding_by_names_dict[skeletal_mesh_name]

    animation_track = actor_binding.add_track(unreal.MovieSceneSkeletalAnimationTrack)
    animation_section = animation_track.add_section()
    animation_section.set_start_frame_bounded(True)
    animation_section.set_end_frame_bounded(True)

    loaded_anim_sequence = editor_asset_subsystem.load_asset(asset_path=cal_test_animation)
    animation_section.get_editor_property('params').set_editor_property('animation', loaded_anim_sequence)


def main(skeletal_mesh_name, asset_prefix, asset_type, skeletal_mesh_root_folder, asset_shortname):
    """Initializes all of the classes required to transfer animation loops between skeletal meshes.

    :param skeletal_mesh_name: Name of the asset that is selected in the content browser.
    :type skeletal_mesh_name: str

    :param skeletal_mesh_root_folder: Root folder that the selected asset exists in.
    :type skeletal_mesh_root_folder: str
    """
    source_skeletal_mesh = '/Game/Library/Packs/FluidFlux/Demo/Mannequin/Mesh/SK_Mannequin.SK_Mannequin'
    target_skeletal_mesh = '{skeletal_mesh_root_folder}/{skeletal_mesh_name}.{skeletal_mesh_name}'.format(skeletal_mesh_root_folder=skeletal_mesh_root_folder, skeletal_mesh_name=skeletal_mesh_name)

    # Initializes the IKRig creation class
    createIKRig = ddcir.CreateIKRig()
    if source_skeletal_mesh:
        source_skeletal_mesh_root_folder = ddcir.get_asset_root(source_skeletal_mesh)
        generated_source_ik_rig = createIKRig.main(source_skeletal_mesh, source_skeletal_mesh_root_folder)
        ussc.saveAssetsLocally([str(generated_source_ik_rig)], sc_state_to_expect_is_enabled=True)
    if target_skeletal_mesh:
        target_skeletal_mesh_root_folder = ddcir.get_asset_root(target_skeletal_mesh)
        generated_target_ik_rig = createIKRig.main(target_skeletal_mesh, target_skeletal_mesh_root_folder)
        ussc.saveAssetsLocally([str(generated_target_ik_rig)], sc_state_to_expect_is_enabled=True)

    # Initialize the Retargeter generator and return generated IKRetargeter uasset
    createIKRetargeter = ddcirt.CreateIKRetargeter()
    generated_ik_retargeter = createIKRetargeter.main(source_skeletal_mesh, target_skeletal_mesh)
    ussc.saveAssetsLocally([str(generated_ik_retargeter)], sc_state_to_expect_is_enabled=True)

    # Use the generated retargeter and batch all the animations to the new skeleton
    animationRetargeter = ddrat.AnimationRetargeter()
    cal_test_animation = animationRetargeter.main(generated_ik_retargeter=generated_ik_retargeter, target_base_folder=skeletal_mesh_root_folder)

    # Duplicate the level and sequence from the Calisthenics default
    usst.performCopyTTForAsset(
        asset_shortname=asset_shortname, 
        asset_prefix=asset_prefix, 
        sg_asset_type=asset_type, 
        asset_content_browser_folderpath=skeletal_mesh_root_folder, 
        is_for_cal=True
    )

    # Find the SkeletalMesh Actor and add animation to it
    base_actor = findBaseActor()
    if base_actor.get_attached_actors():
        skeletal_mesh_actor = base_actor.get_attached_actors()

    # Get a reference to the Unreal Editor's Level Sequence Editor
    level_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    if skeletal_mesh_actor and level_sequence:
        level_sequence_editor_subsystem.add_actors(skeletal_mesh_actor)
        muteControlRigTrack(
            skeletal_mesh_name=skeletal_mesh_name, 
            level_sequence=level_sequence
        )
        setAnimationTrack(
            skeletal_mesh_name=skeletal_mesh_name, 
            level_sequence=level_sequence, 
            cal_test_animation=cal_test_animation
        )

if __name__ == "__main__":
    skeletal_mesh_name = os.environ.get("SKELETAL_MESH_NAME")
    asset_prefix = os.environ["ASSET_PREFIX"]
    asset_type = os.environ["ASSET_TYPE"]
    skeletal_mesh_root_folder = os.environ.get("SKELETAL_MESH_ROOT_FOLDER")
    asset_shortname = os.environ["ASSET_SHORTNAME"]
    main(skeletal_mesh_name, asset_prefix, asset_type, skeletal_mesh_root_folder, asset_shortname)

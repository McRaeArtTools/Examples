# Copyright (c) Digital Dimension. 2024
# All Rights Reserved.
"""Create a IKRetargeter uasset from two IKRig uassets that will be used to batch retarget animation from one to another."""

import unreal


asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
editor_asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)


def get_asset_root(skeletal_mesh):
    """Manipulate skeletal mesh path string to return the folder path.
    
    :param skeletal_mesh: SkeletalMesh uasset path.
    :type skeletal_mesh: str

    :return: Path to the folder a uasset is stored in.
    :rtype: str
    """
    uasset_split_string = '/' + skeletal_mesh.split('/')[-1] # '/Game/Library/Packs/FluidFlux/Demo/Mannequin/Mesh/SK_Mannequin.SK_Mannequin'
    return skeletal_mesh.split(uasset_split_string)[0] # '/Game/Library/Packs/FluidFlux/Demo/Mannequin/Mesh'


class CreateIKRetargeter(object):
    """Class used to create the IKRetargeter uasset."""

    def createIkRetargeter(self):
        """Generate a IKRig uasset."""
        # Creates the retargeter in the target uasset folder
        self.generated_ik_retargeter = asset_tools.create_asset(
            asset_name='GeneratedIKRetargeter',
            package_path=self.target_skeletal_mesh_root_folder,
            asset_class=unreal.IKRetargeter,
            factory=unreal.IKRetargetFactory()
        )
    
    def getRetargeterController(self):
        # Get the IK Retargeter controller.
        self.retargeter_controller = unreal.IKRetargeterController.get_controller(self.generated_ik_retargeter)

    def setRetargeterSourceAndTarget(self):
        # Load the Source and Target IK Rigs.
        # ['/Game/Library/Packs/FluidFlux/Demo/Mannequin/Mesh/SK_Mannequin.SK_Mannequin', '/Game/Assets/Character/CHA_Pv4Test/CHA_Pv4Test_Main__Standard/Modeling/Meshes/v000/SK_CHA_Pv4Test_Main__Standard_Modeling.SK_CHA_Pv4Test_Main__Standard_Modeling']
        source_ik_rig = editor_asset_subsystem.load_asset(asset_path=self.source_skeletal_mesh_root_folder + '/GeneratedIKRig')
        target_ik_rig = editor_asset_subsystem.load_asset(asset_path=self.target_skeletal_mesh_root_folder + '/GeneratedIKRig')

        # Assign the Source and Target IK Rigs.
        self.retargeter_controller.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source_ik_rig)
        self.retargeter_controller.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, target_ik_rig)

        # Map the chains of the source IKRig to the Target IKRig
        self.retargeter_controller.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)

    def main(self, source_skeletal_mesh, target_skeletal_mesh):
        """Generate a IKRetargeter using two IKRig uassets.
        
        :param source_skeletal_mesh: Full unreal filepath to the source skeletal mesh uasset.
        :type source_skeletal_mesh: str

        :param target_skeletal_mesh: Full unreal filepath to the target skeletal mesh uasset.
        :type target_skeletal_mesh: str

        :return: IK Retargeter uasset.
        :rtype: :class:`unreal.IKRetargeter`
        """
        # '/Game/MetaHumans/Common/Female/Tall/OverWeight/Body/f_tal_ovw_body.f_tal_ovw_body'
        # target_skeletal_mesh = '/Game/Assets/Character/CHA_Pv4Test/CHA_Pv4Test_Main__Standard/Modeling/Meshes/v000/SK_CHA_Pv4Test_Main__Standard_Modeling.SK_CHA_Pv4Test_Main__Standard_Modeling'
        self.source_skeletal_mesh_root_folder = get_asset_root(source_skeletal_mesh)
        self.target_skeletal_mesh_root_folder = get_asset_root(target_skeletal_mesh)

        self.createIkRetargeter()
        self.getRetargeterController()
        self.setRetargeterSourceAndTarget()
        return self.generated_ik_retargeter

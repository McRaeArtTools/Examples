"""Uses a IKRetargerer uasset to export animation from a source IKRig to a target IKRig."""

import unreal


asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
editor_asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)


class AnimationRetargeter(object):
    """Class used to create the IKRetargeter uasset."""

    def getAnimSequences(self):
        """Search content browser for available animations for transfer."""
        # Filter all uassets in specified folder to only retrieve uassets of class `unreal.AnimSequence`
        anim_sequence_filter = unreal.ARFilter(
            class_names=['AnimSequence'], 
            package_paths=[self.source_ik_rig_animation_folder], 
            recursive_classes=True
        )
        anim_sequences = unreal.AssetRegistryHelpers.get_asset_registry().get_assets(anim_sequence_filter)

        # Loop through all anim sequences and only add unique entities to list
        self.unique_anim_sequences = []
        for anim_sequence in anim_sequences:
            if 'Thriller_Part_2' in str(anim_sequence.get_editor_property('asset_name')):
                if anim_sequence not in self.unique_anim_sequences:
                    self.unique_anim_sequences.append(anim_sequence)
    
    def batchRetargetAnimation(self):
        """Loop through all the chosen animation sequences and retarget them to the target mesh."""
        self.duplicated_animations = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
            assets_to_retarget=self.unique_anim_sequences,
            source_mesh=None,
            target_mesh=None,
            ik_retarget_asset=self.generated_ik_retargeter,
            search='',
            replace='',
            prefix='',
            suffix="",
            remap_referenced_assets=True
        )        

    def moveAnimations(self):
        """Save all the retargeted animations to the correct "Animations" folder where it originated."""
        for duplicated_animation in self.duplicated_animations:
            self.destination_asset_path = self.target_ik_rig_animation_folder + '/' + str(duplicated_animation.asset_name)
            editor_asset_subsystem.rename_asset(source_asset_path=duplicated_animation.package_name, destination_asset_path=self.destination_asset_path)

    def main(self, generated_ik_retargeter, target_base_folder):
        """Export animation from a source IKRig to a target IKRig.
        
        :param: Auto-generated IK Retargeter uasset.
        :type: :class:`unreal.IKRetargeter`
        """
        self.generated_ik_retargeter = generated_ik_retargeter
        # Animation source folder to search through
        self.source_ik_rig_animation_folder = '/Game/Library/Packs/FluidFlux/Demo/Mannequin/Animations'
        self.target_ik_rig_animation_folder = target_base_folder + '/Animations'

        self.getAnimSequences()
        self.batchRetargetAnimation()
        self.moveAnimations()

        return self.destination_asset_path

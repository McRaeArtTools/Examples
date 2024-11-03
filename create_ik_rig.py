"""Create a IKRig uasset from a SkeletalMesh uasset that will be used to retarget animation from another IKRig usasset."""

import re

import unreal


asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
ik_rig_controller_tools = unreal.IKRigController()


def get_asset_root(skeletal_mesh):
    """Manipulate skeletal mesh path string to return the folder path.
    
    :param skeletal_mesh: SkeletalMesh uasset path.
    :type skeletal_mesh: str

    :return: Path to the folder a uasset is stored in.
    :rtype: str
    """
    uasset_split_string = '/' + skeletal_mesh.split('/')[-1] # '/Game/Library/Packs/FluidFlux/Demo/Mannequin/Mesh/SK_Mannequin.SK_Mannequin'
    return skeletal_mesh.split(uasset_split_string)[0] # '/Game/Library/Packs/FluidFlux/Demo/Mannequin/Mesh'


def create_temp_control_rig(loaded_skeletal_mesh):
    """Create/Update the Control Rig asset from an existing SkeletalMesh.

    :param loaded_skeletal_mesh: Loaded SkeletalMesh uasset.
    :type loaded_skeletal_mesh: :class:`unreal.SkeletalMesh`

    :return: Loaded ControlRig uasset.
    :rtype: :class:`unreal.ControlRig`
    """
    temp_control_rig_reference = unreal.ControlRigBlueprintFactory.create_control_rig_from_skeletal_mesh_or_skeleton(loaded_skeletal_mesh)
    return temp_control_rig_reference


def get_all_bones(temp_control_rig_reference):
    """Loop through all of the bones in the ControlRig Hierarchy and create a list of unique bones.
    
    :param temp_control_rig_reference: Loaded ControlRig uasset.
    :type temp_control_rig_reference: :class:`unreal.ControlRig`

    :return: List of unique bone names.
    :rtype: list of str
    """
    unique_bone_names = []
    control_rig_hierarchy = temp_control_rig_reference.get_hierarchy_controller().get_hierarchy()
    for element in control_rig_hierarchy.get_bones():
        if element.type == unreal.RigElementType.BONE:
            if element.name not in unique_bone_names:
                unique_bone_names.append(str(element.name))
    return unique_bone_names


def get_rig_side_values(rig_side):
    """Create two values based on the string side given and return standardized results.
    
    :param rig_side: Name of the rig side to create a dict for.
    :type rig_side: str

    :return: Short form of the rig side.
    :rtype: str

    :return: Long form of the rig side.
    :rtype: str
    """
    if rig_side.lower() == 'left':
        side_short = 'l'
        side_long = 'Left'
    elif rig_side.lower() == 'right':
        side_short = 'r'
        side_long = 'Right'
    return side_short, side_long


def get_extremities_chain_bones(
    side_short, 
    side_long, 
    unique_bone_names, 
    valid_chain_start_bones, 
    valid_chain_end_bones
):
    """Find two strings that will correspond to the start and end bone chains.
    
    :param side_short: Shortened string value of the rig side being searched for.
    :type side_short: str

    :param side_long: Extended string value of the rig side being searched for.
    :type side_long: str

    :param unique_bone_names: List of unique bone names.
    :type unique_bone_names: list of str

    :param valid_chain_start_bones: List of valid start bones for chain.
    :type valid_chain_start_bones: list of str

    :param valid_chain_end_bones: List of valid end bones for chain.
    :type valid_chain_end_bones: list of str

    :return: Name of the valid start bone that was found.
    :rtype: str

    :return: Name of the valid end bone that was found.
    :rtype: str
    """
    start_bone_name = ''
    end_bone_name = ''
    #TODO: Expand on this logic to catch more naming conventions
    # Loop through all unique bones in the skeleton
    for unique_bone_name in unique_bone_names:
        if '_' in unique_bone_name:
            #TODO: Provide examples
            # Loop through all valid start joints to create a start chain
            for chain_bone in valid_chain_start_bones:
                if chain_bone in unique_bone_name:
                    unique_bone_name_split = unique_bone_name.split('_')
                    # Ensure that there is only 1 underscore because there may be extra support bones with similar names
                    if side_short in unique_bone_name_split and len(unique_bone_name_split) == 2:
                        start_bone_name = unique_bone_name
                        break
            #TODO: Provide examples
            # Loop through all valid end joints to create a end chain
            for chain_bone in valid_chain_end_bones:
                if chain_bone in unique_bone_name:
                    unique_bone_name_split = unique_bone_name.split('_')
                    # Ensure that there is only 1 underscore because there may be extra support bones with similar names
                    if side_short in unique_bone_name_split and len(unique_bone_name_split) == 2:
                        end_bone_name = unique_bone_name
                        break
        else:
            # Intended Start/End Bones: LeftArm, LeftHand
            # Intended Start/End Bones: LeftUpLeg, LeftFoot
            # Loop through all valid start joints to create a start chain
            for chain_bone in valid_chain_start_bones:
                chain_found = False
                side_found = False
                if chain_bone in unique_bone_name.lower():
                    if side_long in unique_bone_name:
                        for unique_split_side in unique_bone_name.split(side_long):
                            if chain_bone.lower() == unique_split_side.lower():
                                chain_found = True
                        for unique_chain_side in unique_bone_name.lower().split(chain_bone):
                            if side_long.lower() == unique_chain_side.lower():
                                side_found = True
                        # Ensure that there is only 1 underscore because there may be extra support bones with similar names
                        if chain_found and side_found:
                            start_bone_name = unique_bone_name
                            break
            # Loop through all valid end joints to create a end chain
            for chain_bone in valid_chain_end_bones:
                chain_found = False
                side_found = False
                if chain_bone in unique_bone_name.lower():
                    if side_long in unique_bone_name:
                        for unique_split_side in unique_bone_name.split(side_long):
                            if chain_bone.lower() == unique_split_side.lower():
                                chain_found = True
                        for unique_chain_side in unique_bone_name.lower().split(chain_bone):
                            if side_long.lower() == unique_chain_side.lower():
                                side_found = True
                        # Ensure that there is only 1 underscore because there may be extra support bones with similar names
                        if chain_found and side_found:
                            end_bone_name = unique_bone_name
                            break
    if start_bone_name and end_bone_name:
        return start_bone_name, end_bone_name


def get_center_column_chain_bones(
    unique_bone_names, 
    valid_chain_bone
):
    """Find two strings that will correspond to the start and end bone chains.

    :param unique_bone_names: List of unique bone names.
    :type unique_bone_names: list of str

    :param valid_chain_bone: Valid start and end bone for chain.
    :type valid_chain_bone: str

    :return: Name of the valid start bone that was found.
    :rtype: list of str

    :return: Name of the valid end bone that was found.
    :rtype: str
    """
    start_bone_name = ''
    end_bone_name = ''
    bones_in_chain = []
    valid_bones = []
    lowest_bone_number = None
    highest_bone_number = None
    stripped_bone_name = ''
    #TODO: Expand on this logic to catch more naming conventions
    # Loop through all unique bones in the skeleton
    for unique_bone_name in unique_bone_names:
        if valid_chain_bone.lower() in unique_bone_name.lower():
            if '_' in unique_bone_name:
                # This is here to catch bones who contain an underscore later
                if valid_bones:
                    valid_bones.append(unique_bone_name)
                #TODO: Provide examples
                unique_bone_name_split = unique_bone_name.split('_')
                # If the "unique_bone_name" has no underscores then we just use the bone name since it is alone
                if len(unique_bone_name_split) == 1:
                    start_bone_name = unique_bone_name
                    end_bone_name = unique_bone_name
                for split in unique_bone_name_split:
                    try: 
                        if int(split):
                            bones_in_chain.append(split)
                    except:
                        continue
            else:
                valid_bones.append(unique_bone_name)
    # Handles cases where first bone has no number and last bone does
    # Spine -> Spine2
    if len(valid_bones) == 2:
        start_bone_name = valid_bones[0]
        end_bone_name = valid_bones[-1]
    elif len(valid_bones) > 1:
        for valid_bone in valid_bones:
            bone_number = re.sub('[^\d.,]', '', valid_bone)
            if not bone_number:
                start_bone_name = valid_bone
                lowest_bone_number = 0
                stripped_bone_name = valid_bone
            if not stripped_bone_name and bone_number:
                stripped_bone_name = unique_bone_name.split(bone_number)[0]
            if not start_bone_name and not lowest_bone_number:
                lowest_bone_number = bone_number
            if bone_number:
                bone_number = int(bone_number)
                if not highest_bone_number and bone_number > lowest_bone_number:
                    highest_bone_number = bone_number
                if bone_number > highest_bone_number:
                    highest_bone_number = bone_number
        if not start_bone_name:
            start_bone_name = '{stripped_bone_name}{lowest_bone_number}'.format(stripped_bone_name=stripped_bone_name, lowest_bone_number=lowest_bone_number)
        end_bone_name = '{stripped_bone_name}{highest_bone_number}'.format(stripped_bone_name=stripped_bone_name, highest_bone_number=highest_bone_number)
        return start_bone_name, end_bone_name
    elif len(valid_bones) == 1:
        start_bone_name = valid_bones[0]
        end_bone_name = valid_bones[0]
    #TODO: Provide examples
    # Only one bone exists but it still had some versioning so we still only use the bone name with it's single version
    if len(bones_in_chain) == 1:
        start_bone_name = valid_chain_bone + '_{}'.format(bones_in_chain[0])
        end_bone_name = valid_chain_bone + '_{}'.format(bones_in_chain[0])
    #TODO: Provide examples
    # Get the first and last bone entries in the list for the start and end bones in the chain
    if len(bones_in_chain) > 1:
        start_bone_name = valid_chain_bone + '_{}'.format(bones_in_chain[0])
        end_bone_name = valid_chain_bone + '_{}'.format(bones_in_chain[-1])
    return start_bone_name, end_bone_name


def get_phalanges_chain_bones(
    side_short,
    side_long,
    unique_bone_names, 
    valid_chain_bone
):
    """Find two strings that will correspond to the start and end bone chains.

    :param side_short: Shortened string value of the rig side being searched for.
    :type side_short: str

    :param unique_bone_names: List of unique bone names.
    :type unique_bone_names: list of str

    :param valid_chain_bone: Valid start and end bone for chain.
    :type valid_chain_bone: str

    :return: Name of the valid start bone that was found.
    :rtype: list of str

    :return: Name of the valid end bone that was found.
    :rtype: str
    """
    underscore_naming_convention = False
    start_bone_name = ''
    end_bone_name = ''
    lowest_bone_number = None
    highest_bone_number = None
    phalange_bones = []
    stripped_bone_name = ''
    #TODO: Expand on this logic to catch more naming conventions
    # Loop through all unique bones in the skeleton
    for unique_bone_name in unique_bone_names:
        if '_' in unique_bone_name:
            if valid_chain_bone in unique_bone_name:
                underscore_naming_convention = True
                #TODO: Provide examples
                unique_bone_name_split = unique_bone_name.split('_')
                if side_short in unique_bone_name_split:
                    phalange_bones.append(unique_bone_name)
        else:
            # Example Bone Input: LeftHandIndex1
            if valid_chain_bone.lower() in unique_bone_name.lower() and side_long.lower() in unique_bone_name.lower():
                bone_number = re.sub('[^\d.,]' , '', unique_bone_name)
                if not stripped_bone_name:
                    stripped_bone_name = unique_bone_name.split(bone_number)[0]
                if not lowest_bone_number:
                    lowest_bone_number = bone_number
                if not highest_bone_number and bone_number > lowest_bone_number:
                    highest_bone_number = bone_number
                if lowest_bone_number and highest_bone_number:
                    if bone_number < lowest_bone_number:
                        lowest_bone_number = bone_number
                    if bone_number > highest_bone_number:
                        highest_bone_number = bone_number
    if underscore_naming_convention:
        start_bone_name = phalange_bones[0]
        end_bone_name = phalange_bones[-1]
    else:
        start_bone_name = '{stripped_bone_name}{lowest_bone_number}'.format(stripped_bone_name=stripped_bone_name, lowest_bone_number=lowest_bone_number)
        end_bone_name = '{stripped_bone_name}{highest_bone_number}'.format(stripped_bone_name=stripped_bone_name, highest_bone_number=highest_bone_number)
    
    return start_bone_name, end_bone_name


def create_chain_dict(
    rig_side, 
    chain_choice, 
    unique_bone_names
):
    """Create a dictionary containing all the arm chain data that will be needed in the IKRigDefinition.
    
    :param rig_side: Name of the rig side to create a dict for.
    :type rig_side: str

    :param chain_choice: Name of the chain to create a dict for.
    :type chain_choice: str

    :param unique_bone_names: List of unique bone names.
    :type unique_bone_names: list of str
    """
    side_long = ''
    # Ensure that the correct bone is chosen depending on the side queried
    if chain_choice == 'arm':
        side_short, side_long = get_rig_side_values(rig_side)
        valid_chain_start_bones = ['upperarm', 'arm']
        valid_chain_end_bones = ['hand', 'wrist']
        start_bone_name, end_bone_name = get_extremities_chain_bones(
            side_short, 
            side_long, 
            unique_bone_names, 
            valid_chain_start_bones, 
            valid_chain_end_bones
        )
    elif chain_choice == 'leg':
        side_short, side_long = get_rig_side_values(rig_side)
        valid_chain_start_bones = ['upperleg', 'thigh', 'upleg']
        valid_chain_end_bones = ['foot', 'heel']
        start_bone_name, end_bone_name = get_extremities_chain_bones(
            side_short, 
            side_long, 
            unique_bone_names, 
            valid_chain_start_bones, 
            valid_chain_end_bones
        )
    elif chain_choice == 'spine':
        valid_chain_bone = 'spine'
        start_bone_name, end_bone_name = get_center_column_chain_bones(
            unique_bone_names, 
            valid_chain_bone
        )
    elif chain_choice == 'neck':
        valid_chain_bone = 'neck'
        start_bone_name, end_bone_name = get_center_column_chain_bones(
            unique_bone_names, 
            valid_chain_bone
        )
    elif chain_choice == 'head':
        valid_chain_bone = 'head'
        start_bone_name, end_bone_name = get_center_column_chain_bones(
            unique_bone_names, 
            valid_chain_bone
        )
    elif chain_choice in ['index', 'middle', 'ring', 'pinky', 'thumb']:
        side_short, side_long = get_rig_side_values(rig_side)
        valid_chain_bone = chain_choice
        start_bone_name, end_bone_name = get_phalanges_chain_bones(
            side_short,
            side_long,
            unique_bone_names, 
            valid_chain_bone
        )
    else:
        unreal.log_warning('Invalid chain choice...')

    if start_bone_name and end_bone_name:
        chain_dict = {
        "chain_name": "{side_long}{chain_choice}".format(side_long=side_long, chain_choice=chain_choice.capitalize()),
        "start_bone_name": "{start_bone_name}".format(start_bone_name=start_bone_name),
        "end_bone_name": '{end_bone_name}'.format(end_bone_name=end_bone_name)
        }
        return chain_dict


def create_ik_goal(
    rig_side, 
    end_goal,
    chain_choice,
    ik_rig_controller,
    unique_bone_names
):
    """Create an IK Goal.
    
    :param rig_side: Name of the rig side to create a dict for.
    :type rig_side: str

    :param end_goal: Name of the IKGoal limb.
    :type end_goal: str

    :param chain_choice: Name of the chain to create a dict for.
    :type chain_choice: str

    :param ik_rig_controller: The IKRig Controller that is used to create chain and goals.
    :type ik_rig_controller: :class:`unreal.IKRigController`

    :param unique_bone_names: List of unique bone names.
    :type unique_bone_names: list of str

    :return: Name of the IKGoal that was created.
    :rtype: str
    """
    side_short, side_long = get_rig_side_values(rig_side)
    ik_bone_target = ''
    for unique_bone_name in unique_bone_names:
        if end_goal.lower() in unique_bone_name.lower():
            if '_' in unique_bone_name:
                unique_bone_name_split = unique_bone_name.split('_')
                #TODO: Change this logic eventually if we want to use specific IK bones
                if side_short in unique_bone_name_split or side_long in unique_bone_name_split:
                    if 'vb' not in unique_bone_name and ' ' not in unique_bone_name:
                        if 'ik' not in unique_bone_name:
                            ik_bone_target = unique_bone_name
            elif side_long.lower() in unique_bone_name.lower():
                if 'vb' not in unique_bone_name and ' ' not in unique_bone_name:
                    if 'ik' not in unique_bone_name:
                        ik_bone_target = unique_bone_name
    ik_goal_name = "{side_long}{end_goal}IK".format(side_long=side_long, end_goal=end_goal) # LeftHandIK
    ik_rig_controller.add_new_goal(goal_name=ik_goal_name, bone_name=ik_bone_target)
    chain_name = "{side_long}{chain_choice}".format(side_long=side_long, chain_choice=chain_choice.capitalize())
    ik_rig_controller.set_retarget_chain_goal(chain_name, ik_goal_name)
    return ik_goal_name


class CreateIKRig(object):
    """Class used to create the IKRig uassets from a SkeletalMesh uasset."""

    def getIkRigController(self):
        """Get the IK Rig controller uasset that was created."""
        self.ik_rig_controller = ik_rig_controller_tools.get_controller(self.generated_ik_rig)

    def getSkeletalMesh(self):
        """Set the skeletal mesh uasset inside the IKRig controller uasset."""
        self.active_skeletal_mesh = self.ik_rig_controller.get_skeletal_mesh()

    def createTemporaryControlRig(self):
        """Generate a ControlRig uasset from the skeletal mesh that will bed used to query the skeleton hierarchy."""
        self.temp_control_rig_reference = create_temp_control_rig(self.loaded_skeletal_mesh)

    def getAllBones(self):
        """Get a list of all the unique bones in the ControlRig hierarchy to use in chain creation."""
        self.unique_bone_names = get_all_bones(self.temp_control_rig_reference)
        self.root_bone = self.unique_bone_names[0]
        unreal.log_warning('self.root_bone: {}'.format(self.root_bone))

    def setRetargetRoot(self):
        """Set the skeletal mesh uasset inside the IKRig controller uasset."""
        self.ik_rig_controller.set_retarget_root(root_bone_name=self.root_bone)

    def setSkeletalMesh(self):
        """Set the skeletal mesh uasset inside the IKRig controller uasset."""
        self.ik_rig_controller.set_skeletal_mesh(skeletal_mesh=self.loaded_skeletal_mesh)

    def createChain(self):
        """Create all of the bone chains required to retarget animation between two IKRigs."""
        rig_sides = ['left', 'right']
        multi_side_chain_choices = ['arm', 'leg', 'index', 'middle', 'ring', 'pinky', 'thumb']
        chain_choices = ['spine', 'neck', 'head']
        for chain_choice in multi_side_chain_choices:
            for rig_side in rig_sides:
                chain_dict = create_chain_dict(rig_side=rig_side, chain_choice=chain_choice, unique_bone_names=self.unique_bone_names)
                self.ik_rig_controller.add_retarget_chain(chain_name=chain_dict["chain_name"], start_bone_name=chain_dict["start_bone_name"], end_bone_name=chain_dict["end_bone_name"], goal_name='')
        for chain_choice in chain_choices:
            chain_dict = create_chain_dict(rig_side=rig_side, chain_choice=chain_choice, unique_bone_names=self.unique_bone_names)
            self.ik_rig_controller.add_retarget_chain(chain_name=chain_dict["chain_name"], start_bone_name=chain_dict["start_bone_name"], end_bone_name=chain_dict["end_bone_name"], goal_name='')

    def createGoals(self):
        """Create all the goals that are needed for an accurate IK system."""
        self.ik_goals = []
        rig_sides = ['left', 'right']
        end_goals = ['Hand', 'Foot']
        for rig_side in rig_sides:
            for end_goal in end_goals:
                if end_goal == 'Hand':
                    chain_choice = 'Arm'
                elif end_goal == 'Foot':
                    chain_choice = 'Leg'
                ik_goal_name = create_ik_goal(
                    rig_side=rig_side, 
                    end_goal=end_goal,
                    chain_choice=chain_choice,
                    ik_rig_controller=self.ik_rig_controller,
                    unique_bone_names=self.unique_bone_names
                )
                if ik_goal_name not in self.ik_goals:
                    self.ik_goals.append(ik_goal_name)

    def createSolver(self):
        """Create the IK Solver that will house all the IK Goals that drive IK animation."""
        fbik_index = self.ik_rig_controller.add_solver(unreal.IKRigFBIKSolver)
        self.ik_rig_controller.set_root_bone(self.root_bone, 0)
        for ik_goal in self.ik_goals:
            self.ik_rig_controller.connect_goal_to_solver(ik_goal, fbik_index)

    def createIkRig(self):
        """Generate a IKRig uasset."""
        self.generated_ik_rig = asset_tools.create_asset(
            asset_name=self.ik_rig_blueprint_name,
            package_path=self.skeletal_mesh_root_folder,
            asset_class=unreal.IKRigDefinition,
            factory=unreal.IKRigDefinitionFactory()
        )
    
    def main(self, skeletal_mesh, skeletal_mesh_root_folder):
        """Generate a IKRig using the currently selected SkeletalMesh.
        
        :param skeletal_mesh: Name of the asset that is selected in the content browser.
        :type skeletal_mesh: str

        :param skeletal_mesh_root_folder: Root folder that the selected asset exists in.
        :type skeletal_mesh_root_folder: str

        :return: Generated IKRig.
        :rtype: :class:`unreal.IKRigDefinition`
        """
        self.unloaded_skeletal_mesh = skeletal_mesh
        self.loaded_skeletal_mesh = unreal.load_object(name=self.unloaded_skeletal_mesh, outer=None)
        self.skeletal_mesh_root_folder = skeletal_mesh_root_folder
        self.ik_rig_blueprint_name = 'GeneratedIKRig'
        ik_rig_expected_package_name = '{skeletal_mesh_root_folder}/{ik_rig_blueprint_name}.{ik_rig_blueprint_name}'.format(
            skeletal_mesh_root_folder=self.skeletal_mesh_root_folder, 
            ik_rig_blueprint_name=self.ik_rig_blueprint_name
        )

        # Only create a new IKRig uasset if it doesn't exist
        if not unreal.EditorAssetLibrary.does_asset_exist(ik_rig_expected_package_name):
            # IKRig Creation Steps
            self.createIkRig()
            self.getIkRigController()
            self.setSkeletalMesh()

            total_assets_to_load = 1
            text_label = "Creating Control Rig Now..."
            with unreal.ScopedSlowTask(total_assets_to_load, text_label) as slow_task:
                slow_task.make_dialog(True)
                for i in range(total_assets_to_load):
                    if slow_task.should_cancel():
                        break
                    slow_task.enter_progress_frame(1)
                # self.getSkeletalMesh()
                self.createTemporaryControlRig()

            #IKRig Setup Steps
            self.getAllBones()
            self.setRetargetRoot()
            self.createChain()

            # Create the solver and goals needed
            self.createGoals()
            self.createSolver()

            # Delete the ControlRig that was created since it was only needed to get all the bone names
            unreal.EditorAssetLibrary.delete_asset(self.temp_control_rig_reference.get_path_name()) # Do this last so that it does not get corrupted and not delete

            return self.generated_ik_rig
        # Load pre-existing IKRig uasset and return it so it can be used for retargeting
        else:
            unreal.log_warning('IKRig "{}" Already existed, skipping creation...'.format(ik_rig_expected_package_name))
            self.generated_ik_rig = unreal.load_object(name=ik_rig_expected_package_name, outer=None)
            return self.generated_ik_rig

from duplocli.terraform.common.tf_utils import TfUtils
from duplocli.terraform.common.tf_file_utils import TfFileUtils

from duplocli.terraform.providers.aws.tf_step1 import AwsTfImportStep1
from duplocli.terraform.providers.aws.tf_step2 import AwsTfImportStep2

from duplocli.terraform.providers.aws.aws_resources import AwsResources

from duplocli.terraform.tfbackup.backup_import_folders import BackupImportFolders

import os
class AwsTfSteps:
    only_step2 = False
    only_step1 = False
    def __init__(self, params):
        self.utils = TfUtils(params)
        self.file_utils = TfFileUtils(params)
        self.params = params

    ######### modules == tenant, infra or all customer objects ######
    def execute(self):
        self.pre_execute()
        ##  debug
        if self.only_step1 or self.only_step2 :
            for module in self.params.modules():  # infra and tenants in modules to export
                self.params.set_step_type(module)
                if self.only_step1:
                    self._step1_tf_state()
                else:
                    self._step2_tf_main()
            return [ self.params.temp_folder , self.params.import_name, self.params.zip_file_path+".zip"]
        ###
        # execute
        for module in self.params.modules(): # infra and tenants in modules to export
            self._module_execute(module)
        self.post_execute()
        return  [ self.params.temp_folder , self.params.import_name, self.params.zip_file_path+".zip"]


    def _init_step1(self):
        self.step1 = AwsTfImportStep1(self.params)
        return self.step1

    def _init_step2(self):
        self.step2 = AwsTfImportStep2(self.params)
        return self.step2

    def _module_execute(self, module):
        self.params.set_step_type(module)
        self._step1_tf_state()
        self._step2_tf_main()

    ######### steps ######

    def _step1_tf_state(self):
        self.params.set_step("step1")
        print("\n")
        print(self.file_utils.stage_prefix(), "step1_tf_state")
        #step1
        api = self._api()
        if self.params.module == 'infra':
            cloud_resources = api.get_infra_resources()
        else:
            cloud_resources = api.get_tenant_resources()
        #step2
        print(cloud_resources)
        self.step1 = self._init_step1()
        self.step1.execute(cloud_resources)
        # download_aws_keys
        if self.params.module == 'infra':
            pass
        else:
            if self.params.download_aws_keys == 'yes':
                print(" ====== execute_infra_step1 download_key ====== \n")
                tenant_key_pairs = api.get_tenant_key_pair_list()
                self.step1.download_key(tenant_key_pairs)
        print(" ====== execute_infra_step1 ====== DONE\n")


    def _step2_tf_main(self):
        self.params.set_step("step2")
        print("\n====== execute_step2 ====== START")
        self.step2 = self._init_step2()
        self.step2.execute()
        print("temp_folder  ***** ", self.params.temp_folder)
        print("import_name  ***** ", self.params.import_name)
        print("zip_file_path  ***** ", os.path.abspath(self.params.zip_file_path+".zip"))
        print(" ====== execute_step2 ====== DONE\n")
    ############# ######


    ############# ######
    def pre_execute(self):
        self.file_utils.delete_folder(self.params.temp_folder)
        for module in self.params.modules():
            self.params.set_step_type(module)
            self.params.set_step("step1")
            self.file_utils._ensure_folders()

    def post_execute(self):
        self._zip()
        self.backup()
        print("================================================================================== ")
        print("temp_folder  ***** ", self.params.temp_folder)
        print("import_name  ***** ", self.params.import_name)
        print("log_folder  ***** ", self.file_utils.log_folder())
        print("fial_folder  ***** ", self.file_utils.final_folder())
        print("files  ***** ", self.file_utils.ls_folder(self.file_utils.final_folder()))
        print("zip_file_path  ***** ", os.path.abspath(self.params.zip_file_path + ".zip"))
        print("import_name  ***** ", self.params.import_name)
        print("log_folder  ***** ", os.path.abspath(self.file_utils.log_folder()))
        print("final_folder  ***** ", os.path.abspath(self.file_utils.final_folder()))
        print("================================================================================== ")

    def backup(self):
        try:
            # backup and s3 sync
            terraform_folder = os.path.join("duplocli", "terraform")
            import_tf_backup_settings_auth_service = os.path.join(terraform_folder,
                                                                  "import_tf_backup_settings_auth_service.json")
            if os.path.exists(import_tf_backup_settings_auth_service):
                backup_settings_json = import_tf_backup_settings_auth_service
            else:
                backup_settings_json = self._get_backup_settings_json()  # os.path.join(terraform_folder,"tfbackup","json_default_tf_backup_settings.json")
            eackupImportFolders = BackupImportFolders(self.params, backup_settings_json=backup_settings_json)
            eackupImportFolders.backup_folders()
        except Exception as e:
            print("ERROR:Steps:","backup", e)
    # def post_execute(self):
    #     self._zip()
    #     # backup and s3 sync
    #     print(os.getcwd())
    #     #'/Users/brighu/_duplo_code/branch/duplocli/duplocli/terraform'
    #     terraform_folder = os.getcwd() #os.path.join("duplocli", "terraform")
    #     import_tf_backup_settings_auth_service = os.path.join(terraform_folder, "json_tf_backup_settings_auth_service.json")
    #     if os.path.exists(import_tf_backup_settings_auth_service):
    #         backup_settings_json = import_tf_backup_settings_auth_service
    #     else:
    #         backup_settings_json =  os.path.join(terraform_folder,"tfbackup","json_default_tf_backup_settings.json")
    #     eackupImportFolders = BackupImportFolders(self.params, backup_settings_json=backup_settings_json)
    #     eackupImportFolders.backup_folders()

    def _get_backup_settings_json(self):
        json_file = "backup_settings.json"
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), json_file)
        return json_path

    def _zip(self):
        copy_files = []
        for module in self.params.modules():
            self.params.set_step_type(module)
            self.params.set_step("step2")
            copy_files.append(self.file_utils.tf_resources_file())
            copy_files.append(self.file_utils.tf_state_file())
            copy_files.append(self.file_utils.tf_main_file())
        copy_files.append(self.file_utils.keys_folder())
        self.file_utils.zip_final_folder(self.params.tenant_name,
                                         self.file_utils.final_folder(),
                                         self.file_utils.zip_folder(),
                                         copy_files)
    ############

    ###############
    def _api(self):
        self.api = AwsResources(self.params)
        return self.api

    ###############
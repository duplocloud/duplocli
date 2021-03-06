# import json
# import datetime
# from collections import defaultdict
#
# import os
#
# from duplocli.terraform.aws.common.tf_utils import TfUtils
# from duplocli.terraform.aws.schema.aws_tf_schema import AwsTfSchema
#
#
# class AwsToTfUtilStep1 :
#     step = "step1"
#
#     # aws_tf_schema
#     aws_tf_schema_file = "data/aws_tf_schema.json"
#     aws_tf_schema = {}
#     is_allow_none = True
#
#     #
#     # DEPRECATED: # mapping_aws_to_tf_state:
#     # aws_to_tf_state_sync_ids_file = "data/aws_to_tf_sync_id_mapping.json"
#     # mapping_aws_to_tf_state_sync_ids = []
#
#     # mapping_aws_to_tf_state
#     mapping_aws_keys_to_tf_keys_file = "data/mapping_aws_keys_to_tf_keys.json"
#     mapping_aws_keys_to_tf_keys = []
#
#     # main.tf.json
#     main_tf_json_file_name = "main.tf.json"
#     main_tf_json_dict = {"resource":{}}
#     resources_dict = main_tf_json_dict["resource"]
#
#     #tf_import_script.sh
#     tf_import_script_file_name = "tf_import_script.sh"
#     tf_import_sh_list = []
#
#     # tf_import_script.sh
#     tf_run_script_file_name = "run.sh"
#
#
#     def __init__(self, tenant_name="bigdata01", aws_az="us-west-2"):
#         self.utils = TfUtils()
#         self.aws_az = aws_az
#         self.tenant_name = tenant_name
#         self.tenant_id = self.utils.get_tenant_id(tenant_name)
#
#         ## script files
#         self.tf_temp_path = self.utils.get_tf_temp_path(self.step)
#         self.tf_json_file = self.utils.get_save_to_temp_path(self.step, self.main_tf_json_file_name)
#         self.tf_import_script_file = self.utils.get_save_to_temp_path(self.step, self.tf_import_script_file_name)
#         self.tf_run_script_file = self.utils.get_save_to_temp_path(self.step, self.tf_run_script_file_name)
#
#         #
#         self._load_mapping_aws_keys_to_tf_keys()
#         self.load_schema()
#         self.empty_output()
#         self.aws_provider()
#
#     def load_schema(self):
#         self.aws_tf_schema = AwsTfSchema (self.aws_tf_schema_file)
#         #self.utils.load_json_file(self.aws_tf_schema_file)
#
#     ############ aws tf resources ##########
#     #todo: could be automated using schema -- using required fields + data/duplo_aws_tf_schema.json
#     def aws_resource(self, tf_resource_type, aws_obj, tf_name=None):
#
#         ### "TF_RESOURCE_TYPE" "TF_RESOURCE_VAR_NAME" e.g. "aws_elasticache_cluster" "cluster1"
#         if tf_name is None:
#             tf_resource_var_name = self._get_aws_to_tf_state_sync_name(tf_resource_type,  aws_obj)
#         else:
#             tf_resource_var_name = tf_name
#
#         ### create: resource tf_resource_type  tf_resource_var_name
#         resource_obj = self._init_tf_resource(tf_resource_type, tf_resource_var_name, aws_obj)
#
#         #keep an eye ---we are neglecting datas type !
#         #required fields: can not use current value from aws_obj. we do not know aws field name to tf field name mapping.
#         schema = self.aws_tf_schema.get_tf_resource(tf_resource_type)
#         for required_name in schema.required:
#             resource_obj[required_name] = "aa"
#         return resource_obj
#
#     ############ aws tf resources ##########
#
#     def aws_elasticache_cluster(self, aws_obj):
#         return self.aws_resource("aws_elasticache_cluster", aws_obj)
#
#     def aws_s3_bucket(self, aws_obj):
#         return self.aws_resource("aws_s3_bucket", aws_obj)
#
#     def aws_db_instance(self, aws_obj):
#         return self.aws_resource("aws_db_instance", aws_obj)
#
#     def aws_instance(self, aws_obj, name):
#         return self.aws_resource("aws_instance", aws_obj, tf_name=name)
#
#     def aws_iam_instance_profile(self, aws_obj):
#         return self.aws_resource("aws_iam_instance_profile", aws_obj)
#
#     def aws_iam_role(self, aws_obj):
#         return self.aws_resource("aws_iam_role", aws_obj)
#
#     def aws_security_group(self, aws_obj):
#         return self.aws_resource("aws_security_group", aws_obj)
#
#     def aws_vpc(self, aws_obj):
#         #todo: not tested
#         return self.aws_resource("aws_vpc", aws_obj)
#
#     ############ aws_provider ##########
#     def aws_provider(self):
#         tf_resource_type = "provider"
#         tf_resource_var_name = "aws"
#         resource_obj = self._base_provider(tf_resource_type, tf_resource_var_name)
#         resource_obj["version"] = "~> 2.0"
#         resource_obj["region"] = self.aws_az
#         self.tf_import_sh_list.append('terraform init ')
#         return resource_obj
#     def _base_provider(self, tf_resource_type, tf_resource_var_name):
#         resource_obj = {}
#         resource_obj[tf_resource_var_name] = {}
#         self.main_tf_json_dict[tf_resource_type] = resource_obj
#         return resource_obj[tf_resource_var_name]
#     ############ utility methods ##########
#
#
#     def _get_or_create_tf_resource_type_root(self, tf_resource_type):
#         ### create: resource "TF_RESOURCE_TYPE" "TF_RESOURCE_VAR_NAME"
#         if tf_resource_type not in self.resources_dict:
#             self.resources_dict[tf_resource_type] = {}
#         return self.resources_dict[tf_resource_type]
#
#     def _init_tf_resource(self, tf_resource_type, tf_resource_var_name, aws_obj):
#         ### get aws sync_id: used to update tf state
#         tf_resource_type_sync_id = self._get_aws_to_tf_state_sync_id(tf_resource_type,  aws_obj)
#
#         ### create: resource "TF_RESOURCE_TYPE" "TF_RESOURCE_VAR_NAME"
#         tf_resource_type_root = self._get_or_create_tf_resource_type_root(tf_resource_type)
#         resource_obj = {}
#         tf_resource_type_root[tf_resource_var_name] = resource_obj
#
#         ### create: terraform import "TF_RESOURCE_TYPE.TF_RESOURCE_VAR_NAME" "tf_resource_type_sync_id"
#         self.tf_import_sh_list.append(
#             'terraform import "' + tf_resource_type + '.' + tf_resource_var_name + '"  "' + tf_resource_type_sync_id + '"')
#         ### return:  resource_obj
#         return resource_obj
#
#     ############ mapping_aws_keys_to_tf_keys = sync_ids and names ##########
#     def _load_mapping_aws_keys_to_tf_keys(self):
#         self.mapping_aws_keys_to_tf_keys = self.utils.load_json_file(self.mapping_aws_keys_to_tf_keys_file)
#         self.mapping_aws_to_tf_state_sync_ids = self.mapping_aws_keys_to_tf_keys['syncids']
#         self.mapping_aws_to_tf_state_sync_names = self.mapping_aws_keys_to_tf_keys['names']
#
#     def _get_aws_to_tf_state_sync_id(self, tf_resource_type,  aws_obj):
#         if tf_resource_type not in self.mapping_aws_to_tf_state_sync_ids:
#             raise Exception("please define sync_id for '{0}' mapping_aws_keys_to_tf_keys.json."
#                             + " Used to aws id during terraform import.".format(tf_resource_type))
#
#         ### get aws sync_id: used to update tf state
#         aws_key = self.mapping_aws_to_tf_state_sync_ids[tf_resource_type]
#         aws_key_val = aws_obj[aws_key]
#         return aws_key_val
#
#     def _get_aws_to_tf_state_sync_name(self, tf_resource_type,  aws_obj):
#         if tf_resource_type not in self.mapping_aws_to_tf_state_sync_names:
#             raise Exception("please define sync name for '{0}' mapping_aws_keys_to_tf_keys.json. "
#                             + " Used to create a name for terraform resource in main.tf.json".format(tf_resource_type))
#
#         ### get aws sync_name: used to create a name for terraform object in main.tf
#         aws_key = self.mapping_aws_to_tf_state_sync_names[tf_resource_type]
#         aws_key_val = aws_obj[aws_key]
#         return aws_key_val
#
#     ############ aws_to_tf_state_sync_id ##########
#
#     ############ main.tf.json + script + generate state ##########
#
#     def empty_output(self):
#         self.utils.empty_temp_folder(self.step)
#
#     def create_state(self):
#         self._plan()
#         self._save_tf_files()
#         self.utils.create_state(self.tf_run_script_file, self.step)
#
#     def _save_tf_files(self):
#         self.utils.save_to_json(self.tf_json_file, self.main_tf_json_dict)
#         self.utils.save_run_script(self.tf_import_script_file, self.tf_import_sh_list)
#         run_sh_list=[]
#         run_sh_list.append("cd {0}".format(self.tf_temp_path))
#         run_sh_list.append("chmod 777 *.sh")
#         run_sh_list.append("./{0}  ".format(self.tf_import_script_file_name))
#         self.utils.save_run_script(self.tf_run_script_file, run_sh_list)
#         # add plan to script
#
#     def _plan(self):
#         ### create: terraform plan ...
#         # bug in tf -> creates extra aws_security_group_rule... remove aws_security_group_rule first.
#         self.tf_import_sh_list.append(
#             'terraform state list | grep aws_security_group_rule | xargs terraform state rm; terraform plan')
#
#     ############ main.tf.json + script + generate state ##########

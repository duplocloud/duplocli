import psutil
import os
import datetime
import argparse
from duplocli.terraform.common.tf_file_utils import TfFileUtils
from duplocli.terraform.params.config import get_help, arg_params
from duplocli.terraform.params.arg_parse import TfModule, ArgParse


class ParamBase:

    def __init__(self, provider, args_param_list,   default_params):
        self.paramHelper = ArgParse( provider, args_param_list,   default_params)
        self.args_param_list = args_param_list
        self.default_params = default_params
        self.provider = provider

    def validate(self):
        pass

    ########

    def set_step_type(self, step_type):
        self.step_type = step_type
        self.module = step_type
        if step_type in self.modules():
            self.tf_module = self.get_tf_module(step_type)

    def set_step(self, step):
        self.step = step

    def modules(self):
        return list(self.tf_modules.keys())

    def get_tf_module(self, tenant_name):
        return self.tf_modules[tenant_name]

    ####### parser ######
    def get_parser(self):
        return self.paramHelper.get_parser()

    def parsed_args(self, parsed_args):
        # self.parsed_args_params = parsed_args
        parameters = self.paramHelper.parsed_args(parsed_args)

        # set as attributes
        self._set_attributes(parameters)
        self.tf_modules =  self.paramHelper.getTfModules(parameters)

        ### create_work_file_paths
        self._create_work_file_paths()


        print("########## final parameters ########## ")
        parameters_cur = vars(self)
        for key in parameters_cur:
            print("final", key, getattr(self, key))

        return parameters

    def _set_attributes(self, parameters):
        key_list = list(parameters.keys())
        att_name_list = self.attr_names + key_list
        for att_name in att_name_list:
            value = self._from_dict(parameters, att_name)
            setattr(self, att_name, value)

    def _from_dict(self, parameters, key):
        if key in parameters:
            return parameters[key]
        return None

    def _create_work_file_paths(self):
        params = self
        self.file_utils = TfFileUtils(self)
        if self.import_name is None:
            now = datetime.datetime.now()
            now_str = now.strftime("%m-%d-%Y--%H-%M-%S")
            self.import_name = "{0}-{1}".format(self.provider, now_str)
        self.parameters_default = self.default_params  #self.file_utils.load_json_file(self.default_params_path)
        if self.parameters_default["temp_folder"] == self.temp_folder:
            self.temp_folder = os.path.join(self.temp_folder, self.tenant_name, self.import_name)
            self.zip_folder = os.path.join(self.temp_folder, "zip")
        if self.zip_file_path is None:
            self.zip_file_path = os.path.join(self.zip_folder, self.import_name)
        self.temp_folder_path = self.temp_folder
        self.zip_folder_path = self.zip_folder

    def _check_required_fields(self, required_fields):
        self.paramHelper._check_required_fields(required_fields)


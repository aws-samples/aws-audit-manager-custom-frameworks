# Core python packages
import yaml

# 3rd party packages
import boto3

# /src
from mergeMultiFramework import merge_multiple_framework

def create_generate_yaml_automated_controls(
        report_list: list,
        custom_report_name: str,
        filename: str,
        region_name = None,
    ):


    auditmanager_client = boto3.client('auditmanager', region_name=region_name)
    ## create a zero byte yaml file
    open(filename, 'w').close()

    for name_report in report_list:
        framework_list_response = auditmanager_client.list_assessment_frameworks(frameworkType='Standard')

        for framework_list in framework_list_response['frameworkMetadataList']:
            if framework_list['name'] == name_report:
                id_report = framework_list['id']

        framework_controls_response = auditmanager_client.get_assessment_framework(
            frameworkId=id_report
        )
        yaml_dict = {}
        control_sets_list = []
        yaml_control_dict = {}
        for control_sets in framework_controls_response['framework']['controlSets']:
            control_sets_dict = {}
            control_list = []
            yaml_control_list = []
            for controls in control_sets['controls']:
                controls_dict = {}
                if controls['controlSources'] != 'Manual':
                    yaml_control_list.append(controls['name'])
                    controls_dict['id'] = controls['id']
                    control_list.append(controls_dict)

            if len(yaml_control_list) > 0:
                yaml_control_dict[control_sets['name']] = yaml_control_list
            control_sets_dict['name'] = control_sets['name']
            control_sets_dict['controls'] = control_list
            control_sets_list.append(control_sets_dict)

        if len(yaml_control_dict) > 0:
            yaml_dict[name_report] = yaml_control_dict

        ## writes into yaml file
        with open(filename, 'a') as file:
            documents = yaml.dump(yaml_dict, file)

    merge_multiple_framework(custom_report_name, filename)
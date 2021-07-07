# Core python packages
import sys

# 3rd party packages
import boto3

# /src
from utils import *

def merge_multiple_framework(
        custom_report_name: str,
        filename: str,
        region_name=None,
) -> dict:
    format_yaml = open_yaml(input_file=filename)
    """
    Creates a custom assessment framework in Audit Manager by merging multiple frameworks using YAML

    Args:
        custom report_name (*string*)--
        [**REQUIRED**]
		The name of existing framework.

        filename  (*string*)--
        [**REQUIRED**]
        The filepath of aml file


    Raises:
        error: raises Boto3 ClientError

    Returns:
        [type]: [description]
    """

    auditmanager_client = boto3.client('auditmanager', region_name=region_name)

    ## List all standard frameworks
    try:
        framework_response = auditmanager_client.list_assessment_frameworks(frameworkType='Standard')
    except botocore.exceptions.ClientError as error:
        raise error

    already_exists = check_framework_existence(custom_report_name)

    if already_exists:
        sys.exit(
            f"The customer framework {custom_report_name} already exists. Please note that Framework name within the AWS account should be unique")

     ## replace framework name with framework id
    format_yaml_orig = format_yaml.copy()
    for yaml_keys in format_yaml_orig.keys():
        for f_response in framework_response.get('frameworkMetadataList'):
            if f_response['name'] == yaml_keys:
                format_yaml[f_response['id']] = format_yaml[yaml_keys]
                del format_yaml[yaml_keys]

        ## creates an output list
    yaml_control_sets_list = []

    for yaml_items in format_yaml.items():  ## iterates through yaml file
        for yaml_control_sets in yaml_items[1].keys():  ## iterates through control_sets
            for control_sets in auditmanager_client.get_assessment_framework(frameworkId=yaml_items[0])['framework']['controlSets']:  ## fetches list of controlSets of single 	framework
                yaml_control_sets_dict = {}
                control_list = []
                if control_sets['name'] == yaml_control_sets:  ## compare name of control_sets with input_yaml_control sets ## Returns list of list as an output
                    for yaml_control_list in yaml_items[1].values():  ## will fetch corresponding controls from control sets
                        for yaml_controls in yaml_control_list:  ## will fetch corresponding controls from control sets. We do it twice as we get list of list as an output
                            for controls in control_sets['controls']:  ## iterates through controls
                                if controls['name'] == yaml_controls:  ## compares with input yaml and convert into required format.
                                    controls_dict = {}
                                    controls_dict['id'] = controls['id']  ## we need control's Id as an input
                                    control_list.append(controls_dict)

                if len(control_list) > 0:
                    yaml_control_sets_dict['name'] = controls['name']
                    yaml_control_sets_dict['controls'] = control_list
                    yaml_control_sets_list.append(yaml_control_sets_dict)
    try:
        response = auditmanager_client.create_assessment_framework(
            name=custom_report_name,
            controlSets=yaml_control_sets_list
        )
        logging.debug(response)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logging.info(f"Custom Framework {custom_report_name} Created successfully")
    except botocore.exceptions.ClientError as error:
        raise error
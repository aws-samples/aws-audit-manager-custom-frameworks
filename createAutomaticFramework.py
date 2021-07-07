# core python packages
import sys

# 3rd party packages - see requirements.txt
import boto3

# /src
from utils import *



# Create custom assessment framework using automated controls

def create_automated_custom_framework(
        report_name: str = None,
        custom_report_name: str = None,
        region_name=None,
) -> dict:
    """
    Create a custom assessment framework using automated controls in Audit Manager

    Args:
        report_name (*string*)--
        [**REQUIRED**]
		The name of existing framework. Defaults to **None**.

        custom_report_name (*string*)--
        [**REQUIRED**]
        The name of the custom framework. Defaults to **None**.


    Raises:
        error: raises Boto3 ClientError

    Returns:
        [type]: [description]
    """

    auditmanager_client = boto3.client('auditmanager', region_name=region_name)

    ## List all standard frameworks
    try:
        framework_list_response = auditmanager_client.list_assessment_frameworks(frameworkType='Standard')
    except botocore.exceptions.ClientError as error:
        raise error

    custom_exists = check_framework_existence(custom_report_name)

    if custom_exists:
        sys.exit(f"The customer framework {custom_report_name} already exists. Please note that Framework name within the AWS account should be unique")

    ## Extract framework id of given framework
    standard_exists = False
    for framework_list in framework_list_response['frameworkMetadataList']:
        if framework_list['name'] == report_name:
            id_report = framework_list['id']
            standard_exists = True

    if not standard_exists:
        sys.exit(f"The framework name {report_name} doesn't exist")


    ## Returns complete information about given framework
    try:
        framework_controls_response = auditmanager_client.get_assessment_framework(
            frameworkId=id_report
        )
    except botocore.exceptions.ClientError as error:
        raise error

    control_sets_list = []

    ## Get control sets and controls of given framework
    for control_sets in framework_controls_response['framework']['controlSets']:
        control_sets_dict = {}

        control_list = []
        for controls in control_sets['controls']:
            controls_dict = {}
            if controls['controlSources'] != 'Manual':  ## Filters out manual controls
                controls_dict['id'] = controls['id']
                control_list.append(controls_dict)
        if len(control_list) > 0:
            control_sets_dict['name'] = control_sets['name']
            control_sets_dict['controls'] = control_list
            control_sets_list.append(control_sets_dict)  ## create a list of dictionaries

    try:
        response = auditmanager_client.create_assessment_framework(
            name=custom_report_name,
            controlSets=control_sets_list
        )
        logging.debug(response)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logging.info(f"Custom Framework {custom_report_name} Created successfully")
    except botocore.exceptions.ClientError as error:
        raise error


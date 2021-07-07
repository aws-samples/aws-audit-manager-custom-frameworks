# Core python packages
import logging

# 3rd party packages - see requirements.txt
import boto3
import botocore.exceptions

# src python
from utils import *

# Create custom assessment framework in Audit Manager
def create_custom_framework(
        custom_report_name: str = None,
        description: str = None,
        complianceType: str = None,
        control_sets: list = None,
        region_name=None,
) -> dict:
    """
    Creates a custom assessment framework in Audit Manager

    Args:
        custom_report_name (*string*)--
        [**REQUIRED**]
        The name of the custom framework. Defaults to **None**.
        description (*string*, optional): An . Defaults to **None**.
        complianceType (*string*, optional): [description]. Defaults to **None**.
        control_sets (*string*, optional): [description]. Defaults to **None**.
        auditmanager (*string*, optional): [description]. Defaults to **None**.

    Raises:
        error: raises Boto3 ClientError
        error: raises Boto3 ClientError

    Returns:
        [type]: [description]
    """
    auditmanager_client = boto3.client('auditmanager', region_name=region_name)
    existing_frameworks = (
        auditmanager_client.list_assessment_frameworks(frameworkType="Custom"))
    already_exists = False
    # Looping through all existing custom frameworks
    for existing in existing_frameworks["frameworkMetadataList"]:
        # Checking if the framework being created already exists and
        # updating it
        if existing["name"] == custom_report_name:
            already_exists = True
            try:
                response = auditmanager_client.update_assessment_framework(
                    frameworkId=existing["id"],
                    name=custom_report_name,
                    description=description,
                    complianceType=complianceType,
                    controlSets=control_sets
                )
                logging.debug(response)
                return response
            except botocore.exceptions.ClientError as error:
                raise error

    # Creating new framework if it does not already exist
    if already_exists is False:
        try:
            response = auditmanager_client.create_assessment_framework(
                name=custom_report_name,
                description=description,
                complianceType=complianceType,
                controlSets=control_sets
            )
            logging.debug(response)
            return response
        except botocore.exceptions.ClientError as error:
            raise error


def list_controls(controlType: str = None, region_name=None) -> dict:
    auditmanager_client = boto3.client('auditmanager', region_name=region_name)
    existing_controls = auditmanager_client.list_controls(controlType="Custom")
    nextToken = existing_controls.get('nextToken', None)
    while nextToken is not None:
        next_existing_controls = auditmanager_client.list_controls(
            controlType="Custom",
            nextToken=nextToken
        )
        # Adding each control in the new list of controls to the existing list
        for item in next_existing_controls["controlMetadataList"]:
            existing_controls["controlMetadataList"].append(item)

        # Checking if there is a token in the new list of controls
        if "nextToken" in next_existing_controls:
            nextToken = next_existing_controls["nextToken"]
        else:
            nextToken = None
    logging.debug(existing_controls)
    return existing_controls


# Create


# Create custom controls in Audit Manager
def create_custom_controls(input=None, controls=None, region_name=None):
    auditmanager_client = boto3.client('auditmanager', region_name=region_name)
    # Calls the list_controls() and returns a list of existing controls
    existing_controls = list_controls(region_name=region_name)
    control_sets = []
    # Iterating through the control sets in the JSON file
    for control_set in input:
        # Creating a dictionary of control sets and list of control IDs
        # to pass them into the assessment framework in the correct format
        control_sets_dict = {}
        control_ids = []
        control_sets_dict.setdefault("name", control_set)

        # Iterating through each control in the control set
        for control in input[control_set]:

            already_exists = False
            # Looping through all existing custom controls
            for existing in existing_controls["controlMetadataList"]:
                # Checking if the control being created already exists and
                # updating it if so
                if existing["name"] == input[control_set][control]["name"]:
                    already_exists = True
                    controlMappingSources = []

                    # Adding each data source to a
                    # list to feed into the control creation
                    for data_source in input[control_set][control]["controlMappingSources"]:
                        # Converting keywords to uppercase if not already
                        if "sourceKeyword" in data_source:
                            keyword = data_source["sourceKeyword"]["keywordValue"]
                            if keyword.isupper() is not True:
                                uppercase_keyword = keyword.upper()
                                data_source["sourceKeyword"]["keywordValue"] = uppercase_keyword
                        controlMappingSources.append(data_source)
                    # Create control
                    try:
                        response = auditmanager_client.update_control(
                            controlId=existing["id"],
                            name=input[control_set][control]["name"],
                            description=(
                                input[control_set][control]["description"]),
                            testingInformation=(
                                input[control_set]
                                [control]["testingInformation"]),
                            actionPlanTitle=(
                                input[control_set]
                                [control]["actionPlanTitle"]),
                            actionPlanInstructions=(
                                input[control_set]
                                [control]["actionPlanInstructions"]),
                            controlMappingSources=controlMappingSources
                        )
                    except botocore.exceptions.ClientError as error:
                        raise error

                    control_ids.append({"id": response["control"]["id"]})
                    break

            # Creating new control if it does not already exist
            if already_exists is False:
                controlMappingSources = []

                # Adding each data source to a
                # list to feed into the control creation
                for data_source in input[control_set][control]["controlMappingSources"]:
                    # Converting keywords to uppercase if not already
                    if "sourceKeyword" in data_source:
                        keyword = data_source["sourceKeyword"]["keywordValue"]
                        if keyword.isupper() is not True:
                            uppercase_keyword = keyword.upper()
                            data_source["sourceKeyword"]["keywordValue"] = uppercase_keyword
                    controlMappingSources.append(data_source)
                # Create control
                try:
                    response = auditmanager_client.create_control(
                        name=input[control_set][control]["name"],
                        description=input[control_set][control]["description"],
                        testingInformation=(
                            input[control_set][control]["testingInformation"]),
                        actionPlanTitle=(
                            input[control_set][control]["actionPlanTitle"]),
                        actionPlanInstructions=(
                            input[control_set]
                            [control]["actionPlanInstructions"]),
                        controlMappingSources=controlMappingSources
                    )
                except botocore.exceptions.ClientError as error:
                    raise error

                control_ids.append({"id": response["control"]["id"]})

        control_sets_dict["controls"] = control_ids
        control_sets.append(control_sets_dict)

    return control_sets








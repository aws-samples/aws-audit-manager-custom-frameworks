# Core python packages
import json
import logging
import sys
import os


# 3rd party packages - see requirements.txt
import boto3
import botocore.exceptions
import yaml

# src python
from utils import *
def open_input(filepath: str = None) -> str:
    """
    Performs a check on the --filepath argument to attempt to find the
    template file for the custom control and custom framework.

    It looks in three locations.

    * A complete path to the file
    * A file in /frameworks
    * An S3 URL

    Args:
        filepath (*string*, REQUIRED):

        A string which defined the path to the template file for the
        custom controls and custome framework

        Defaults to None.

    Raises:
        FileNotFoundError: The FileNotFoundError will be raised if it cannot
        locate the file
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    framework_dir = os.path.join(script_dir, 'frameworks')
    try:
        if os.path.isfile(filepath) is True:
            logging.info(
                'Input file found at {}'.format(filepath))
            if filepath.endswith(".json") is True:
                contents = open_json(input_file=filepath)
                return contents
            elif (
                    filepath.endswith(".yaml") is True
                    or
                    filepath.endswith(".yml") is True
            ):
                contents = open_yaml(input_file=filepath)
                return contents
            else:
                logging.info("Incorrect file type. An input file should be yaml or json.")
                sys.exit(1)
        elif os.path.isfile(os.path.join(framework_dir, filepath)) is True:
            filepath = os.path.join(framework_dir, filepath)
            logging.info(
                'Input file found in {} directory'.format(
                    os.path.join(framework_dir, filepath)))
            if filepath.endswith('.json') is True:
                contents = open_json(input_file=filepath)
                return contents
            elif (
                    filepath.endswith(".yaml") is True
                    or
                    filepath.endswith(".yml") is True
            ):
                contents = open_yaml(input_file=filepath)
                return contents
            else:
                logging.info("Incorrect file type. An input file should be yaml or json.")
                sys.exit(1)
        elif filepath.startswith('s3://') is True:
            logging.info('Input file is in S3 bucket {}'.format(filepath))
            if filepath.endswith('.json') is True:
                contents = json.load(get_object_from_s3(filepath))
                return contents
            elif (
                    filepath.endswith(".yaml") is True
                    or
                    filepath.endswith(".yml") is True
            ):
                contents = yaml.safe_load(get_object_from_s3(filepath))
                return contents
            else:
                logging.info("Incorrect file type. An input file should be yaml or json.")
                sys.exit(1)
        else:
            raise FileNotFoundError
    except FileNotFoundError as error:
        raise error


def get_object_from_s3(s3_path: str = None) -> dict:
    s3 = boto3.client('s3')
    try:
        bucket_path = s3_path.split('/')
        bucket_name = bucket_path[2]
        key = bucket_path[(len(bucket_path) - 1)]
        response = s3.get_object(
            Bucket=bucket_name,
            Key=key
        )
        file_contents = response['Body'].read().decode()
        return file_contents
    except botocore.exceptions.ClientError as error:
        raise error

def open_yaml(input_file: str = None) -> dict:
    with open(input_file, 'r', encoding="utf8") as file_object:
        contents = yaml.safe_load(file_object)
        logging.debug(contents)
        return contents


def open_json(input_file: str = None) -> dict:
    with open(input_file, 'r', encoding="utf8") as file_object:
        contents = json.load(file_object)
        logging.debug(contents)
        return contents


def get_account_status(region_name=None):
    auditmanager_client = boto3.client('auditmanager', region_name=None)
    try:
        response_get_status = auditmanager_client.get_account_status()
        return response_get_status
    except botocore.exceptions.ClientError as error:
        raise error


def register_account(region_name=None):
    auditmanager_client = boto3.client('auditmanager', region_name=region_name)
    try:
        get_status = get_account_status(region_name=region_name)
        if get_status["status"] != "ACTIVE":
            response = auditmanager_client.register_account()
            return response
    except botocore.exceptions.ClientError as error:
        raise error


def check_framework_existence(custom_report_name, region_name=None):
    auditmanager_client = boto3.client('auditmanager', region_name=region_name)
    existing_frameworks = (auditmanager_client.list_assessment_frameworks(frameworkType="Custom"))
    already_exists = False
    for existing in existing_frameworks["frameworkMetadataList"]:
        # Checking if the framework being created already exists and
        # updating it
        if existing["name"] == custom_report_name:
            already_exists = True
    return already_exists

# Core python packages
import sys
import logging

# from src
from utils import *
from cli import create_arg_parser
from createAutomaticFramework import create_automated_custom_framework
from generateYAMLFramework import create_yaml_controls
from mergeMultiFramework import merge_multiple_framework
from createCustomStandard import *
# Deploy the custom controls and framework to every region required

def deploy_to_all_regions(regions: str = None):
    regions_list = regions.split(",")

    logging.info("-------- Beginning deployment --------")
    deployment_status = True
    # Iterating through the list of regions
    for region_name in regions_list:
        # Checking if Audit Manager has been registered in that region
        # and registering if not
        register_region = register_account(region_name=region_name)
        argument = (vars(create_arg_parser()))
        input_job_name = argument.get('job_name')

        deployment_region_status = False

        if input_job_name == 'Custom-Standard-Framework':
            if argument.get('custom_report_name') and argument.get('filepath') and argument.get('description') and argument.get('complianceType'):
                input = open_input(argument.get('filepath'))
                # Creating custom controls and passing to a custom framework

                # 👇 The function call to create_custom_controls👇
                control_sets = create_custom_controls(
                    input,
                    region_name=region_name
                )
                #The function call to create_custom_framework👇
                create_custom_framework(
                    argument.get('custom_report_name'),
                    argument.get('description'),
                    argument.get('complianceType'),
                    control_sets,
                    region_name=region_name
                )
                deployment_region_status = True
            else:
                logging.error("--customFrameworkName, --description, --compliance-type and --template-path are required parameters.")
                print("python customFramework.py --jobName Custom-Standard-Framework --customFrameworkName \"S3 Controls Framework\" --description \"Automated AWS Config Controls for Amazon S3\" --compliance-type \"AWS Service\" --template-path \"frameworks/s3_config_framework.yaml\" --regions \"us-east-1\"")

        elif input_job_name == 'Automated-Custom-Framework':

            if argument.get('custom_report_name') and argument.get('report_name'):
                create_automated_custom_framework(
                    argument.get('report_name'),
                    argument.get('custom_report_name')
                )
                deployment_region_status = True
            else:
                logging.error("--customFrameworkName and --existingFrameworkName are required parameters.")
                print("Example: python customFramework.py --jobName Automated-Custom-Framework --existingFrameworkName \"PCI DSS V3.2.1\" --customFrameworkName \"PCI DSS V3.2.1 - Automated Controls Only\"  --regions \"us-east-1\"")

        elif input_job_name == 'Merge-Multiple-Framework':

            if argument.get('custom_report_name') and argument.get('filepath'):
                merge_multiple_framework(
                    argument.get('custom_report_name'),
                    argument.get('filepath'),
                    argument.get('region_name')
                    )
                deployment_region_status = True
            else:
                logging.error("--customFrameworkName and --filepath are required parameters.")
                print("Example: python customFramework.py  --jobName Merge-Multiple-Framework --customFrameworkName \"Custom Enterprise Controls\" --template-path \"frameworks/multi_framework.yaml\" --regions \"us-east-1\"")

        elif input_job_name == 'Generate-YAML-Framework':

            if argument.get('filepath') and argument.get('report_name'):
                create_yaml_controls(
                    argument.get('report_name'),
                    argument.get('filepath')

                )
                deployment_region_status = True
            else:
                logging.error("--existingFrameworkName, --template-path and --filepath are required parameters.")
                print("Example: python customFramework.py --jobName Generate-YAML-Framework --existingFrameworkName \"AWS License Manager\" --template-path \"frameworks/license_manager_controls.yaml\" --regions \"us-east-1\"")
        else:
            logging.error(f"The job name {input_job_name} does not exist.")
            logging.error("Expected JobNames : Custom-Standard-Framework|Automated-Custom-Framework|Merge-Multiple-Framework|Generate-YAML-Framework")

        if deployment_region_status:
            logging.info(f"Deployment to the {region_name} region has been completed.")
        else:
            logging.error(f"Deployment to the {region_name} region has been failed.")
            deployment_status = False

    if deployment_status:
        logging.info("-------- All deployments have been completed --------")
    else:
        logging.error("-------- Issues reported while deploying custom frameworks --------")
    return register_region


# Main function
def main():
    if not sys.version_info >= (3, 5):
        sys.exit('python version must be 3.5 or greater')
    else:
        argument = (vars(create_arg_parser()))
        if argument.get('verbose') is True:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        deploy_to_all_regions(
            (argument.get('regions')))


if __name__ == '__main__':
    main()

# Core python packages
import argparse
import ast

def create_arg_parser() -> dict:
    # Define the parser variable to equal argparse.ArgumentParser()
    parser = argparse.ArgumentParser(
        description="Creates a custom audit framework",
        )

    # Add each of the arguments using the parser.add_argument() method
    parser.add_argument(
        "--jobName",
        dest='job_name',
        type=str,
        required=False,
        help="The name of the job. Currently we are supporting merge-multi-framework")

    parser.add_argument(
        "--customFrameworkName",
        dest='custom_report_name',
        type=str,
        required=False,
        help="The name of the new custom framework")

    parser.add_argument(
        "--existingFrameworkName",
        dest='report_name',
        type=str,
        required=False,
        help="The name of an existing framework")

#    parser.add_argument(
#        "--report_list",
#        dest="report_list",
#        type=ast.literal_eval,
#        required=False,
#        help="The list of existing frameworks")

    parser.add_argument(
        '--description',
        dest='description',
        type=str,
        required=False,
        help='An optional description for the new custom framework',)

    parser.add_argument(
        "--compliance-type",
        dest="complianceType",
        type=str,
        required=False,
        help=(
            "The compliance type that the new custom framework supports,"
            "such as CIS or HIPPA")
            )

    parser.add_argument(
        "--template-path",
        dest="filepath",
        type=str,
        required=False,
        help=(
            "file containing the template body for the control sets,"
            "in either json or yaml"),
        )

    parser.add_argument(
        "--regions",
        dest="regions",
        type=str,
        required=True,
        help=(
            "List of regions to deploy custom framework into,"
            "separated by a single ','"),
        )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        help=(
            """
            Using -v or --verbose will set the logging level
            to DEBUG to return increased logging,\
            CAUTION - This will generate a lot of logs!
            """),
        action='store_true',
    )




    # This will inspect the command line, convert each argument
    # to the appropriate type and invoke the appropriate action.
    args = parser.parse_args()
    return args


def main():
    create_arg_parser()


if __name__ == '__main__':
       main()

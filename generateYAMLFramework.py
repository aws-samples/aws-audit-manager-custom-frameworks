# Core python packages
import yaml

# 3rd party packages
import boto3

def create_yaml_controls(
        name_report: str,
        filename: str,
        region_name = None
        ):


	auditmanager_client = boto3.client('auditmanager', region_name=region_name)
	
	## create a zero byte yaml file
	open(filename, 'w', encoding="utf-8" ).close()
	
	framework_list_response = auditmanager_client.list_assessment_frameworks(frameworkType='Standard')
	

	for framework_list in framework_list_response['frameworkMetadataList']:
		if framework_list['name'] == name_report:
			id_report = framework_list['id']
	
	framework_controls_response = auditmanager_client.get_assessment_framework(
	    frameworkId=id_report
	)
	
	yaml_dict = {}
	
	for control_sets in framework_controls_response['framework']['controlSets']:
        
		control_sets_dict = {}
		
		for controls in control_sets['controls']:
	            
			controls_dict = {}
	
			controls_dict['name'] = controls['name'].strip()[0:300]
			if 'description' in controls.keys():
				controls_dict['description'] = controls['description'].strip()[0:1000]
			else:
				controls_dict['description'] = "Not Available"
			controls_dict['testingInformation'] = "-"
			controls_dict['actionPlanTitle'] = "-"
			controls_dict['actionPlanInstructions'] = "-"
	        
			for control_map in controls['controlMappingSources']:
				control_map['sourceName'] = control_map['sourceId']
				control_map.pop('sourceId')
	        
			controls_dict['controlMappingSources'] = controls['controlMappingSources']
			control_sets_dict[controls['name'].strip()] = controls_dict
	    
		yaml_dict[control_sets['name']] = control_sets_dict

	with open(filename, 'a', encoding="utf-8") as file:
		documents = yaml.dump(yaml_dict, file, sort_keys=False)

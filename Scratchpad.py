# import pandas as pd
# import passwords
# from sqlalchemy import create_engine
#
# url = passwords.rds_access
#
# engine = create_engine(url)
# connect = engine.connect()
#
# keyword_count = f'''select distinct keywords, keyword_count from public.rake_data
# order by keyword_count desc'''
# keyword_count_df = pd.read_sql(keyword_count, con=connect)
# keyword_count_df= keyword_count_df.iloc[:, 0]
# print(keyword_count_df)

# number_list = list(range(1,21,1))
#
# print(number_list)


#YAML file for ElasticBeanstalk called config.YAML
# branch-defaults:
#   default:
#     environment: null
#     group_suffix: null
#   master:
#     environment: null
#     group_suffix: null
# environment-defaults:
#   flask-env:
#     branch: null
#     repository: null
# global:
#   application_name: causalation3
#   branch: master
#   default_ec2_keyname: aws-eb
#   default_platform: Python 3.8
#   default_region: us-east-1
#   include_git_submodules: true
#   instance_profile: null
#   platform_name: null
#   platform_version: null
#   profile: null
#   repository: Causalation2
#   sc: git
#   workspace_type: Application
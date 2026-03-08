# AWS EC2 CloudWatch Agent

## Objective:

The goal of this project is to experiment and understand how AWS CloudWatch, lambda Function and S3 work. The end goal of this is to create a AI agent for security purpose in mind using Bedrock. 

<u>CloudWatch</u> is a AWS service that collects monitoring data from servers/apps. There are 4 services it provides:

- Logs - Text output from applications/systems
  - Can be streams (single) or groups
- Metrics - Numerical data (CPU %, disk usage, request counts)
- Events - Alerts/triggers (when something happens)
- Dashboards - Visual monitoring

<u>Lambda Function</u> is a serverless compute that runs script/code when triggered by a event and stops automatically. 

<u>S3 (Simple Storage Service)</u> Is a bucket that is a container that stores files. Each bucket have unique names, can hold many-many files and files is organized by keys.

There are 3 other markdown file:

1.  [CloudWatch](CloudWatch.md): Documentation how I setup CloudWatch on Ubuntu and AWS console
2.  [WizardSetup](WizardSetup.md): Table showing the options I chose when setting up CloudWatch Agent
3. [Lambda Function & S3](Lambda_Function_&_S3.md): Documentation how I setup Lambda Function and S3 to work with CloudWatch

Note: The instance image I used is Ubuntu. Thus, the process of installing AWS CLI or the CloudWatch agent is a bit different: requires downloading a package first (.deb). Additionally, instead of `yum`, it's `apt` to install packages.  



## Possible Future Improvement Check List

- [ ]  Add more threat detection conditions/logic
- [ ]  Store Lambda result to S3 
- [ ] Integrate SSM for convince and security
- [ ] Add more lambda functions for other purpose
- [ ] Provide instruction/process how to install dependences without using S3
- [ ]  Find a job :/


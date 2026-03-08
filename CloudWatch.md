# AWS CloudWatch on Ubuntu

## About:

This markdown document is the process I used to setup CloudWatch Agent on my EC2 Ubuntu instance and on AWS Console. The purpose of the CloudWatch is to monitor the instance performance and system logs like `/var/log/auth.log` and `/var/log/syslog`; each in different log group. The reason I picked `auth.log` because this files tracks SSH logins, sudo commands, and failed authorization attempts. By tracking these events, it ensure that any unauthorized access is alerted. I also picked syslog because this log captures kernel and system-level events, useful for detecting crashes or unusual behavior. 



## Process:

1. Create IAM role with `CloudWatchAgentServerPolicy` and `AmazonSSMManagedInstanceCore` policy for EC2 as a use case.

   <br>

2. Add the new role in the EC2 instance during creation or after:

   - For after, click on Actions → Security → Modify IAM role → select the create role → Update IAM role

   <br>

3. Install CloudWatch Agent on instance

   ```bash
   sudo wget https://amazoncloudwatch-agent.s3.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
   sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
   ```

   - To check if installed, `aws` folder should be in `/opt` directory

   <br>

4. Setup AWS CloudWatch config using Wizard

   ```bash
   sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
   ```

   - For suggested choices go to [WizardSetup.md](WizardSetup.md)

   - When ask about SSM, say no for now

   <br>

5. Start up CloudWatch (not for SSM)

   ```bash
   sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json
   ```

   <br>

6. Check if the agent is running

   ```bash
   sudo systemctl status amazon-cloudwatch-agent
   service amazon-cloudwatch-agent status
   ```

   - Hopefully it says running for both (basically the same commands)

   - Top stop the agent from sending update to AWS:

     ```bash
     sudo systemctl stop amazon-cloudwatch-agent
     ```

   <br>

7. Check if the agent is running properly

   ```bash	
   tail -f /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log
   ```

   - `tail` output the last part of file
   - `-f` flag output any new lines (live monitoring of a file)

   - **If `permission denied` in outputs, the agent might not have permission to read the file**

     - For `cwagent`, give permission to read system logs:

       ```bash
       sudo usermod -aG adm cwagent
       ```

   - **If `Unable to describe ec2 tags` in output, add `DescribeTag` as inline permission for the role**

     - In IAM role used by the instance, simply `create inline policy` in the <u>add permission</u> dropdown
     - Select EC2 as service and add `DescribeTag` as actions allowed
     - The permission allows the CloudWatch agent to call the EC2 API to retrieve custom metadata and tags that have assigned to the instance. This enables the agent to automatically organize and label logs and metrics in the AWS console using the project names, environment types, or owner tags.

8. Check if there's a log group that contain a log stream (log to track) in AWS CloudWatch console site under Log Management



## Learning Curves:

Learning how to use AWS CloudWatch was a bit challenging. Below, I have provided some issues I faced or learned during the process of setting up the CloudWatch Agent.

1. Because the instance is Ubuntu, I needed to use a specific URL to download the CloudWatch package. 
2. The architecture for `amd64` is the same as `x86_64`
3. The reason `DescribeTags` is required as a permission in IAM role if <u>EC2 Dimension</u> is true is because EC2 Dimension enhance the metrics with EC2-specific metadata and EC2-tags. For tags, they live outside the instance and requires a EC2 API call to retrieve the tags. To allow API calls, `DescribeTags` must be added to allow the IAM role to call the API. 
4. When picking `cwagent` for agent user in the Wizard setup, by default, this agent have low-privilege access. In order for this agent to read system logs (requires root/admin privileges), I assigned the agent with `adm`. `adm` does not stand for admin but is a group (administrative logging) to allow non-root users to read system logs, nothing else. 
5. AWS CLI is not required for CloudWatch but can be for troubleshooting, check IAM role permissions and etc within the instance. 
6. When setting up the Wizard, there were many question I did not understand and was confused which options to chose. After some Googling and asking AI, I made a table in [WizardSetup](WizardSetup.md) that helped me determine which options I should pick for the purpose of this project. 
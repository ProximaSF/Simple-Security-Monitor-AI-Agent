# AWS CloudWatch on Ubuntu

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
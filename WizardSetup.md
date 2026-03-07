| Wizard  Question          | Recommended  Choice                                          | Security  Reasoning                                          |
| ------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Operating System          | Linux                                                        | Instance is on Linux                                         |
| EC2 or On-Premises?       | EC2                                                          | Auto-discovers  region, credentials. Simplifies setup. On-prem requires manual credentials. |
| Agent User                | cwagent (might need admin privilege to read system logs)     | Dedicated  non-root user. Better security than root.         |
| StatsD Daemon?            | No                                                           | Not needed for security monitoring. More for custom apps publishing metrics. |
| CollectD Monitoring?      | No                                                           | Additional dependency. Not required for basic logs.          |
| Monitor Host Metrics?     | Yes                                                          | CPU,  memory, disk useful for detecting resource exhaustion attacks. Minimal cost. |
| CPU per Core?             | No                                                           | Aggregate CPU is sufficient. Per-core adds 8+ extra metrics with little security value. |
| EC2 Dimensions?           | Yes (will require `DescribeTag` inline permison to be added for the IAM role for the instance) | Adds InstanceId, InstanceType, ImageId. Essential for multi-instance environments.  Free metadata: more for organizaition. |
| Aggregate EC2 Dimensions? | Yes                                                          | Reduces  metric cardinality. Fewer = cheaper. Aggregate by InstanceId only. |
| Metrics Resolution        | 60  seconds                                                  | Standard  1-minute interval. Sub-minute (1-30s) costs 5-60x more. |
| Default Metrics Config    | Standard                                                     | Includes  disk, memory, swap. Basic is too limited; Advanced adds unnecessary metrics. |
| Monitor Log Files?        | Yes                                                          | Essential for security agent. Will collect auth, syslog, application logs. |
| Log File 1: Path          | /var/log/auth.log                                            | important file to monitor for:  Failed logins, sudo usage, permission changes, etc. Must-have for security monitoring. |
| Log File 1: Group Name    | auth-logs                                                    | Descriptive name. Groups related logs together in CloudWatch. |
| Log File 1: Log Class     | STANDARD                                                     | Keep in STANDARD (hot). Frequent access needed for security analysis. |
| Log File 1: Retention     | 3 days                                                       | More days, more data it will save                            |
| Log File 2: Path          | /var/log/syslog  (or /var/log/messages)                      | System  events, kernel messages, cron jobs. Less critical than auth.log. |
| Log File 2: Group Name    | system-logs                                                  | Separates system logs from auth logs for easier filtering.   |
| Log File 2: Log Class     | INFREQUENT_ACCESS                                            | Query  less often. Good candidate for cheaper tier if retention long. |
| Log File 2: Retention     | 3  days                                                      | Shorter retention saves cost. Critical issues usually surface quickly. |
| X-Ray Traces?             | No                                                           | Only  needed if instrumenting application code. Not required for log monitoring. |
| Store Config in SSM?      | No                                                           | Centralized  config management. Essential for multi-instance deployments. Cheap. |
| SSM Parameter Name        | No                                                           | Use  descriptive name. "security-agent" indicates purpose. Helps with  multi-config setups. |
| SSM Region                | Same  as instances                                           | Avoid  cross-region calls. Latency + data transfer costs.    |
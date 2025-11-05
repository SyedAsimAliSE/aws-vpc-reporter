# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in VPC Reporter, please report it to us privately before disclosing it publicly.

### How to Report

- Email: s.asim.ali.se@gmail.com
- Include "Security Vulnerability" in the subject line
- Provide as much detail as possible about the vulnerability

### What to Include

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Any proof-of-concept code or screenshots

### Response Time

We will acknowledge receipt of your vulnerability report within 48 hours and provide a detailed response within 7 days.

### Security Measures

VPC Reporter is designed with security in mind:

- **Read-Only Operations**: The tool only performs read-only AWS API calls
- **No Data Storage**: No AWS data is stored or transmitted externally
- **Local Processing**: All data processing happens locally on your machine
- **Credential Safety**: Uses standard AWS credential management

### Best Practices for Users

1. **Use Least Privilege**: Grant only necessary AWS IAM permissions
2. **Review Credentials**: Regularly rotate AWS access keys
3. **Secure Configuration**: Store configuration files securely
4. **Network Security**: Run from trusted network environments

### AWS IAM Permissions

The minimum required AWS IAM permissions for VPC Reporter:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "directconnect:Describe*"
            ],
            "Resource": "*"
        }
    ]
}
```

## Security Updates

Security updates will be announced through:
- GitHub releases
- Security advisories
- Update notifications in the tool

We encourage all users to keep their VPC Reporter installation up to date.

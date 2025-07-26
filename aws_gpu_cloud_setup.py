#!/usr/bin/env python3
"""
AWS AI GPU Cloud Platform Setup Script
Automated setup for AI Empower GPU Cloud infrastructure
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

class AWSGPUCloudSetup:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.s3 = boto3.client('s3')
        self.rds = boto3.client('rds')
        self.elbv2 = boto3.client('elbv2')
        
    def create_vpc_infrastructure(self):
        """Create VPC, subnets, and security groups"""
        print("🚀 Creating VPC infrastructure...")
        
        # Create VPC
        vpc_response = self.ec2.create_vpc(
            CidrBlock='10.0.0.0/16',
            TagSpecifications=[
                {
                    'ResourceType': 'vpc',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'AI-GPU-Cloud-VPC'},
                        {'Key': 'Project', 'Value': 'AI-GPU-Cloud'},
                        {'Key': 'Environment', 'Value': 'Production'}
                    ]
                }
            ]
        )
        vpc_id = vpc_response['Vpc']['VpcId']
        print(f"✅ VPC created: {vpc_id}")
        
        # Create Internet Gateway
        igw_response = self.ec2.create_internet_gateway(
            TagSpecifications=[
                {
                    'ResourceType': 'internet-gateway',
                    'Tags': [{'Key': 'Name', 'Value': 'AI-GPU-Cloud-IGW'}]
                }
            ]
        )
        igw_id = igw_response['InternetGateway']['InternetGatewayId']
        
        # Attach Internet Gateway to VPC
        self.ec2.attach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id
        )
        print(f"✅ Internet Gateway created and attached: {igw_id}")
        
        return vpc_id, igw_id
    
    def create_gpu_instances(self, vpc_id):
        """Create GPU instances for ML training and inference"""
        print("🎯 Creating GPU instances...")
        
        # GPU Training Instance (p3.2xlarge)
        training_instance = self.ec2.run_instances(
            ImageId='ami-0c02fb55956c7d316',  # Amazon Linux 2 AMI
            MinCount=1,
            MaxCount=1,
            InstanceType='p3.2xlarge',
            KeyName='ai-gpu-cloud-key',  # You'll need to create this key pair
            SecurityGroupIds=['sg-gpu-training'],  # Create security group first
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'AI-GPU-Training-Instance'},
                        {'Key': 'Purpose', 'Value': 'ML-Training'},
                        {'Key': 'Project', 'Value': 'AI-GPU-Cloud'}
                    ]
                }
            ]
        )
        
        # GPU Inference Instance (g4dn.xlarge)
        inference_instance = self.ec2.run_instances(
            ImageId='ami-0c02fb55956c7d316',
            MinCount=1,
            MaxCount=1,
            InstanceType='g4dn.xlarge',
            KeyName='ai-gpu-cloud-key',
            SecurityGroupIds=['sg-gpu-inference'],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'AI-GPU-Inference-Instance'},
                        {'Key': 'Purpose', 'Value': 'ML-Inference'},
                        {'Key': 'Project', 'Value': 'AI-GPU-Cloud'}
                    ]
                }
            ]
        )
        
        print("✅ GPU instances created successfully!")
        return training_instance, inference_instance
    
    def create_s3_buckets(self):
        """Create S3 buckets for ML models and data"""
        print("📦 Creating S3 buckets...")
        
        buckets = [
            'ai-gpu-cloud-models',
            'ai-gpu-cloud-datasets',
            'ai-gpu-cloud-logs',
            'ai-gpu-cloud-backups'
        ]
        
        for bucket_name in buckets:
            try:
                self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': 'us-east-1'
                    }
                )
                
                # Add bucket tags
                self.s3.put_bucket_tagging(
                    Bucket=bucket_name,
                    Tagging={
                        'TagSet': [
                            {'Key': 'Project', 'Value': 'AI-GPU-Cloud'},
                            {'Key': 'Environment', 'Value': 'Production'},
                            {'Key': 'Purpose', 'Value': bucket_name.split('-')[-1].title()}
                        ]
                    }
                )
                print(f"✅ S3 bucket created: {bucket_name}")
                
            except ClientError as e:
                print(f"❌ Error creating bucket {bucket_name}: {e}")
    
    def create_rds_database(self):
        """Create RDS database for user management"""
        print("🗃️ Creating RDS database...")
        
        try:
            db_response = self.rds.create_db_instance(
                DBName='aigpucloud',
                DBInstanceIdentifier='ai-gpu-cloud-db',
                DBInstanceClass='db.t3.micro',
                Engine='mysql',
                MasterUsername='admin',
                MasterUserPassword='AIGPUCloud2025!',  # Change this password!
                AllocatedStorage=20,
                VpcSecurityGroupIds=['sg-database'],  # Create security group first
                Tags=[
                    {'Key': 'Name', 'Value': 'AI-GPU-Cloud-Database'},
                    {'Key': 'Project', 'Value': 'AI-GPU-Cloud'},
                    {'Key': 'Environment', 'Value': 'Production'}
                ]
            )
            print("✅ RDS database creation initiated!")
            return db_response
            
        except ClientError as e:
            print(f"❌ Error creating RDS database: {e}")
    
    def setup_load_balancer(self, vpc_id):
        """Create Application Load Balancer"""
        print("⚖️ Creating Application Load Balancer...")
        
        try:
            alb_response = self.elbv2.create_load_balancer(
                Name='AI-GPU-Cloud-ALB',
                Subnets=['subnet-1', 'subnet-2'],  # Replace with actual subnet IDs
                SecurityGroups=['sg-load-balancer'],  # Create security group first
                Tags=[
                    {'Key': 'Name', 'Value': 'AI-GPU-Cloud-Load-Balancer'},
                    {'Key': 'Project', 'Value': 'AI-GPU-Cloud'}
                ]
            )
            print("✅ Application Load Balancer created!")
            return alb_response
            
        except ClientError as e:
            print(f"❌ Error creating load balancer: {e}")
    
    def run_full_setup(self):
        """Run the complete setup process"""
        print("🚀 Starting AI GPU Cloud Platform Setup...")
        print("=" * 50)
        
        try:
            # 1. Create VPC infrastructure
            vpc_id, igw_id = self.create_vpc_infrastructure()
            
            # 2. Create S3 buckets
            self.create_s3_buckets()
            
            # 3. Create RDS database
            self.create_rds_database()
            
            # 4. Create GPU instances (commented out to avoid costs)
            # training_instance, inference_instance = self.create_gpu_instances(vpc_id)
            
            # 5. Setup load balancer
            # self.setup_load_balancer(vpc_id)
            
            print("=" * 50)
            print("🎉 AI GPU Cloud Platform setup completed!")
            print(f"📋 VPC ID: {vpc_id}")
            print(f"🌐 Internet Gateway ID: {igw_id}")
            print("💡 Next steps:")
            print("   1. Create security groups")
            print("   2. Create key pairs")
            print("   3. Launch GPU instances")
            print("   4. Configure auto-scaling")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")

if __name__ == "__main__":
    # Initialize setup
    setup = AWSGPUCloudSetup()
    
    print("🔧 AI GPU Cloud Platform - AWS Setup Script")
    print("📝 This script will set up your GPU cloud infrastructure")
    print()
    
    # Run setup
    setup.run_full_setup()

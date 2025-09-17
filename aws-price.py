import boto3
import json
import os
import base64
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Decode credentials
AWS_ACCESS_KEY = base64.b64decode(os.getenv("AWS_ACCESS_KEY_ENC")).decode("utf-8")
AWS_SECRET_KEY = base64.b64decode(os.getenv("AWS_SECRET_KEY_ENC")).decode("utf-8")

# AWS Regions mapping
regions = {
    "1": ("US East (N. Virginia)", "us-east-1", "US East (N. Virginia)"),
    "2": ("US East (Ohio)", "us-east-2", "US East (Ohio)"),
    "3": ("US West (Oregon)", "us-west-2", "US West (Oregon)"),
    "4": ("Asia Pacific (Mumbai)", "ap-south-1", "Asia Pacific (Mumbai)"),
    "5": ("Asia Pacific (Singapore)", "ap-southeast-1", "Asia Pacific (Singapore)"),
    "6": ("Asia Pacific (Sydney)", "ap-southeast-2", "Asia Pacific (Sydney)"),
    "7": ("Europe (Frankfurt)", "eu-central-1", "Europe (Frankfurt)"),
    "8": ("Europe (Ireland)", "eu-west-1", "Europe (Ireland)"),
    "9": ("Europe (London)", "eu-west-2", "Europe (London)")
}

def get_instance_types(region_code, family_prefix=None):
    ec2 = boto3.client(
        "ec2",
        region_name=region_code,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    paginator = ec2.get_paginator("describe_instance_types")
    instance_types = []

    for page in paginator.paginate():
        for itype in page["InstanceTypes"]:
            name = itype["InstanceType"]
            vcpu = itype["VCpuInfo"]["DefaultVCpus"]
            mem = itype["MemoryInfo"]["SizeInMiB"] / 1024
            if family_prefix and not name.startswith(family_prefix):
                continue
            instance_types.append((name, vcpu, mem))
    return instance_types

def get_price(region_name, instance_type):
    pricing = boto3.client(
        "pricing",
        region_name="us-east-1",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    response = pricing.get_products(
        ServiceCode="AmazonEC2",
        Filters=[
            {"Type": "TERM_MATCH", "Field": "location", "Value": region_name},
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
            {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
            {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
            {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
        ],
        MaxResults=1
    )

    for product in response["PriceList"]:
        data = json.loads(product)
        terms = data["terms"]["OnDemand"]
        for _, term in terms.items():
            for _, price_dimension in term["priceDimensions"].items():
                return float(price_dimension["pricePerUnit"]["USD"])
    return None

def main():
    # Step 1: Region selection
    print("Available AWS Regions:")
    for num, (name, code, loc) in regions.items():
        print(f"{num}. {name} ({code})")

    region_num = input("\nSelect region (number): ").strip()
    region_entry = regions.get(region_num)
    if not region_entry:
        print("❌ Invalid region selection")
        return

    region_name, region_code, pricing_location = region_entry
    print(f"\n✅ Selected region: {region_code}")

    # Step 2: Family prefix filter
    family_prefix = input("\nEnter instance family prefix (e.g., t, m, c, r) or leave blank for all: ").strip()

    # Step 3: Fetch instances
    instances = get_instance_types(region_code, family_prefix)
    print(f"\nTotal instance types found in {region_code}: {len(instances)}\n")

    for i, (name, vcpu, mem) in enumerate(instances[:50], 1):  # limit display
        print(f"{i}. {name} - {vcpu} vCPUs, {mem:.1f} GiB")

    inst_num = int(input("\nEnter instance type number: ").strip())
    inst_name, inst_vcpu, inst_mem = instances[inst_num - 1]

    # Step 4: Pricing
    price_hourly = get_price(pricing_location, inst_name)
    if not price_hourly:
        print("⚠️ Price not available for this instance")
        return

    price_monthly = price_hourly * 24 * 30
    price_yearly = price_hourly * 24 * 365

    # Step 5: Final Output
    print("\n✅ Instance Info:")
    print(f"Instance Type : {inst_name}")
    print(f"vCPUs         : {inst_vcpu}")
    print(f"Memory        : {inst_mem:.0f} GiB")
    print(f"Hourly Price  : ${price_hourly:.4f}/hour")
    print(f"Monthly Price : ${price_monthly:.2f}/month")
    print(f"Yearly Price  : ${price_yearly:.2f}/year")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to download a specific file from a Hugging Face model to the models--org--model directory
structure and create a tar.gz of that directory.
"""

import os
import sys
import argparse
from huggingface_hub import hf_hub_download
import tarfile
import shutil

def parse_args():
    parser = argparse.ArgumentParser(
        description="Download a specific file from a Hugging Face model and create a tar.gz of the model directory"
    )
    parser.add_argument(
        "--model", "-m", 
        default="unstructuredio/yolo_x_layout",
        help="Model identifier (default: unstructuredio/yolo_x_layout)"
    )
    parser.add_argument(
        "--file", "-f", 
        default="yolox_l0.05.onnx",
        help="Specific file to download (default: yolox_l0.05.onnx)"
    )
    parser.add_argument(
        "--output", "-o", 
        default="./",
        help="Output directory to save the model (default: current directory)"
    )
    parser.add_argument(
        "--no-tar", 
        action="store_true",
        help="Skip creating a tar.gz archive (default: create archive)"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    # Get model ID parts
    org_name, model_name = args.model.split("/", 1) if "/" in args.model else ("", args.model)
    
    # Create the models--org--model directory structure
    hf_model_dir_name = f"models--{org_name.replace('/', '--')}--{model_name.replace('/', '--')}"
    
    if os.path.exists(hf_model_dir_name):
        shutil.rmtree(hf_model_dir_name)
        
    # unstructuredio/yolo_x_layout yolox_l0.05.onnx ./temp_hf_cache
    try:
        # Download the specific file
        hf_hub_download(
            repo_id=args.model,
            filename=args.file,
            cache_dir="./",
            local_dir_use_symlinks=False  # To get actual files, not symlinks
        )
        # Create tar.gz unless --no-tar was specified
        if not args.no_tar:
            tar_filename = f"{hf_model_dir_name}.tar.gz"
            tar_path = os.path.join(args.output, tar_filename)
            
            print(f"Creating archive: {tar_path}")
            
            # Navigate to the output directory to make paths relative in the archive
            original_dir = os.getcwd()
            os.chdir(args.output)
            
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(hf_model_dir_name)
            
            # Return to original directory
            os.chdir(original_dir)
            print(f"Archive created: {tar_path}")
        else:
            print("Error: Could not find model directory in downloaded file path")
            sys.exit(1)
            
        # Clean up the temporary cache
        print("Cleaning up temporary files...")
        shutil.rmtree(".locks")
        shutil.rmtree(hf_model_dir_name)
        
    except Exception as e:
        print(f"Error downloading model: {e}")
        sys.exit(1)
    
    print("\nDownload completed successfully!")
    if not args.no_tar:
        print(f"Archive: {os.path.join(args.output, tar_filename)}")

if __name__ == "__main__":
    main()
import os
from PyPDF2 import PdfMerger
import logging
from datetime import datetime
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_file_info(file_path):
    """
    Get file information including prefix and creation time.
    Prefix is the text before the first underscore.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        tuple: (prefix, creation_time)
    """
    # Get filename without extension
    filename = os.path.splitext(os.path.basename(file_path))[0]
    
    # Get prefix (part before first underscore)
    prefix = filename.split('_')[0]
    
    # If prefix is empty, use the entire filename
    if not prefix:
        prefix = filename
    
    # Get file creation time
    creation_time = os.path.getctime(file_path)
    
    return prefix, creation_time

def merge_pdfs_by_prefix(input_dir, output_dir=None):
    """
    Merge PDF files with the same prefix and sort by time.
    
    Args:
        input_dir (str): Path to directory containing PDF files
        output_dir (str, optional): Output directory. If None, use input_dir
    """
    try:
        # If no output_dir specified, use input_dir
        if output_dir is None:
            output_dir = input_dir
        
        # Create output_dir if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get list of all PDF files
        pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"No PDF files found in directory {input_dir}")
            return False
        
        # Group files by prefix
        prefix_groups = {}
        for pdf_file in pdf_files:
            file_path = os.path.join(input_dir, pdf_file)
            prefix, creation_time = get_file_info(file_path)
            
            if prefix not in prefix_groups:
                prefix_groups[prefix] = []
            prefix_groups[prefix].append((file_path, creation_time))
        
        # Process each prefix group
        for prefix, files in prefix_groups.items():
            if not files:
                continue
                
            logger.info(f"Processing group {prefix} with {len(files)} files")
            
            # Sort files by creation time
            files.sort(key=lambda x: x[1])  # x[1] is creation_time
            
            # Create merger for this group
            merger = PdfMerger()
            
            # Merge each file
            for file_path, _ in files:
                try:
                    merger.append(file_path)
                    logger.info(f"Added file: {os.path.basename(file_path)}")
                except Exception as e:
                    logger.error(f"Error adding file {file_path}: {str(e)}")
                    continue
            
            # Create output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{prefix}_merged_{timestamp}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            # Save merged file
            merger.write(output_path)
            merger.close()
            
            logger.info(f"Successfully merged group {prefix}: {output_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error merging PDFs: {str(e)}")
        return False

if __name__ == "__main__":
    # Current directory
    current_dir = os.getcwd()
    
    # PDF directory
    pdf_dir = os.path.join(current_dir, "pdf")
    
    # Output directory (can be None to use same as input directory)
    output_dir = os.path.join(current_dir, "pdf_merged")
    
    # Check if directory exists
    if not os.path.exists(pdf_dir):
        logger.error(f"Directory {pdf_dir} does not exist")
    else:
        # Perform merge
        success = merge_pdfs_by_prefix(pdf_dir, output_dir)
        
        if success:
            logger.info("Merge process completed")
        else:
            logger.error("Could not merge PDFs")

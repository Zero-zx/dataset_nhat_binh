import os
from PIL import Image
import glob

def get_image_size(image_path):
    """Get the dimensions of an image."""
    try:
        with Image.open(image_path) as img:
            return img.size  # Returns (width, height)
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return None

def find_largest_dimension(image_dir):
    """Find the largest width and height among all images."""
    max_width = 0
    max_height = 0
    
    # Get all PNG files
    image_files = glob.glob(os.path.join(image_dir, "*.png"))
    
    print(f"Found {len(image_files)} images")
    
    for image_path in image_files:
        size = get_image_size(image_path)
        if size:
            width, height = size
            max_width = max(max_width, width)
            max_height = max(max_height, height)
            print(f"{os.path.basename(image_path)}: {width}x{height}")
    
    # Use the maximum dimension to create a square
    square_size = max(max_width, max_height)
    print(f"\nLargest dimension found: {max_width}x{max_height}")
    print(f"Square size will be: {square_size}x{square_size}")
    
    return square_size

def resize_image_to_square(image_path, output_path, square_size):
    """Resize an image to a square size with transparent padding."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGBA to support transparency (handles RGB, RGBA, P, etc.)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Calculate padding to center the image
            width, height = img.size
            
            # Calculate scaling to fit within square while maintaining aspect ratio
            scale = min(square_size / width, square_size / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Resize image
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create a new square image with transparent background
            square_img = Image.new('RGBA', (square_size, square_size), (0, 0, 0, 0))
            
            # Calculate position to center the resized image
            x_offset = (square_size - new_width) // 2
            y_offset = (square_size - new_height) // 2
            
            # Paste the resized image onto the square canvas (preserves alpha channel)
            square_img.paste(img_resized, (x_offset, y_offset), img_resized)
            
            # Save the result
            square_img.save(output_path, 'PNG')
            print(f"Resized: {os.path.basename(image_path)} -> {os.path.basename(output_path)}")
            return True
    except Exception as e:
        print(f"Error resizing {image_path}: {e}")
        return False

def main():
    image_dir = "images"
    
    if not os.path.exists(image_dir):
        print(f"Error: Directory '{image_dir}' not found!")
        return
    
    # Find the largest dimension
    print("Scanning images to find largest dimension...\n")
    square_size = find_largest_dimension(image_dir)
    
    if square_size == 0:
        print("No valid images found!")
        return
    
    # Ask for confirmation
    print(f"\nAll images will be resized to {square_size}x{square_size} (square)")
    response = input("Continue? (y/n): ").strip().lower()
    
    if response != 'y':
        print("Cancelled.")
        return
    
    # Resize all images
    print("\nResizing images...\n")
    image_files = glob.glob(os.path.join(image_dir, "*.png"))
    success_count = 0
    
    for image_path in image_files:
        if resize_image_to_square(image_path, image_path, square_size):
            success_count += 1
    
    print(f"\nDone! Successfully resized {success_count}/{len(image_files)} images to {square_size}x{square_size}")

if __name__ == "__main__":
    main()


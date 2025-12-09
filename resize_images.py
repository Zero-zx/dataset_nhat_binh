import os
from PIL import Image
import glob
from collections import Counter

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

def detect_background_color(img):
    """Detect the solid background color by sampling from visible content areas."""
    width, height = img.size
    
    # First, composite onto white to see actual colors (for transparent images)
    if img.mode == 'RGBA':
        # Create white background
        white_bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
        img_composited = Image.alpha_composite(white_bg, img)
        img_to_sample = img_composited.convert('RGB')
    else:
        img_to_sample = img.convert('RGB')
    
    # Sample from multiple regions: avoid center (subject) but get visible background
    samples = []
    
    # Sample from outer regions (likely background, not subject)
    regions = [
        # Top region
        (width // 4, 0, width * 3 // 4, height // 4),
        # Bottom region
        (width // 4, height * 3 // 4, width * 3 // 4, height),
        # Left region
        (0, height // 4, width // 4, height * 3 // 4),
        # Right region
        (width * 3 // 4, height // 4, width, height * 3 // 4),
        # Corners
        (0, 0, width // 3, height // 3),
        (width * 2 // 3, 0, width, height // 3),
        (0, height * 2 // 3, width // 3, height),
        (width * 2 // 3, height * 2 // 3, width, height),
    ]
    
    for x1, y1, x2, y2 in regions:
        # Sample every few pixels in this region
        step_x = max(1, (x2 - x1) // 20)
        step_y = max(1, (y2 - y1) // 20)
        for y in range(y1, y2, step_y):
            for x in range(x1, x2, step_x):
                if 0 <= x < width and 0 <= y < height:
                    pixel = img_to_sample.getpixel((x, y))
                    if len(pixel) >= 3:
                        samples.append(pixel[:3])
    
    if samples:
        # Find most common color
        color_counts = Counter(samples)
        # Get the most common color
        bg_color = color_counts.most_common(1)[0][0]
        return bg_color
    
    return (255, 255, 255)  # Default to white

def resize_image_to_square(image_path, output_path, square_size):
    """Resize an image to a square size with background color extended."""
    try:
        with Image.open(image_path) as img:
            # First, ensure we have RGBA to detect solid colors from transparent images
            if img.mode != 'RGBA':
                img_rgba = img.convert('RGBA')
            else:
                img_rgba = img.copy()
            
            # Detect background color from visible content areas
            bg_color = detect_background_color(img_rgba)
            
            # Composite the RGBA image onto the detected background color
            # This ensures transparent areas are filled with the correct background
            bg_img = Image.new('RGBA', img_rgba.size, bg_color + (255,))
            img_composited = Image.alpha_composite(bg_img, img_rgba)
            
            # Convert to RGB for final processing
            img_rgb = img_composited.convert('RGB')
            
            # Calculate padding to center the image
            width, height = img_rgb.size
            
            # Calculate scaling to fit within square while maintaining aspect ratio
            scale = min(square_size / width, square_size / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Resize image
            img_resized = img_rgb.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create a new square image with detected background color
            square_img = Image.new('RGB', (square_size, square_size), bg_color)
            
            # Calculate position to center the resized image
            x_offset = (square_size - new_width) // 2
            y_offset = (square_size - new_height) // 2
            
            # Paste the resized image onto the square canvas
            square_img.paste(img_resized, (x_offset, y_offset))
            
            # Save the result
            square_img.save(output_path, 'PNG')
            print(f"Resized: {os.path.basename(image_path)} -> {os.path.basename(output_path)} (bg: {bg_color})")
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


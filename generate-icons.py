#!/usr/bin/env python3        
"""
SNT Tools - Icon Generator Script
Generates all required PWA icons from a source image.

Requirements:
    pip install Pillow cairosvg

Usage:
    python generate-icons.py [source_image]
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is not installed.")
    print("Install with: pip install Pillow")
    sys.exit(1)

try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False
    print("Warning: cairosvg not installed. SVG support disabled.")
    print("Install with: pip install cairosvg")

# Icon sizes to generate
STANDARD_SIZES = [16, 32, 57, 60, 72, 76, 96, 114, 120, 128, 144, 152, 180, 192, 384, 512]
MASKABLE_SIZES = [192, 512]

def load_image(source_path):
    """Load image from file, handling SVG conversion."""
    source_path = Path(source_path)
    
    if source_path.suffix.lower() == '.svg':
        if not HAS_CAIROSVG:
            print("Error: Cannot process SVG without cairosvg.")
            print("Install with: pip install cairosvg")
            sys.exit(1)
        
        # Convert SVG to PNG at high resolution
        png_data = cairosvg.svg2png(url=str(source_path), output_width=512, output_height=512)
        from io import BytesIO
        return Image.open(BytesIO(png_data))
    else:
        return Image.open(source_path)

def create_icon(source_img, size, output_path, maskable=False):
    """Create a single icon at specified size."""
    # Create a copy and resize
    img = source_img.copy()
    
    if maskable:
        # For maskable icons, add padding (content in center 80%)
        # Calculate the size the content should be (80% of final size)
        content_size = int(size * 0.8)
        img = img.resize((content_size, content_size), Image.Resampling.LANCZOS)
        
        # Create background with theme color
        background = Image.new('RGBA', (size, size), (0, 64, 128, 255))  # #004080
        
        # Paste resized content in center
        offset = (size - content_size) // 2
        if img.mode == 'RGBA':
            background.paste(img, (offset, offset), img)
        else:
            background.paste(img, (offset, offset))
        img = background
    else:
        # Standard resize
        img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Convert to RGB if saving as PNG (remove alpha if needed)
    if img.mode == 'RGBA':
        # Keep RGBA for transparency
        pass
    elif img.mode != 'RGB':
        img = img.convert('RGBA')
    
    img.save(output_path, 'PNG')
    print(f"  Created: {output_path}")

def generate_all_icons(source_path, output_dir='icons'):
    """Generate all PWA icons from source image."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"Loading source: {source_path}")
    source_img = load_image(source_path)
    
    # Ensure source is RGBA for transparency support
    if source_img.mode != 'RGBA':
        source_img = source_img.convert('RGBA')
    
    print(f"\nGenerating standard icons...")
    for size in STANDARD_SIZES:
        create_icon(source_img, size, output_dir / f'icon-{size}.png')
    
    print(f"\nGenerating maskable icons...")
    for size in MASKABLE_SIZES:
        create_icon(source_img, size, output_dir / f'icon-maskable-{size}.png', maskable=True)
    
    # Create favicon.ico
    print(f"\nGenerating favicon.ico...")
    sizes_for_ico = [16, 32, 48]
    ico_images = []
    for size in sizes_for_ico:
        img = source_img.copy()
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        ico_images.append(img)
    
    ico_images[0].save(
        output_dir / 'favicon.ico',
        format='ICO',
        sizes=[(s, s) for s in sizes_for_ico]
    )
    print(f"  Created: {output_dir / 'favicon.ico'}")
    
    print(f"\n✓ All icons generated in {output_dir}/")
    print("\nNext steps:")
    print("1. Review the generated icons")
    print("2. Test maskable icons at https://maskable.app/")
    print("3. Deploy your PWA")

def main():
    if len(sys.argv) > 1:
        source = sys.argv[1]
    else:
        # Default source
        source = 'icons/icon.svg'
        if not Path(source).exists():
            source = 'icons/icon.png'
    
    if not Path(source).exists():
        print(f"Error: Source file '{source}' not found.")
        print("\nUsage: python generate-icons.py [source_image]")
        print("\nProvide a source image (512x512 PNG or SVG recommended)")
        sys.exit(1)
    
    generate_all_icons(source)

if __name__ == '__main__':
    main()

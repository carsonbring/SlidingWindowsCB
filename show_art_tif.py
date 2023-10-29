import matplotlib.pyplot as plt
import tifffile
import os

# Set the directory containing the TIFF files
directory = 'img_artificial'

# List all TIFF files in the directory
tiff_files = [file for file in os.listdir(directory) if file.endswith('.tif')]

# Display each TIFF file
for tiff_file in tiff_files:
    # Construct the full path
    file_path = os.path.join(directory, tiff_file)
    
    # Read and display the image using tifffile
    img = tifffile.imread(file_path)
    plt.imshow(img, cmap='gray')  # Assuming grayscale images
    plt.title(tiff_file)
    plt.show()

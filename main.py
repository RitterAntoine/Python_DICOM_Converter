import os
import pydicom
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image
import numpy as np


input_dicom_folder = "data"
output_folder = 'output'
output_image_width = 480
output_image_height = 480
duration_in_milliseconds_between_each_image = 200
png_file_extension = '.png'
gif_file_extension = '.gif'
grayscale_colormap = 'gray'
minimum_value_for_normalization = 0
maximum_value_for_normalization = 255


def find_dicom_files(directory: str) -> List[str]:
    list_of_all_dicom_files_found = []
    
    for current_folder, list_of_subfolders, list_of_files_in_folder in os.walk(directory):
        for file_name in list_of_files_in_folder:
            complete_file_path = os.path.join(current_folder, file_name)
            
            try:
                pydicom.dcmread(complete_file_path, stop_before_pixels=True)
                list_of_all_dicom_files_found.append(complete_file_path)
            except Exception:
                pass
    
    return list_of_all_dicom_files_found

def load_dicom_image(file_path: str) -> np.ndarray:
    dicom_data = pydicom.dcmread(file_path)
    pixel_array_of_the_image = dicom_data.pixel_array
    
    return pixel_array_of_the_image

def normalize_image(image_array: np.ndarray) -> np.ndarray:
    if image_array.dtype == np.uint8:
        return image_array
    
    minimum_pixel_value_in_image = image_array.min()
    maximum_pixel_value_in_image = image_array.max()
    
    if maximum_pixel_value_in_image > minimum_pixel_value_in_image:
        difference_between_min_and_max = maximum_pixel_value_in_image - minimum_pixel_value_in_image
        image_scaled_between_zero_and_one = (image_array - minimum_pixel_value_in_image) / difference_between_min_and_max
        image_scaled_between_zero_and_two_hundred_fifty_five = image_scaled_between_zero_and_one * maximum_value_for_normalization
        image_converted_to_unsigned_integers = image_scaled_between_zero_and_two_hundred_fifty_five.astype(np.uint8)
        return image_converted_to_unsigned_integers
    else:
        black_image_of_same_size = np.zeros_like(image_array, dtype=np.uint8)
        return black_image_of_same_size


def save_3d_image(image_array: np.ndarray, output_path: str) -> None:
    output_path_with_gif_extension = output_path.replace(png_file_extension, gif_file_extension)
    list_of_all_images_for_animation = []
    total_number_of_slices_in_3d_image = image_array.shape[0]
    
    for index_of_current_slice in range(total_number_of_slices_in_3d_image):
        pixel_array_of_current_slice = image_array[index_of_current_slice]
        slice_normalized_between_zero_and_two_hundred_fifty_five = normalize_image(pixel_array_of_current_slice)
        pil_image_of_the_slice = Image.fromarray(slice_normalized_between_zero_and_two_hundred_fifty_five)
        pil_image_resized = pil_image_of_the_slice.resize((output_image_width, output_image_height), Image.Resampling.LANCZOS)
        list_of_all_images_for_animation.append(pil_image_resized)
    
    first_image_of_the_list = list_of_all_images_for_animation[0]
    all_images_except_the_first = list_of_all_images_for_animation[1:]
    
    first_image_of_the_list.save(
        output_path_with_gif_extension,
        save_all=True,
        append_images=all_images_except_the_first,
        duration=duration_in_milliseconds_between_each_image,
        loop=0
    )


def save_2d_image(image_array: np.ndarray, output_path: str) -> None:
    image_normalized = normalize_image(image_array)
    pil_image_to_save = Image.fromarray(image_normalized)
    pil_image_to_save.save(output_path)


def save_image(image_array: np.ndarray, output_path: str) -> None:
    if image_array.ndim == 3:
        save_3d_image(image_array, output_path)
    else:
        save_2d_image(image_array, output_path)

def main():
    list_of_all_dicom_files_found = find_dicom_files(input_dicom_folder)
    total_number_of_dicom_files_found = len(list_of_all_dicom_files_found)
    print(f"Found {total_number_of_dicom_files_found} DICOM files in '{input_dicom_folder}'.")
    
    for complete_path_of_current_dicom_file in list_of_all_dicom_files_found:
        pixel_array_loaded_from_dicom = load_dicom_image(complete_path_of_current_dicom_file)
        
        relative_path_of_file_from_source_folder = os.path.relpath(complete_path_of_current_dicom_file, input_dicom_folder)
        complete_path_of_output_file = os.path.join(output_folder, relative_path_of_file_from_source_folder)
        
        path_ends_with_png_extension = complete_path_of_output_file.endswith(png_file_extension)
        if not path_ends_with_png_extension:
            complete_path_of_output_file += png_file_extension
        
        parent_folder_of_output_file = os.path.dirname(complete_path_of_output_file)
        os.makedirs(parent_folder_of_output_file, exist_ok=True)
        
        if pixel_array_loaded_from_dicom.ndim == 3:
            final_path = complete_path_of_output_file.replace(png_file_extension, gif_file_extension)
        else:
            final_path = complete_path_of_output_file
        
        save_image(pixel_array_loaded_from_dicom, final_path)
        print(f"Saved: {final_path}")

if __name__ == "__main__":
    main()
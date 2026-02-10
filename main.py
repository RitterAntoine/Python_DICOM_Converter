import os
import pydicom
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image
import numpy as np


folder_containing_dicom_files_to_process = "data"
destination_folder_for_converted_images = 'output'
image_width_for_gif_output = 480
image_height_for_gif_output = 480
duration_in_milliseconds_between_each_image = 200
number_of_loops_zero_means_infinite = 0
png_file_extension = '.png'
gif_file_extension = '.gif'
grayscale_colormap = 'gray'
minimum_value_for_normalization = 0
maximum_value_for_normalization = 255
number_of_dimensions_for_3d_image = 3
divisor_to_get_middle_index = 2


def find_dicom_files(directory: str) -> List[str]:
    list_of_all_dicom_files_found = []
    
    for current_folder, list_of_subfolders, list_of_files_in_folder in os.walk(directory):
        for file_name in list_of_files_in_folder:
            complete_path_of_the_file = os.path.join(current_folder, file_name)
            
            try:
                pydicom.dcmread(complete_path_of_the_file, stop_before_pixels=True)
                list_of_all_dicom_files_found.append(complete_path_of_the_file)
            except Exception:
                pass
    
    return list_of_all_dicom_files_found

def load_dicom_image(file_path: str) -> np.ndarray:
    medical_dicom_data = pydicom.dcmread(file_path)
    pixel_array_of_the_image = medical_dicom_data.pixel_array
    
    return pixel_array_of_the_image

def display_image(image_array: np.ndarray, title: Optional[str] = None, show: bool = False) -> None:
    pixel_array_to_display = image_array
    
    if pixel_array_to_display.ndim == number_of_dimensions_for_3d_image:
        total_number_of_slices_in_image = pixel_array_to_display.shape[0]
        index_of_the_middle_slice = total_number_of_slices_in_image // divisor_to_get_middle_index
        pixel_array_to_display = pixel_array_to_display[index_of_the_middle_slice]
    
    if show:
        plt.imshow(pixel_array_to_display, cmap=grayscale_colormap)
        if title:
            plt.title(title)
        plt.axis('off')
        plt.show()

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
        pil_image_resized_to_480_by_480 = pil_image_of_the_slice.resize((image_width_for_gif_output, image_height_for_gif_output), Image.Resampling.LANCZOS)
        list_of_all_images_for_animation.append(pil_image_resized_to_480_by_480)
    
    first_image_of_the_list = list_of_all_images_for_animation[0]
    all_images_except_the_first = list_of_all_images_for_animation[1:]
    
    first_image_of_the_list.save(
        output_path_with_gif_extension,
        save_all=True,
        append_images=all_images_except_the_first,
        duration=duration_in_milliseconds_between_each_image,
        loop=number_of_loops_zero_means_infinite
    )


def save_2d_image(image_array: np.ndarray, output_path: str) -> None:
    image_normalized_between_zero_and_two_hundred_fifty_five = normalize_image(image_array)
    pil_image_to_save = Image.fromarray(image_normalized_between_zero_and_two_hundred_fifty_five)
    pil_image_to_save.save(output_path)


def save_image(image_array: np.ndarray, output_path: str) -> None:
    number_of_dimensions_of_pixel_array = image_array.ndim
    image_has_three_dimensions = number_of_dimensions_of_pixel_array == number_of_dimensions_for_3d_image
    
    if image_has_three_dimensions:
        save_3d_image(image_array, output_path)
    else:
        save_2d_image(image_array, output_path)

def main():
    list_of_all_dicom_files_found = find_dicom_files(folder_containing_dicom_files_to_process)
    total_number_of_dicom_files_found = len(list_of_all_dicom_files_found)
    print(f"Found {total_number_of_dicom_files_found} DICOM files in '{folder_containing_dicom_files_to_process}'.")
    
    for complete_path_of_current_dicom_file in list_of_all_dicom_files_found:
        pixel_array_loaded_from_dicom = load_dicom_image(complete_path_of_current_dicom_file)
        
        file_name_without_path = os.path.basename(complete_path_of_current_dicom_file)
        display_image(pixel_array_loaded_from_dicom, title=file_name_without_path, show=False)
        
        relative_path_of_file_from_source_folder = os.path.relpath(complete_path_of_current_dicom_file, folder_containing_dicom_files_to_process)
        complete_path_of_output_file = os.path.join(destination_folder_for_converted_images, relative_path_of_file_from_source_folder)
        
        path_ends_with_png_extension = complete_path_of_output_file.endswith(png_file_extension)
        if not path_ends_with_png_extension:
            complete_path_of_output_file += png_file_extension
        
        parent_folder_of_output_file = os.path.dirname(complete_path_of_output_file)
        os.makedirs(parent_folder_of_output_file, exist_ok=True)
        
        image_has_three_dimensions = pixel_array_loaded_from_dicom.ndim == number_of_dimensions_for_3d_image
        if image_has_three_dimensions:
            final_path_actually_used = complete_path_of_output_file.replace(png_file_extension, gif_file_extension)
        else:
            final_path_actually_used = complete_path_of_output_file
        
        save_image(pixel_array_loaded_from_dicom, final_path_actually_used)
        print(f"Saved: {final_path_actually_used}")

if __name__ == "__main__":
    main()
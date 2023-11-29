import os
import pdal
import json

def laz_to_las(input_laz_file, output_las_file):
    
    input_laz_file = input_laz_file.replace('\\', '\\\\')
    output_las_file = output_las_file.replace("\\", '\\\\')
    #defining the PDAL pipeline for converting Laz to Las
    pdal_pipeline_json = f"""
    {{
        "pipeline": [
            {{
                "type": "readers.las",
                "filename": "{input_laz_file}"
            }},
            {{
                "type": "writers.las",
                "filename": "{output_las_file}"
            }}
        ]
    }}
    """
    pipeline = pdal.Pipeline(pdal_pipeline_json)
    pipeline.execute()

def las_to_tif(input_las_file, output_tif_file):

    input_las_file =input_las_file.replace('\\', '\\\\')
    output_tif_file = output_tif_file.replace('\\', '\\\\')
    #defining the PDAL pipeline for converting Las to TIF
    pdal_pipeline_json = f"""
    {{
        "pipeline": [
            {{
                "type": "readers.las",
                "filename": "{input_las_file}"
            }},
            {{
                "type": "writers.gdal",
                "filename": "{output_tif_file}",
                "output_type": "idw",
                "resolution": 6.0 
            }}
        ]
    }}
    """
    pipeline = pdal.Pipeline(pdal_pipeline_json)
    pipeline.execute()

laz_file_directory = os.getcwd() + "\\laz_files\\NDSouthWest.laz"
las_file_directory = os.getcwd() + "\\laz_files\\NDSouthWest.las"

#converting Laz to Las
laz_to_las(laz_file_directory, las_file_directory)

#converting Las to TIF
output_tif_file = os.getcwd() + "\\img_souris\\NDSouthWest.tif"
las_to_tif(las_file_directory, output_tif_file)

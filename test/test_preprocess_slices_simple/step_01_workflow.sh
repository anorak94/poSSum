#!/bin/bash -xe

specimen_id=brainmaps_s40

DIR_RAW_SLICES=00_source_sections
DIR_RAW_REFERENCE=01_raw_reference
DIR_INPUT_DATA=10_input_data

RESLICE_BACKGROUND=255


#--------------------------------------------------------------------
# Prepare the directory structure. It is not complicated this time
#--------------------------------------------------------------------
rm -rf ${DIR_RAW_SLICES} ${DIR_INPUT_DATA}
mkdir -p ${DIR_RAW_SLICES} ${DIR_INPUT_DATA}


#--------------------------------------------------------------------
# Try extracting the test sections from the archive
#--------------------------------------------------------------------
tar -xvvzf 00_source_sections.tgz


#--------------------------------------------------------------------
# Download the image stack to reconstruct. In case it is not already
# downloaded.
#--------------------------------------------------------------------
for section in `cat sections_to_download`
do
    if [ ! -f  ${DIR_RAW_SLICES}/${section}.jpg ]; then
        wget http://brainmaps.org/HBP-JPG/40/${section}.jpg \
            -O ${DIR_RAW_SLICES}/${section}.jpg 
    fi
done 

pos_process_source_images \
     --loglevel=DEBUG \
     -d ${DIR_INPUT_DATA} \
     --input-images-dir ${DIR_RAW_SLICES} \
     --input-workbook ${specimen_id}.xls \
     --output-workbook ${specimen_id}_processed.xls \
     --header-file header.sh \
     \
     --enable-process-source-images \
         --canvas-gravity Center \
         --canvas-background White \
         --mask-threshold 84.0 \
         --mask-median 2 \
         --mask-color-channel red \
         --masking-background ${RESLICE_BACKGROUND} \
     \
     --enable-source-stacking \
         --use-slice-to-slice-mask \
     \
     --enable-remasking \
     \
     --enable-slice-extraction \
     \
     --disable-reference

#--------------------------------------------------------------------
# Only now we can load the actual header file
#--------------------------------------------------------------------
source header.sh


#--------------------------------------------------------------------
# Below we are testing the behaviour of the slicing and restacking
# functions which purpose is to... slice the stack into individual
# sections and then stack it back into 3D image.
# Sound silly but it is suprisingly usefull.
#--------------------------------------------------------------------
tempdir=`hd_split_volume ${VOL_RGB_MASKED}`
hd_stack_sections ${tempdir} rgb_stack-sectioned_and_stacked_back.nii.gz
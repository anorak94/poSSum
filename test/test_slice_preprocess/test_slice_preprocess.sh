#!/bin/bash
set -xe 

# Image downloaded from the BrainMaps.org website: 
# http://brainmaps.org/ajax-viewer.php?datid=42&sname=459

INPUT_IMAGE=test_input
rm -rfv ${INPUT_IMAGE}_*.*

pos_preprocess_image \
    -i ${INPUT_IMAGE}.nii.gz \
    -g ${INPUT_IMAGE}_g_1.nii.gz \
    -r ${INPUT_IMAGE}_r_1.nii.gz 

pos_preprocess_image \
    -i ${INPUT_IMAGE}.nii.gz \
    -g ${INPUT_IMAGE}_g_3.nii.gz \
    -r ${INPUT_IMAGE}_r_3.nii.gz \
    --color-channel red

pos_preprocess_image \
    -i ${INPUT_IMAGE}.nii.gz \
    -g ${INPUT_IMAGE}_g_4.nii.gz \
    -r ${INPUT_IMAGE}_r_4.nii.gz \
    --color-channel red \
    --invert-source-image \
    --invert-rgb-image

pos_preprocess_image \
    -i ${INPUT_IMAGE}.nii.gz \
    -g ${INPUT_IMAGE}_g_5.nii.gz \
    -r ${INPUT_IMAGE}_r_5.nii.gz \
    --color-channel red \
    --invert-source-image \
    --median-filter-radius 3 3 \
    --invert-rgb-image

pos_preprocess_image \
    -i ${INPUT_IMAGE}.nii.gz \
    -g ${INPUT_IMAGE}_g_6.nii.gz \
    -r ${INPUT_IMAGE}_r_6.nii.gz \
    --extract-roi 200 200 250 250 \
    --resize-factor 0.5

pos_preprocess_image \
    -i ${INPUT_IMAGE}.nii.gz \
    -g ${INPUT_IMAGE}_g_8.nii.gz \
    -r ${INPUT_IMAGE}_r_8.nii.gz \
    --extract-roi 100 100 350 350 \
    --resize-factor 0.5

pos_preprocess_image \
    -i ${INPUT_IMAGE}.nii.gz \
    -g ${INPUT_IMAGE}_g_7.nii.gz \
    -r ${INPUT_IMAGE}_r_7.nii.gz \
    --extract-roi 100 100 350 350 \
    --resize-factor 0.5 \
    --median-filter-radius 4 4 \
    --invert-rgb-image

md5sum -c test_slice_preprocess.md5
exit $?

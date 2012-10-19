mkdir -p /dev/shm/uniform/
#---------------------------------------------------------
# This code gives nice effects 

#   c3d \
#       /home/pmajka/possum/data/02_02_NN2/70_blockface_to_histology_registration/02_02_NN2_final_nissl_r.nii.gz \
#       -scale -1 -shift 255 \
#       /home/pmajka/Dropbox/Photos/oposy_skrawki/02_02_NN2/02_02_NN2_final_nissl_mask.nii.gz \
#       -times \
#       -scale -1 -shift 255 \
#       -type uchar -o 02_02_NN2_final_nissl_masked.nii.gz

c3d /home/pmajka/Dropbox/Photos/oposy_skrawki/02_02_NN2/02_02_NN2_final_nissl_mask.nii.gz -replace 2 1 -type uchar -o mask.nii.gz

START_SLICE=0
END_SLICE=263

#   python framework/deformable_histology_reconstruction_4.py \
#       --inputVolume   1 02_02_NN2_final_nissl_masked.nii.gz \
#       --outlineVolume 0 mask.nii.gz \
#       --maskedVolume 1 02_tm.nii.gz \
#       --maskedVolumeFile processing/02_02_NN2_masked_custom.csv \
#       --startSlice ${START_SLICE} \
#       --endSlice ${END_SLICE} \
#       --iterations 4 \
#       --neighbourhood 1 \
#       -d /dev/shm/uniform/ \
#       --outputNaming new_test_1 \
#       --antsImageMetricOpt 16 \
#       --antsTransformation 0.05 \
#       --antsRegularization 3.0 1.0 \
#       --antsIterations 1000x1000x1000x0x0 \
#       --outputVolumePermutationOrder 0 2 1 \
#       --outputVolumeSpacing 0.01584 0.08 0.01584 \
#       --outputVolumeOrigin 0 0.04 0 \
#       --outputVolumeOrientationCode RAS
#         
#   python framework/deformable_histology_reconstruction_4.py \
#       --inputVolume   1 02_02_NN2_final_nissl_masked.nii.gz \
#       --outlineVolume 0 mask.nii.gz \
#       --registerSubset processing/02_02_NN2_outliers.csv \
#       --startSlice ${START_SLICE} \
#       --endSlice ${END_SLICE} \
#       --iterations 8 \
#       --startFromIteration 4 \
#       --neighbourhood 1 \
#       -d /dev/shm/uniform/ \
#       --outputNaming new_test_1 \
#       --antsImageMetricOpt 16 \
#       --antsTransformation 0.05 \
#       --antsRegularization 1.0 1.0 \
#       --antsIterations 1000x1000x1000x0x0 \
#       --outputVolumePermutationOrder 0 2 1 \
#       --outputVolumeSpacing 0.01584 0.08 0.01584 \
#       --outputVolumeOrigin 0 0.04 0 \
#       --outputVolumeOrientationCode RAS

#   python framework/deformable_histology_reconstruction_4.py \
#       --inputVolume   0 02_02_NN2_final_nissl_masked.nii.gz \
#       --outlineVolume 1 mask.nii.gz \
#       --startSlice ${START_SLICE} \
#       --endSlice ${END_SLICE} \
#       --startFromIteration 8 \
#       --iterations 13 \
#       --neighbourhood 1 \
#       -d /dev/shm/uniform/ \
#       --outputNaming new_test_1 \
#       --antsImageMetricOpt 16 \
#       --antsTransformation 0.05 \
#       --antsRegularization 1.0 1.0 \
#       --antsIterations 1000x1000x1000x0000x0000 \
#       --outputVolumePermutationOrder 0 2 1 \
#       --outputVolumeSpacing 0.01584 0.08 0.01584 \
#       --outputVolumeOrigin 0 0.04 0 \
#       --outputVolumeOrientationCode RAS

#   python framework/deformable_histology_reconstruction_4.py \
#       --inputVolume   1 02_02_NN2_final_nissl_masked.nii.gz \
#       --outlineVolume 0 mask.nii.gz \
#       --startSlice ${START_SLICE} \
#       --endSlice ${END_SLICE} \
#       --startFromIteration 13 \
#       --iterations 18 \
#       --neighbourhood 1 \
#       -d /dev/shm/uniform/ \
#       --outputNaming new_test_1 \
#       --antsImageMetricOpt 2 \
#       --antsTransformation 0.01 \
#       --antsRegularization 1.0 1.0 \
#       --antsIterations 1000x1000x1000x0000x0000 \
#       --outputVolumePermutationOrder 0 2 1 \
#       --outputVolumeSpacing 0.01584 0.08 0.01584 \
#       --outputVolumeOrigin 0 0.04 0 \
#       --outputVolumeOrientationCode RAS

    python framework/deformable_histology_reconstruction_4.py \
        --inputVolume   1 02_02_NN2_final_nissl_masked.nii.gz \
        --outlineVolume 0 mask.nii.gz \
        --startSlice ${START_SLICE} \
        --endSlice ${END_SLICE} \
        --startFromIteration 18 \
        --iterations 24 \
        --neighbourhood 1 \
        -d /dev/shm/uniform/ \
        --outputNaming new_test_1 \
        --antsImageMetricOpt 4 \
        --antsTransformation 0.01 \
        --antsRegularization 1.0 1.0 \
        --antsIterations 1000x1000x1000x1000x1000 \
        --outputVolumePermutationOrder 0 2 1 \
        --outputVolumeSpacing 0.01584 0.08 0.01584 \
        --outputVolumeOrigin 0 0.04 0 \
        --outputVolumeOrientationCode RAS

#   # ------------------------------------------------------------------
#   # Good for eliminating the outliers - smaller gradient
#      python framework/deformable_histology_reconstruction_4.py \
#          --inputVolume   1 02_02_NN2_final_nissl_masked.nii.gz \
#          --registerSubset processing/02_02_NN2_outliers.csv \
#          --startSlice 0 \
#          --endSlice 263 \
#          --iterations 5 \
#          --neighbourhood 1 \
#          -d /dev/shm/uniform/ \
#          --outputNaming new_test_1 \
#          --antsImageMetricOpt 16 \
#          --antsTransformation 0.05 \
#          --antsRegularization 1.0 1.0 \
#          --antsIterations 1000x1000x1000x0x0 \
#          --outputVolumePermutationOrder 0 2 1 \
#          --outputVolumeSpacing 0.01584 0.08 0.01584 \
#          --outputVolumeOrigin 0 0.04 0 \
#          --outputVolumeOrientationCode RAS


#   # --------------------------------------------------------
#   # Elliminate outlies by ergistering whole slides to 
#   # their average image

#      python framework/deformable_histology_reconstruction_4.py \
#          --inputVolume   1 02_02_NN2_final_nissl_masked.nii.gz \
#          --outlineVolume 0 /home/pmajka/Dropbox/Photos/oposy_skrawki/02_02_NN2/02_02_NN2_final_nissl_mask.nii.gz \
#          --maskedVolume 0 02_tm.nii.gz \
#          --skipSlicePreprocess \
#          --registerSubset processing/02_02_NN2_outliers.csv \
#          --startSlice 0 \
#          --endSlice 263 \
#          --startFromIteration 1 \
#          --iterations 7 \
#          --neighbourhood 1 \
#          -d /dev/shm/uniform/ \
#          --outputNaming new_test_1 \
#          --antsImageMetricOpt 16 \
#          --antsTransformation 0.15 \
#          --antsRegularization 1.0 1.0 \
#          --antsIterations 1000x1000x1000x0x0 \
#          --outputVolumePermutationOrder 0 2 1 \
#          --outputVolumeSpacing 0.01584 0.08 0.01584 \
#          --outputVolumeOrigin 0 0.04 0 \
#          --outputVolumeOrientationCode RAS

   
# ----------------------------------------------------------------
# 
   
#  
#       --skipSlicePreprocess \
#  python framework/deformable_histology_reconstruction_3.py \
#      -i /home/pmajka/Dropbox/Photos/oposy_skrawki/02_02_NN2/02_02_NN2_final_nissl_mask.nii.gz \
#      --startSlice 0 \
#      --endSlice 263 \
#      --neighbourhood 1 \
#      --startFromIteration 5 \
#      --iterations 8 \
#      -d /dev/shm/uniform/ \
#      --outputNaming DG-dilated-rs \
#      --antsImageMetricOpt 16 \
#      --antsTransformation 0.05 \
#      --antsRegularization 1.0 1.0 \
#      --antsIterations 1000x1000x1000x1000x0000 \
#      --outputVolumePermutationOrder 0 2 1 \
#      --outputVolumeSpacing 0.01584 0.08 0.01584 \
#      --outputVolumeOrigin 0 0.04 0 \
#      --outputVolumeOrientationCode RAS
#  
#  python framework/deformable_histology_reconstruction_3.py \
#      -i /home/pmajka/Dropbox/Photos/oposy_skrawki/02_02_NN2/02_02_NN2_final_nissl_mask.nii.gz \
#       --startSlice 0 \
#       --endSlice 263 \
#       --neighbourhood 1 \
#       --startFromIteration 8 \
#       --iterations 11 \
#       -d /dev/shm/uniform/ \
#       --outputNaming DG-dilated-rs \
#       --antsImageMetricOpt 16 \
#       --antsTransformation 0.05 \
#       --antsRegularization 1.0 1.0 \
#       --antsIterations 1000x1000x1000x1000x1000 \
#       --outputVolumePermutationOrder 0 2 1 \
#       --outputVolumeSpacing 0.01584 0.08 0.01584 \
#       --outputVolumeOrigin 0 0.04 0 \
#       --outputVolumeOrientationCode RAS

# 
#---------------------------------------------------------
   

#!/usr/bin/python

import copy
import numpy as np

from pos_parameters import ants_intensity_meric, ants_registration, images_weighted_average
from pos_deformable_wrappers import blank_slice_deformation_wrapper
from pos_wrapper_skel import generic_workflow
from pos_filenames import filename

class deformable_reconstruction_iteration(generic_workflow):
    _f = { \
        'src_slice'  : filename('src_slice',  work_dir = '00_src_slices',      str_template =  '{idx:04d}.nii.gz'),
        'processed'  : filename('processed',  work_dir = '01_process_slices',  str_template =  '{idx:04d}.nii.gz'),
        'outline'    : filename('outline',    work_dir = '02_outline',         str_template =  '{idx:04d}.nii.gz'),
        'poutline'   : filename('poutline',   work_dir = '03_poutline',        str_template =  '{idx:04d}.nii.gz'),
        'cmask'      : filename('cmask',      work_dir = '04_cmask',           str_template =  '{idx:04d}.nii.gz'),
        'pcmask'     : filename('pcmask',     work_dir = '05_pcmask',          str_template =  '{idx:04d}.nii.gz'),
        'transform'  : filename('transform',  work_dir = '11_transformations', str_template =  '{idx:04d}Warp.nii.gz'),
        'out_naming' : filename('out_naming', work_dir = '11_transformations', str_template = '{idx:04d}'),
        'resliced'   : filename('resliced',   work_dir = '21_resliced',        str_template = '{idx:04d}.nii.gz'),
        'resliced_outline' : filename('resliced_outline', work_dir = '22_resliced_outline', str_template = '{idx:04d}.nii.gz'),
        'resliced_custom'  : filename('resliced_custom', work_dir = '24_resliced_custom', str_template = '{idx:04d}.nii.gz')
        }
    
    _usage = ""
    
    def __init__(self, options, args, pool = None):
        super(self.__class__, self).__init__(options, args, pool)
        
        start, end, eps = self._get_edges()
        self.slice_range = range(start, end +1)
        
        self._load_subset_file()
        self._read_custom_registration_assignment()
        
        # Convert the number of iterations string to list of integers
        self.options.antsIterations = \
                map(int, self.options.antsIterations.strip().split("x"))
    
    def _read_custom_registration_assignment(self):
        if self.options.maskedVolume and \
                self.options.maskedVolumeWeight > 0 and \
                self.options.maskedVolumeFile:
            
            masked_registraion = np.loadtxt(self.options.maskedVolumeFile)
            print masked_registraion
            self.masked_registraion = \
                    dict(map(lambda x: (int(x[0]), int(x[1])), masked_registraion))
            self.subset = self.masked_registraion.keys()
        else:
            self.masked_registraion = {}
    
    def _get_edges(self):
        """
        Convenience function for returning frequently used numbers
        """
        return (self.options.startSlice,
                self.options.endSlice,
                self.options.neighbourhood)
    
    def _load_subset_file(self):
        """
        Loads a subset of slices from a given file.
        When the additional file is provided, only slices with indices from the file
        will be registered.
        """
        if self.options.registerSubset:
            subset = np.loadtxt(self.options.registerSubset)
            self.subset = list(subset)
        else:
            self.subset = self.slice_range
    
    def _assign_weights_from_func(self):
        start, end, eps = self._get_edges()
        
        self.weights = {}
        for i in self.slice_range:
            for j in range(i - eps, i + eps+1):
                if j!=i and j<=end and j>=start:
                    self.weights[(i,j)] = 1
    
    def _assign_weights(self):
        self._assign_weights_from_func()
    
    def get_weight(self, i, j):
        return self.weights[(i,j)]
    
    def _preprocess_images(self):
        return self._average_images()
    
    def _average_images(self):
        start, end, eps = self._get_edges()
        
        if self.options.inputVolume and self.options.inputVolumeWeight > 0:
            commands = []
            
            for i in self.slice_range:
                files_to_average = []
                weights = []
                
                for j in range(i - eps, i + eps+1):
                    if j!=i and j<=end and j>=start:
                       files_to_average.append(self.f['src_slice'](idx=j))
                       weights.append(self.get_weight(i,j))
                
                command = images_weighted_average(\
                            dimension = 2,
                            input_images = files_to_average,
                            weights = weights,
                            output_type = 'float',
                            output_image = self.f['processed'](idx=i))
                commands.append(copy.deepcopy(command))
            
            self.execute(commands)
        
        if self.options.outlineVolume and self.options.outlineVolumeWeight > 0:
            commands = []
            
            for i in self.slice_range:
                files_to_average = []
                weights = []
                
                for j in range(i - eps, i + eps+1):
                    if j!=i and j<=end and j>=start:
                       files_to_average.append(self.f['outline'](idx=j))
                       weights.append(self.get_weight(i,j))
                
                command = images_weighted_average(\
                            dimension = 2,
                            input_images = files_to_average,
                            weights = weights,
                            output_type = 'float',
                            output_image = self.f['poutline'](idx=i))
                commands.append(copy.deepcopy(command))
            
            self.execute(commands)
    
    def _calculate_transformations_masked(self):
        start, end, eps = self._get_edges()
        
        commands = []
        
        for i in self.slice_range:
            metrics  = []
            j = self.masked_registraion.get(i, None) 
            
            if j == None:
                fixed_image_type = 'processed'
                fixed_outline_type='poutline'
                mask_image = None
                j=i
            else:
                fixed_image_type = 'src_slice'
                fixed_outline_type='outline'
                mask_image =  self.f['cmask'](idx=j)
            
            if self.options.inputVolume and self.options.inputVolumeWeight > 0:
                metric = ants_intensity_meric(
                            fixed_image  = self.f[fixed_image_type](idx=j),
                            moving_image = self.f['src_slice'](idx=i),
                            metric = self.options.antsImageMetric,
                            weight = self.options.inputVolumeWeight,
                            parameter = self.options.antsImageMetricOpt)
                metrics.append(copy.deepcopy(metric))
            
            if self.options.outlineVolume and self.options.outlineVolumeWeight > 0:
                outline_metric = ants_intensity_meric(
                            fixed_image  = self.f[fixed_outline_type](idx=j),
                            moving_image = self.f['outline'](idx=i),
                            metric = self.options.antsImageMetric,
                            weight = self.options.outlineVolumeWeight,
                            parameter = self.options.antsImageMetricOpt)
                metrics.append(copy.deepcopy(outline_metric))
            
            if i in self.subset:
                registration = ants_registration(
                            dimension = 2,
                            outputNaming = self.f['out_naming'](idx=i),
                            iterations = self.options.antsIterations,
                            transformation = ('SyN', [self.options.antsTransformation]),
                            regularization = (self.options.antsRegularizationType, self.options.antsRegularization),
                            affineIterations = [0],
                            continueAffine = False,
                            rigidAffine = False,
                            imageMetrics = metrics,
                            maskImage = mask_image,
                            allMetricsConverge = True)
            else:
                registration = blank_slice_deformation_wrapper(\
                        input_image = self.f['src_slice'](idx=i),
                        output_image = self.f['transform'](idx=i)
                        )
            commands.append(copy.deepcopy(registration))
        
        self.execute(commands)
    
#   def _calculate_transformations(self):
#       start, end, eps = self._get_edges()
#       
#       commands = []
#       metrics  = []
#       
#       for i in self.slice_range:
#           metrics = []
#           
#           metric = ants_intensity_meric(
#                       fixed_image  = self.f['processed'](idx=i),
#                       moving_image = self.f['src_slice'](idx=i),
#                       metric = self.options.antsImageMetric,
#                       weight = 1,
#                       parameter = self.options.antsImageMetricOpt)
#           metrics.append(metric)
#           
#           if self.options.outlineVolume and self.options.outlineVolumeWeight > 0:
#               outline_metric = ants_intensity_meric(
#                           fixed_image  = self.f['poutline'](idx=i),
#                           moving_image = self.f['outline'](idx=i),
#                           metric = self.options.antsImageMetric,
#                           weight = self.options.outlineVolumeWeight,
#                           parameter = self.options.antsImageMetricOpt)
#               metrics.append(outline_metric)
#           
#           if i in self.subset:
#               registration = ants_registration(
#                           dimension = 2,
#                           outputNaming = self.f['out_naming'](idx=i),
#                           iterations = self.options.antsIterations,
#                           transformation = ('SyN', [self.options.antsTransformation]),
#                           regularization = (self.options.antsRegularizationType, self.options.antsRegularization),
#                           affineIterations = [0],
#                           continueAffine = False,
#                           rigidAffine = False,
#                           imageMetrics = metrics,
#                           allMetricsConverge = True)
#           else:
#               registration = blank_slice_deformation_wrapper(\
#                       input_image = self.f['src_slice'](idx=i),
#                       output_image = self.f['transform'](idx=i)
#                       )
#           
#           commands.append(copy.deepcopy(registration))
#       
#       self.execute(commands)
    
    def launch(self):
        self._assign_weights()
        self._preprocess_images()
        #self._calculate_transformations()
        self._calculate_transformations_masked()
     
    def __call__(self, *args, **kwargs):
        return self.launch()


"""
Cython-optimized quality metrics calculations.
Performance-critical quality metric computations compiled to C.
Part of FREE_LIBRARIES_INTEGRATION - Worker 1 Task A3.2.

This module provides Cython-optimized versions of performance-critical
quality metrics calculations for 50%+ performance improvement.
"""

import numpy as np

cimport numpy as np
from libc.math cimport fabs, log10, pow, sqrt
from libc.stdlib cimport free, malloc


cdef double EPSILON = 1e-10

def calculate_dynamic_range_cython(np.ndarray[double, ndim=1] audio):
    """
    Cython-optimized dynamic range calculation.
    
    Args:
        audio: Input audio array
    
    Returns:
        Dynamic range value
    """
    cdef int n = audio.shape[0]
    cdef double min_val = audio[0]
    cdef double max_val = audio[0]
    cdef int i
    
    for i in range(1, n):
        if audio[i] < min_val:
            min_val = audio[i]
        if audio[i] > max_val:
            max_val = audio[i]
    
    return max_val - min_val


def calculate_zero_crossing_rate_cython(np.ndarray[double, ndim=1] audio):
    """
    Cython-optimized zero crossing rate calculation.
    
    Args:
        audio: Input audio array
    
    Returns:
        Zero crossing rate
    """
    cdef int n = audio.shape[0]
    if n < 2:
        return 0.0
    
    cdef int crossings = 0
    cdef int i
    
    for i in range(1, n):
        if (audio[i-1] >= 0.0 and audio[i] < 0.0) or (audio[i-1] < 0.0 and audio[i] >= 0.0):
            crossings += 1
    
    return <double>crossings / <double>n


def calculate_snr_cython(np.ndarray[double, ndim=1] audio):
    """
    Cython-optimized SNR calculation from single audio array.
    Estimates noise as lower energy portions.
    
    Args:
        audio: Audio array
    
    Returns:
        SNR in dB
    """
    cdef int n = audio.shape[0]
    if n == 0:
        return 0.0
    
    cdef double* power = <double*>malloc(n * sizeof(double))
    cdef double signal_power = 0.0
    cdef double noise_power = 0.0
    cdef double power_sum = 0.0
    cdef int i
    cdef int noise_count = 0
    cdef double threshold
    
    # Calculate power
    for i in range(n):
        power[i] = audio[i] * audio[i]
        power_sum += power[i]
    
    signal_power = power_sum / n
    
    # Estimate noise threshold (10th percentile)
    threshold = signal_power * 0.1
    
    for i in range(n):
        if power[i] < threshold:
            noise_power += power[i]
            noise_count += 1
    
    free(power)
    
    if noise_count == 0:
        noise_power = EPSILON
    else:
        noise_power = noise_power / noise_count
    
    if noise_power < EPSILON:
        noise_power = EPSILON
    
    return 10.0 * log10(signal_power / noise_power)


def calculate_mos_components_cython(
    np.ndarray[double, ndim=1] audio,
    double snr,
    double dynamic_range
):
    """
    Cython-optimized MOS score component calculations.
    
    Args:
        audio: Audio array
        snr: Pre-calculated SNR
        dynamic_range: Pre-calculated dynamic range
    
    Returns:
        Tuple of (snr_factor, dr_factor, spectral_factor)
    """
    cdef double snr_factor = min(1.0, max(0.0, (snr + 10.0) / 40.0))
    cdef double dr_factor = 0.0
    cdef double spectral_factor = 0.0
    
    if dynamic_range > 0:
        dr_factor = min(1.0, dynamic_range / 2.0)
    else:
        dr_factor = -0.5
    
    # Simplified spectral factor (would need FFT for full calculation)
    cdef int n = audio.shape[0]
    if n > 100:
        # Approximate spectral characteristics
        cdef double zcr = calculate_zero_crossing_rate_cython(audio)
        if 0.01 < zcr < 0.2:
            spectral_factor = 0.3
    
    return (snr_factor, dr_factor, spectral_factor)


def calculate_artifact_score_cython(np.ndarray[double, ndim=1] audio):
    """
    Cython-optimized artifact detection score.
    
    Args:
        audio: Audio array
    
    Returns:
        Artifact score (0.0 = no artifacts, 1.0 = many artifacts)
    """
    cdef int n = audio.shape[0]
    if n == 0:
        return 0.0
    
    cdef double clipping_count = 0.0
    cdef double sudden_changes = 0.0
    cdef int i
    cdef double change
    
    # Detect clipping
    for i in range(n):
        if fabs(audio[i]) > 0.99:
            clipping_count += 1.0
    
    # Detect sudden changes (potential artifacts)
    for i in range(1, n):
        change = fabs(audio[i] - audio[i-1])
        if change > 0.5:  # Sudden large change
            sudden_changes += 1.0
    
    cdef double clipping_ratio = clipping_count / n
    cdef double change_ratio = sudden_changes / n
    
    # Combine into artifact score
    return min(1.0, (clipping_ratio * 0.5 + change_ratio * 0.5) * 2.0)


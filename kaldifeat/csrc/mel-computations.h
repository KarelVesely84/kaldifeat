// kaldifeat/csrc/mel-computations.h
//
// Copyright (c)  2021  Xiaomi Corporation (authors: Fangjun Kuang)
//
// This file is copied/modified from kaldi/src/feat/mel-computations.h

#include <cmath>

#include "kaldifeat/csrc/feature-window.h"

#ifndef KALDIFEAT_CSRC_MEL_COMPUTATIONS_H_
#define KALDIFEAT_CSRC_MEL_COMPUTATIONS_H_

namespace kaldifeat {

struct MelBanksOptions {
  int32_t num_bins = 25;  // e.g. 25; number of triangular bins
  float low_freq = 20;    // e.g. 20; lower frequency cutoff

  // an upper frequency cutoff; 0 -> no cutoff, negative
  // ->added to the Nyquist frequency to get the cutoff.
  float high_freq = 0;

  float vtln_low = 100;  // vtln lower cutoff of warping function.

  // vtln upper cutoff of warping function: if negative, added
  // to the Nyquist frequency to get the cutoff.
  float vtln_high = -500;

  bool debug_mel = false;
  // htk_mode is a "hidden" config, it does not show up on command line.
  // Enables more exact compatibility with HTK, for testing purposes.  Affects
  // mel-energy flooring and reproduces a bug in HTK.
  bool htk_mode = false;

  std::string ToString() const {
    std::ostringstream os;
    os << "num_bins: " << num_bins << "\n";
    os << "low_freq: " << low_freq << "\n";
    os << "high_freq: " << high_freq << "\n";
    os << "vtln_low: " << vtln_low << "\n";
    os << "vtln_high: " << vtln_high << "\n";
    os << "debug_mel: " << debug_mel << "\n";
    os << "htk_mode: " << htk_mode << "\n";
    return os.str();
  }
};

std::ostream &operator<<(std::ostream &os, const MelBanksOptions &opts);

class MelBanks {
 public:
  static inline float InverseMelScale(float mel_freq) {
    return 700.0f * (expf(mel_freq / 1127.0f) - 1.0f);
  }

  static inline float MelScale(float freq) {
    return 1127.0f * logf(1.0f + freq / 700.0f);
  }

  static float VtlnWarpFreq(
      float vtln_low_cutoff,
      float vtln_high_cutoff,  // discontinuities in warp func
      float low_freq,
      float high_freq,  // upper+lower frequency cutoffs in
      // the mel computation
      float vtln_warp_factor, float freq);

  static float VtlnWarpMelFreq(float vtln_low_cutoff, float vtln_high_cutoff,
                               float low_freq, float high_freq,
                               float vtln_warp_factor, float mel_freq);

  MelBanks(const MelBanksOptions &opts,
           const FrameExtractionOptions &frame_opts, float vtln_warp_factor,
           torch::Device device);

  int32_t NumBins() const { return static_cast<int32_t>(bins_mat_.size(0)); }

  torch::Tensor Compute(const torch::Tensor &spectrum) const;

  // for debug only
  const torch::Tensor &GetBinsMat() const { return bins_mat_; }

 private:
  // A 2-D matrix of shape [num_bins, num_fft_bins]
  torch::Tensor bins_mat_;

  bool debug_;
  bool htk_mode_;
};

// Compute liftering coefficients (scaling on cepstral coeffs)
// coeffs are numbered slightly differently from HTK: the zeroth
// index is C0, which is not affected.
//
// coeffs is a 1-D float tensor
void ComputeLifterCoeffs(float Q, torch::Tensor *coeffs);

}  // namespace kaldifeat

#endif  // KALDIFEAT_CSRC_MEL_COMPUTATIONS_H_

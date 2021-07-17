#!/usr/bin/env python3

# Copyright      2021  Xiaomi Corporation (authors: Fangjun Kuang)

from pathlib import Path

import torch
from utils import read_ark_txt, read_wave

import kaldifeat

cur_dir = Path(__file__).resolve().parent


def test_fbank_default():
    opts = kaldifeat.FbankOptions()
    opts.frame_opts.dither = 0
    fbank = kaldifeat.Fbank(opts)
    filename = cur_dir / "test_data/test.wav"
    wave = read_wave(filename)

    features = fbank(wave)
    gt = read_ark_txt(cur_dir / "test_data/test.txt")
    assert torch.allclose(features, gt, rtol=1e-1)


def test_fbank_htk():
    opts = kaldifeat.FbankOptions()
    opts.frame_opts.dither = 0
    opts.use_energy = True
    opts.htk_compat = True

    fbank = kaldifeat.Fbank(opts)
    filename = cur_dir / "test_data/test.wav"
    wave = read_wave(filename)

    features = fbank(wave)
    gt = read_ark_txt(cur_dir / "test_data/test-htk.txt")
    assert torch.allclose(features, gt, rtol=1e-1)


def test_fbank_with_energy():
    opts = kaldifeat.FbankOptions()
    opts.frame_opts.dither = 0
    opts.use_energy = True

    fbank = kaldifeat.Fbank(opts)
    filename = cur_dir / "test_data/test.wav"
    wave = read_wave(filename)

    features = fbank(wave)
    gt = read_ark_txt(cur_dir / "test_data/test-with-energy.txt")
    assert torch.allclose(features, gt, rtol=1e-1)


def test_fbank_40_bins():
    opts = kaldifeat.FbankOptions()
    opts.frame_opts.dither = 0
    opts.mel_opts.num_bins = 40

    fbank = kaldifeat.Fbank(opts)
    filename = cur_dir / "test_data/test.wav"
    wave = read_wave(filename)

    features = fbank(wave)
    gt = read_ark_txt(cur_dir / "test_data/test-40.txt")
    assert torch.allclose(features, gt, rtol=1e-1)


def test_fbank_40_bins_no_snip_edges():
    opts = kaldifeat.FbankOptions()
    opts.frame_opts.dither = 0
    opts.mel_opts.num_bins = 40
    opts.frame_opts.snip_edges = False

    fbank = kaldifeat.Fbank(opts)
    filename = cur_dir / "test_data/test.wav"
    wave = read_wave(filename)

    features = fbank(wave)
    gt = read_ark_txt(cur_dir / "test_data/test-40-no-snip-edges.txt")
    assert torch.allclose(features, gt, rtol=1e-1)


def test_fbank_chunk():
    filename = cur_dir / "test_data/test-1hour.wav"
    if filename.is_file() is False:
        print(
            f"Please execute {cur_dir}/test_data/run.sh "
            f"to generate {filename} before running tis test"
        )
        return

    opts = kaldifeat.FbankOptions()
    opts.frame_opts.dither = 0
    opts.mel_opts.num_bins = 40
    opts.frame_opts.snip_edges = False

    fbank = kaldifeat.Fbank(opts)
    wave = read_wave(filename)

    # You can use
    #
    #  $ watch -n 0.2 free -m
    #
    # to view memory consumption
    #
    # 100 frames per chunk
    features = fbank(wave, chunk_size=100 * 10)
    print(features.shape)


def test_fbank_batch():
    wave0 = read_wave(cur_dir / "test_data/test.wav")
    wave1 = read_wave(cur_dir / "test_data/test2.wav")

    opts = kaldifeat.FbankOptions()
    opts.frame_opts.dither = 0
    fbank = kaldifeat.Fbank(opts)

    features = fbank([wave0, wave1], chunk_size=10)

    features0 = fbank(wave0)
    features1 = fbank(wave1)

    assert torch.allclose(features[0], features0)
    assert torch.allclose(features[1], features1)


if __name__ == "__main__":
    test_fbank_default()
    test_fbank_htk()
    test_fbank_with_energy()
    test_fbank_40_bins()
    test_fbank_40_bins_no_snip_edges()
    test_fbank_chunk()
    test_fbank_batch()

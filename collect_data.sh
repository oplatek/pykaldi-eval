#!/bin/bash

echo "Running various experiments for:"
echo "beam (b), lattice-beam (lb), max-active (ma)"
echo "and 50 test utterances"
echo ""

echo "Two experiments:"
echo "    1) First how beam, lattice-beam, max-active influence decoding."
echo "    2) How length of wav influence decoding"

pykaldi_dir=..

# Used args Alex PTICS
# --max-mem=10000000000 --lat-lm-scale=10 --beam=12.0 --lattice-beam=6.0 --max-active=5000', 
# pg CLASS LM weight 0.8 uniform sub sampling td 0.90 tri2b_bmmi
pushd $pykaldi_dir

wav_scp=pykaldi-eval/test_16_wer/input.scp
        # for ma in 2000 6000 12000 ; do
for ma in 5000 2000 8000 ; do
    for lb in  2 3 4.5 6 7 8 ; do 
        for b in 8 11 12 13 16 ; do
            echo; echo "Running for $wav_scp:"
            echo "lb $lb ; b $b ; ma $ma"; echo

            ./run_pykaldi-latgen-faster-decoder.sh \
                --wav_scp $wav_scp --latbeam $lb --beam $b --max_active $ma \
                || exit 1

        done
    done
done

popd

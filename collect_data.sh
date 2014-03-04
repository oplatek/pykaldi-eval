#!/bin/bash

echo "Running various experiments for:"
echo "beam (b), lattice-beam (lb), max-active (ma)"
echo "and 50 test utterances"
echo ""

echo "Two experiments:"
echo "    1) First how beam, lattice-beam, max-active influence decoding."
echo "    2) How length of wav influence decoding"

pykaldi_dir=..

# for b in 13 14 15 16 16.5 ; do
#     for lb in 5.5 6 6.5 7 10 ; do 
#         for ma in 2000 6000 12000 ; do

pushd $pykaldi_dir

wav_scp=pykaldi-eval/test_16_wer/input.scp
for lb in  2 3 4.5 5 6 ; do 
    for b in 13 14 15 16 16.5 ; do
        for ma in 2000 6000 12000 ; do
            echo; echo "Running for $wav_scp:"
            echo "lb $lb ; b $b ; ma $ma"; echo

            # all 50 recodings
            ./run_pykaldi-latgen-faster-decoder.sh --wav_scp $wav_scp --latbeam $lb --beam $b --max_active $ma || exit 1

        done
    done
done

popd

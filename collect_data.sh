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

# source the settings
. path.sh

. utils/parse_options.sh || exit 1

# wav_scp=pykaldi-eval/test_16_wer/input_few.scp
wav_scp=pykaldi-eval/test_16_wer/input.scp

# reference is named based on wav_scp
./build_reference.py $wav_scp $decode_dir
reference=$decode_dir/`basename $wav_scp`.tra

beams="8 9 10 11 12 13 14 15 16"
mkdir -p pykaldi-eval/log pykaldi-eval/kern-log pykaldi-eval/tmp

for ma in 5000 2000 8000 ; do
    for lb in 1 2 3 4 5 6 7 8 10 ; do 
# for ma in 2000 ; do
#     for lb in 1 ; do 
        for b in $beams ; do
            logname=b${b}_lb${lb}_ma${ma}_bs${batch_size}
            pykaldi_latgen_tra=pykaldi-eval/tmp/$$.$logname.tra
            log=pykaldi-eval/log/$$.$logname.log

            echo > $log 
            echo "Running for $wav_scp:" | tee --append $log
            echo >> $log
            echo "lb $lb ; b $b ; ma $ma" | tee --append $log

            kernprof.py -o pykaldi-eval/kern-log/kern_prof_${logname}.log -l -v \
              pykaldi-latgen-faster-decoder.py $wav_scp $batch_size $pykaldi_latgen_tra $WST \
                --verbose=0  --max-mem=10000000000 --lat-lm-scale=15 --config=$MFCC \
                --beam=$beam --lattice-beam=$latbeam --max-active=$max_active \
                $AM $HCLG `cat $SILENCE` $MAT  >> $log &
        done

        wait || exit 1

        for b in $beams ; do
            logname=b${b}_lb${lb}_ma${ma}_bs${batch_size}
            pykaldi_latgen_tra=pykaldi-eval/tmp/$$.$logname.tra
            log=pykaldi-eval/log/$$.$logname.log
            compute-wer --text --mode=present ark:$reference ark,p:$pykaldi_latgen_tra >> $log &
        done
    done
done

popd

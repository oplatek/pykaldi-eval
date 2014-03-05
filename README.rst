Evaluation of GmmLatgenWrapper and its Python wrapper PyGmmLatgenWrapper
========================================================================

See the (intermediate) results at
http://nbviewer.ipython.org/github/oplatek/pykaldi-eval/blob/master/Pykaldi-evaluation.ipynb

We evaluate the dynamic properties of decoder e.g. 
Real Time Factor (RTF), Latency (LAT), Word Error Rate (WER)
and Sentence Error Rate (SER) based on decoding parameters.

We choose to investigate the influence of 
 * beam
 * lattice-beam
 * max-active states
 * wave length
On metrics RTF, LAT, WER and SER mentioned above.

We did not experiment with the Lexicon size and Language Model (LM)
complexity, which certainly influence all the metrics,
but especially the LM complexity is hard to describe and visualise.

Note that decoding is language independent since the LM complexity
and lexicon size is fixed.
We used LM TODO with lexicon size 17000 TODO?


Technical details
~~~~~~~~~~~~~~~~~
The evaluation is perform using the ``pykaldi-latgen-faster-decoder.py``
and its launcher ``run_pykaldi-latgen-faster-decoder.sh`` 
from ``kaldi/src/pykaldi/pykaldi/binutils`` directory.

TODO More describe test sets (So far I use the default from vystadial server)

We suppose the code is run from subdirectory of ``binutils``, 
so copy this repository to ``kaldi/src/pykaldi/pykaldi/binutils``.

.. code-block:: bash

    ./collect_data.sh | tee text_command.log
    ./parse_collect.py text_command.log pickled_tuples.txt

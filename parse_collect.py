#!/usr/bin/env python
# encoding: utf-8
from collections import namedtuple
import sys
import pickle

print """Two experiments:
    1) First how beam, lattice-beam, max-active influence decoding.
    2) How length of wav influence decoding
"""

lentot50 = 82.51
lenavg50 = lentot50 / 50.0


SysRecord = namedtuple('SysRecord', ['wav_scp', 'beam', 'lattice_beam', 'max_active', 'wavlen',
                                     'decodelen', 'forwardlen', 'backwardlen', 'refer_words', 'ins', 'dl', 'sub', 'ser'])
UserRecord = namedtuple(
    'UserRecord', ['wav_name', 'wav_len', 'beam', 'lattice_beam', 'max_active', 'forwardlen', 'backwardlen'])


def parse(log_file_path):
    rec, urec, urecords, records = None, None, [], []
    with open(log_file_path, 'r') as r:
        for line in r:
            if line.startswith('Running for '):
                if rec is not None:
                    raise Exception('Bad logic: not finished parsing previous record')
                wav_scp = line[12:-1]  # After Running for and without :
                rec = SysRecord(wav_scp, None, None, None, None, None,
                                None, None, None, None, None, None, None)
            if line.startswith('lb '):
                lb, b, ma = line.split(';')
                lb, b, ma = float(lb.split()[1]), float(b.split()[1]), float(ma.split()[1])
                rec = rec._replace(lattice_beam=lb, beam=b, max_active=ma)
            if line.startswith('Total time: '):
                decodelen = float(line.split()[2])
                rec = rec._replace(decodelen=decodelen)
            if line.startswith('    53'):
                forward_sys_time = float(line.split()[2])
                rec = rec._replace(forwardlen=forward_sys_time)
            if line.startswith('    56'):
                forward_sys_time = float(line.split()[2])
                forward_sys_time += rec.forwardlen  # forward decoding is 2 times in decode method
                rec = rec._replace(forwardlen=forward_sys_time)
            if line.startswith('    58'):
                prune_final_sys_time = float(line.split()[2])
                rec = rec._replace(backwardlen=prune_final_sys_time)
            if line.startswith('    59'):
                get_lattice_sys_time = float(line.split()[2])
                # backward decoding = prune_final + get_lattice
                backwardlen = rec.backwardlen + get_lattice_sys_time
                rec = rec._replace(backwardlen=backwardlen)
            if line.startswith('%WER'):
                start, ins, dl, sub = line.split(',')
                refer_words, ins, dl, sub = int(
                    start.split()[-1]), int(ins.split()[0]), int(dl.split()[0]), int(sub.split()[0])
                rec = rec._replace(refer_words=refer_words, ins=ins, dl=dl, sub=sub)
            if line.startswith('%SER'):
                ser = float(line.split()[1])
                rec = rec._replace(ser=ser, wavlen=lenavg50)
                records.append(rec)
                rec = None
            # Parsing urec
            if 'has' in line:
                wav_name, has, wav_len, sec = line.split()
                assert has == 'has' and sec == 'sec', 'Parsing bad line'
                if urec is not None:
                    raise Exception('Bad logic: not finished parsing previous user time record\n%s\n' % line)
                urec = UserRecord(wav_name=wav_name, wav_len=float(wav_len), beam=rec.beam,
                                  lattice_beam=rec.lattice_beam, max_active=rec.max_active, forwardlen=None, backwardlen=None)
            if line.startswith('forward decode:'):
                forwardlen = float(line.split()[2])
                urec = urec._replace(forwardlen=forwardlen)
            if line.startswith('backward decode:'):
                backwardlen = float(line.split()[2])
                urec = urec._replace(backwardlen=backwardlen)
                urecords.append(urec)
                urec = None
    return records, urecords

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise Exception('Expecting one argument: log_file_path records_pickle_file')
    log_file_path, pickle_file = sys.argv[1], sys.argv[2]
    srecords, urecords = parse(log_file_path)
    with open(pickle_file, 'w') as p:
        pickle.dump(srecords, p)
        pickle.dump(urecords, p)

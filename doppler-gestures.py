#!/usr/bin/env python

from multiprocessing import Process, Queue, Event
import pyaudio
import wave
import time
import sys
import struct
import itertools
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def block2short(block):
    """
    Take a binary block produced by pyaudio and turn it into an array of
    shorts. Assumes the pyaudio.paInt16 datatype is being used.
    """
    # Each entry is 2 bytes long and block appears as a binary string (array 
    # of 1 byte characters). So the length of our final binary string is the
    # length of the block divided by 2.
    sample_len = len(block)/2
    fmt = "%dh" % (sample_len) # create the format string for unpacking
    return struct.unpack(fmt, block)



def tonePlayer(freq, sync):
    p = pyaudio.PyAudio()


    RATE  = 44100
    CHUNK = 1024*4
    A = (2**16 - 2)/2

    stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=RATE,
                    frames_per_buffer=CHUNK,
                    output=True,
                    input=False)

    stream.start_stream()
    sync.set()
    h = 0
    while 1:
        L = [A*np.sin(2*np.pi*float(i)*float(freq)/RATE) for i in range(h*CHUNK, h*CHUNK + CHUNK)]
        R = [A*np.sin(2*np.pi*float(i)*float(freq)/RATE) for i in range(h*CHUNK, h*CHUNK + CHUNK)]
        data = itertools.chain(*zip(L,R))
        chunk = b''.join(struct.pack('<h', i) for i in data)
        stream.write(chunk)
        h += 1

#            data = wf.readframes(CHUNK)
#        wf.rewind()
    print("done")

    stream.stop_stream()
    stream.close()

#    wf.close()
    p.terminate()
    return True

def recorder(q,freq, window_size, sync):
    p = pyaudio.PyAudio()

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK= 1024*2
    freqs = np.fft.rfftfreq(CHUNK, d=1.0/RATE)
    display_freqs = (freq- window_size/2,freq + window_size/2)
    freq_range = np.where((freqs > display_freqs[0]) & (freqs<display_freqs[1]))
    frange = (freq_range[0][0],freq_range[0][-1])
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    fir = signal.firwin(64, [freq - window_size/2, freq + window_size/2], pass_zero=False,nyq=44100/2)
    stream.start_stream()
    
    frames = []
    plt.ion()
    plt.show()
    plt.draw()

    sync.wait()
    
    while True:
        data = stream.read(CHUNK)
        frame = block2short(data)
        frame = signal.convolve(frame, fir, 'same')
        frame_fft = abs(np.fft.rfft(frame))
        freq_20khz_window = freqs[frange[0]:frange[1]]
        fft_20khz_window = frame_fft[frange[0]:frange[1]]
        fft_maxarg = np.argmax(fft_20khz_window) 
        
        if fft_20khz_window[fft_maxarg] > 50000:
            thresh= fft_20khz_window[fft_maxarg]*.12
        else:
            thresh = 55000
        plt.clf()
        plt.plot(freqs[frange[0]:frange[1]], [thresh for i in range(len(fft_20khz_window))])
        plt.plot(freqs[frange[0]:frange[1]], fft_20khz_window)
        bw_freqs = freq_20khz_window[np.where(fft_20khz_window>thresh)[0]]
        if bw_freqs.size > 2:
            bw = bw_freqs[-1] - bw_freqs[0]
            bw_lsb =  bw_freqs[0] - freq_20khz_window[fft_maxarg]
            bw_usb =  bw_freqs[-1] - freq_20khz_window[fft_maxarg]

            h = "".join([" " for i in range(int(80*(bw_usb + bw_lsb+ 200)/400))])
            print (h+"|")
        plt.ylim([0,CHUNK**2 / 2])
        
        plt.draw()


    print "DONE"
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    return frames

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Plays a wave file.\n\nUsage: %s freq freq_window" % sys.argv[0])
        sys.exit(-1)
    for i in range(10):
        q = Queue()
        s = Event()
        tonePlayer_p = Process(target=tonePlayer, args=(int(sys.argv[1]),s,))
        tonePlayer_p.daemon = True

        recorder_p = Process(target=recorder, args=(q,int(sys.argv[1]),int(sys.argv[2]),s,))
        recorder_p.daemon = True

        recorder_p.start()
        tonePlayer_p.start()


        tonePlayer_p.join()
        recorder_p.join()
        time.sleep(1)

#print rec



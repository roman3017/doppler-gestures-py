# Python Doppler Gestures

# Usage

```
$ ./doppler-gestures.py <tone> <window>
```

__tone__ is in Hz
__window__ is in Hz

Working example:

```
$ export PYTHONPATH=.
$ ./doppler-gestures.py --tone 20000 --window 500 --channels 2
```

Your speakers should be on rather high (no headphones) and your input/mic should also be on and at a high input gain.

# Resources

- [Daniel Rapp's Doppler Javascript](https://danielrapp.github.io/doppler/)
- [Gupta, et. al's SoundWave Paper from Microsoft Research](http://research.microsoft.com/en-us/um/redmond/groups/cue/publications/guptasoundwavechi2012.pdf)

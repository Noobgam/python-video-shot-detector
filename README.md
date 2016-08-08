
# Table of Contents

  * [What is this](#what-is-this)
    * [How to install](#how-to-install)
    * [How to start](#how-to-start)
  * [Source Video](#source-video)
  * [Point to Point Streaming](#point-to-point-streaming)
    * [SDP-file and RTP-stream](#sdp-file-and-rtp-stream)
      * [File Streaming](#file-streaming)
      * [Virtual Device](#virtual-device)
      * [Camera Streaming](#camera-streaming)
      * [Desktop Capturing](#desktop-capturing)
    * [MPEG-TS Streaming](#mpeg-ts-streaming)
      * [MPEG-TS via UDP](#mpeg-ts-via-udp)
      * [MPEG-TS via TCP](#mpeg-ts-via-tcp)
  * [Streaming with a Server](#streaming-with-a-server)
  

# What is this

This is a detector of video shots based of [PyAV]
(http://mikeboers.github.io/PyAV/).

**It is strongly under construction.**

Nowadays, the main purpose of it is to visualize different methods
of shot detection and near duplicate video retrieval.

## How to install

It uses [conda](http://conda.pydata.org/docs/intro.html) as package 
manager. So to install it should run commands:

1. Create new environment and install requirements from conda:
    ```(bash)
         conda create --name shot-detector-3.4 \
            --file ./requirements/py34/requirements-conda-explicit.txt
    ```
2. Activate your environment
    ```(bash)
    source activate shot-detector-3.4
    ```
3. Install requirements from pip *(I wiil remove this step soon)*:
    ```(bash)
    pip install -r ./requirements/py34/requirements-pip.txt
    ```
The same for Python 2.7:

1. Create new environment and install requirements from conda:
    ```(bash)
         conda create --name shot-detector-2.7 \
            --file ./requirements/py27/requirements-conda-explicit.txt
    ```
2. Activate your environment
    ```(bash)
    source activate shot-detector-2.7
    ```
3. Install requirements from pip:
    ```(bash)
    pip install -r ./requirements/py27/requirements-pip.txt
    ```

See [Managing environments]
(http://conda.pydata.org/docs/using/envs.html) for more details.

## How to start

    python -m shot_detector.main_detector 

    python -m shot_detector.main_detector <URI of video file or stream>

# Source Video

You can use any video-file or video-device 
as an input for the Shot Detector.
But in some cases it is required to use on-the-fly video stream.

You can get video-stream from third-party source or generate 
it yourself. There are several ways to generate your own input video 
stream:

* from a file;
* from your camera;
* from your desktop;
* from a virtual device.

More over you can implement it with different schemes of streaming:

* point to point streaming;
* streaming with server (`ffserver`).


# Point to Point Streaming

This is the simplest way to reproduce on-the-fly video stream.
In this case you generate stream only for one reader.
If you use your stream for the Shot Detector,
you cannot check it without stopping the Shot Detector.
But in this stream embodiment you wont deal with latency.

## SDP-file and RTP-stream 

In this case we use [RTP Streaming Protocol]
(https://en.wikipedia.org/wiki/Real-time_Transport_Protocol). 
The main limitation of it is that only one stream supported 
in the RTP muxer. So you can stream only video without audio
or audio without video.

### File Streaming

1. Create a SDP-file and RTP-stream  with `ffmpeg`. 
    For a file stream it looks like this:
   
        ffmpeg -re -i input-file.mp4 -an -f rtp rtp://127.0.0.1:1236 > file-stream.sdp

    Where:
    
    * `-re ` — is a flag that makes `ffmpeg` read input at native frame 
    rate. In this case it is used to simulate a stream from a device.
    Without this flag, your stream will be handled as a simple file.
    It is required only if you work with static file but not real stream.
    * `-i input-file.mp4` — is a name of input file.
    * `-an` — is a flag that makes ffmpeg ignore audio streams.
    The reason of this flag is that RTP doesn't support more than one 
    stream. Moreover, if your file contains several video streams,
    your should choose one and remove odd video streams.
    * `-f rtp` — is an output format — [RTP]
    (https://en.wikipedia.org/wiki/Real-time_Transport_Protocol).
    * `rtp://127.0.0.1:1234` — an address for receiving stream of 
    virtual device.
    * `./file-stream.sdp` — is a is a [stream session description file]
    (https://en.wikipedia.org/wiki/Session_Description_Protocol). 
    
2. Check the `./file-stream.sdp`. In this case it contains following text:
    
        SDP:
        v=0
        o=- 0 0 IN IP4 127.0.0.1
        s=No Name
        c=IN IP4 127.0.0.1
        t=0 0
        a=tool:libavformat 55.33.1000
        m=video 1234 RTP/AVP 96
        b=AS:2000
        a=rtpmap:96 MP4V-ES/90000
        a=fmtp:96 profile-level-id=1

3. Check the stream. Run `ffplay` with `./file-stream.sdp` as an arguments.
        
        ffplay ./file-stream.sdp

    You get a window with video from your file-stream.
    
    * More over you can use any another player that supports RTP.
        For example:
    
            mplayer ./file-stream.sdp
    
4. Stop `ffplay` and then use `./file-stream.sdp` file name 
    as input URI for the Shot Detector
    
**Note:** RTP uses UDP, so the receiver can start up any time, but
you can get packet loss.

### Virtual Device

1. Create a SDP-file and RTP-stream  with `ffmpeg`. 
    For a virtual device it looks like this:
    
        ffmpeg -f lavfi -i mandelbrot -f rtp rtp://127.0.0.1:1234 > virtual-device.sdp 

    Where:
    
    * `-f lavfi` — is format of libavfilter input [virtual device]
        (https://www.ffmpeg.org/ffmpeg-devices.html#lavfi).
        This input device reads data from 
        the open output pads of a libavfilter filtergraph.
    * `-i mandelbrot` — is a filter that draws the [Mandelbrot set]
    (https://en.wikipedia.org/wiki/Mandelbrot_set).
    Check [Fancy Filtering Examples]
    (https://trac.ffmpeg.org/wiki/FancyFilteringExamples#Video)
    in FFmpeg documentaion for another filter types.
    * `-f rtp` — is an output format — [RTP]
    (https://en.wikipedia.org/wiki/Real-time_Transport_Protocol).
    * `rtp://127.0.0.1:1234` — an address for receiving stream of 
    virtual device.
    * `./virtual-device.sdp` — is a is a [stream session description file]
    (https://en.wikipedia.org/wiki/Session_Description_Protocol). 
    
2. Use `virtual-device.sdp` as discussed above.

### Camera Streaming

Create a SDP-file and RTP-stream  with `ffmpeg`. 
For a camera it looks like this:

    ffmpeg -f v4l2 -i /dev/video0 -f rtp rtp://127.0.0.1:1234 > camera.sdp

Where:

* `-f v4l2` — is an input device-format for a camera. 
The full name of it is — [video4linux2]
(https://www.ffmpeg.org/ffmpeg-devices.html#video4linux2_002c-v4l2)
*It works only for linux.* For another systems, please, 
check this page: [FFmpeg Streaming Guide]
(https://trac.ffmpeg.org/wiki/StreamingGuide "Streaming Guide")
* `-i /dev/video0` — is a path to device.
* `-f rtp` — is an output format — [RTP]
(https://en.wikipedia.org/wiki/Real-time_Transport_Protocol).
* `rtp://127.0.0.1:1234` — an address for receiving camera's stream.
* `./camera.sdp` — is a file with a description of your 
[stream session](https://en.wikipedia.org/wiki/Session_Description_Protocol). 

After that use `camera.sdp` as discussed above.

### Desktop Capturing

For a Linux display ffmpeg-command looks like this:

    ffmpeg -f x11grab -video_size wxga  -i :0.0  -f rtp rtp://127.0.0.1:1234 > desktop.sdp

Where:

* `-f x11grab` — is an input format for a [X11-display]
(https://www.ffmpeg.org/ffmpeg-devices.html#x11grab). 
* `-video_size wxga` — size of your display. In this case we use the 
full size of desktop. Check [FFmpeg Capture/Desktop]
(https://trac.ffmpeg.org/wiki/Capture/Desktop) page for other options
* `-i :0.0` — is a desktop name.
* `-f rtp` — is an output format 
* `rtp://127.0.0.1:1234` — an address for receiving camera's stream.
* `./desktop.sdp` — is a stream session description file.

After that use `desktop.sdp` as discussed above.

## MPEG-TS Streaming

With [MPEG-TS](https://en.wikipedia.org/wiki/MPEG_transport_stream) you 
can generate both and audio and video.

### MPEG-TS via UDP

In this case we use [UDP]
(https://en.wikipedia.org/wiki/User_Datagram_Protocol).
So, you still can get packet loss.
They are likely to reveal if you stream via Internet.

Here is example for a camera.
For another devices they are the same.

1. Start `ffmpeg` to generate **MPEG-TS** stream via udp.
    
        ffmpeg -f v4l2 -i /dev/video0 -f mpegts udp://127.0.0.1:1234

    Where:
    
    * `-f v4l2` — is an input device-format for a camera. 
    It works only for linux. For another systems, please, 
    check this page: [FFmpeg Streaming Guide]
    (https://trac.ffmpeg.org/wiki/StreamingGuide "Streaming Guide")
    * `-i /dev/video0` — is a path to device.
    * `-f mpegts` — is an output format — MPEG transport stream.
    * `udp://127.0.0.1:1234` — an address for receiving camera's stream.

2. Check it with `ffplay`:

        ffplay  -fflags nobuffer  udp://127.0.0.1:1234
    
    Where:
    
    * `-fflags nobuffer` — is a flag that makes ffplay don't cache 
    input stream. We set it to reduce latency.
    
3. Use `udp://127.0.0.1:1234` as input video URI for the Shot Detector.   
More over, you can start `ffmpeg` and the Shot Detector in any order.

**Note:** The time in the Shot Detector is a time of a video stream.

Also you can use both video and audio.

    ffmpeg -f v4l2 -i /dev/video0 -f alsa -i hw:0 -f mpegts udp://127.0.0.1:1234

Where:

* `-f alsa` — is an input device-format for a microphone. 
* `-i hw:0` — is a name of a microphone device. See [Capture/ALSA]
(https://trac.ffmpeg.org/wiki/Capture/ALSA) for more details.

### MPEG-TS via TCP

Another option is to use TCP connections for MPEG-TS streaming.
In this case you don't get packet loss.
But you should guarantee that a reader will be started before
a writer. So, reader become a server and writer become a client.

For example:

1. Start `ffplay` as a server

        ffplay -fflags nobuffer  tcp://127.0.0.1:1234?listen

    Where:
    
    * `-fflags nobuffer` — is a flag that makes ffplay don't cache 
    input stream. We set it to reduce latency.
    * `tcp://127.0.0.1:1234?listen` — is a host for sending 
    camera's stream whith `listen` option.
    A writer should send stream to `tcp://127.0.0.1:1234`.
     
     
2. Start `ffmpeg` as a client

        ffmpeg -f v4l2 -i /dev/video0  -f mpegts tcp://127.0.0.1:1234

    Where:
    
    * `-f v4l2` — is an input device-format for a camera. 
    It works only for linux. For another systems, please, 
    check this page: [FFmpeg Streaming Guide]
    (https://trac.ffmpeg.org/wiki/StreamingGuide "Streaming Guide")
    * `-i /dev/video0` — is a path to device.
    * `-f mpegts` — is an output format — MPEG transport stream.
    * `tcp://127.0.0.1:1234` — an address for sending camera's stream.


So, you can pass `tcp://127.0.0.1:1234?listen` as an input video URI 
for the Shot Detector. But you should start it before `ffmpeg`,
Do not forget to stop `ffplay`, before it.

# Streaming with a Server

In this scheme you send the video-stream to a server.
And then any client can get your stream from it.
The simplest way to achive this is to use `ffserver`.

1. Start ffserver with certain configuration file.

        sudo /usr/bin/ffserver -f ./etc/input/ffserver.conf 

    Check [FFServer Configuration](etc/input/ffserver.conf).

2. Send input stream to server.

    For example, for linux-camera you should run:

        /usr/bin/ffmpeg -f v4l2 -i /dev/video0 -f alsa -i hw:0 -tune zerolatency http://localhost:8090/feed1.ffm

    Where:
    
    * `-f v4l2` — is an input device-format for a camera. 
    It works only for linux. For another systems, please, 
    check this page: [FFmpeg Streaming Guide]
    (https://trac.ffmpeg.org/wiki/StreamingGuide "Streaming Guide")
    * `-i /dev/video0` — is a path to device.
    * `-f alsa` — is an input device-format for a microphone. 
    * `-i hw:0` — is a name of a microphone device. See [Capture/ALSA]
    (https://trac.ffmpeg.org/wiki/Capture/ALSA) for more details.
    * `-tune zerolatency` — is a flag that makes `ffmpeg` to change 
    settings to minimize latency. This is not a flag of ffmpeg,
    this is H.264 option. See [Encode/H.264: Choose a preset]
    (https://trac.ffmpeg.org/wiki/Encode/H.264#a2.Chooseapreset)
    for more details.
    * `http://localhost:8090/feed1.ffm` — an address for sending 
    camera's stream.
    
    For desktop it is the same:
    
        /usr/bin/ffmpeg -f x11grab -i :0.0 -f alsa -i hw:0 -tune zerolatency http://localhost:8090/feed1.ffm


3. Check it with `ffplay`:

        ffplay -fflags nobuffer http://localhost:8090/live.flv

    Where:
    
    * `-fflags nobuffer` — is a flag that makes ffplay don't cache 
    input stream. We set it to reduce latency.
    * `http://localhost:8090/live.flv` — is an address to get 
    a video stream. It is specified in `etc/input/ffserver.conf`.
    
    
4.  Pass `http://localhost:8090/live.flv` as an input video URI 
    for the Shot Detector. In this case you may not stop `ffplay`.
    
As for me it is the best way to simulate streaming 
for the Shot Detector.


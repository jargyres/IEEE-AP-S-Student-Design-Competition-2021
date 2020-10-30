import sys
import os
import threading
from multiprocessing.pool import ThreadPool
from bladerf import _bladerf
import matplotlib.pyplot as plt


CHANNEL_COUNT = 2

# =============================================================================
# Search for a bladeRF device attached to the host system
# Returns a bladeRF device handle.
# =============================================================================
def probe_bladerf():
    device = None
    print( "Searching for bladeRF devices..." )
    try:
        devinfos = _bladerf.get_device_list()
        if( len(devinfos) == 1 ):
            device = "{backend}:device={usb_bus}:{usb_addr}".format(**devinfos[0]._asdict())
            print( "Found bladeRF device: " + str(device) )
        if( len(devinfos) > 1 ):
            print( "Unsupported feature: more than one bladeRFs detected." )
            print( "\n".join([str(devinfo) for devinfo in devinfos]) )
            shutdown( error = -1, board = None )
    except _bladerf.BladeRFError:
        print( "No bladeRF devices found." )
        pass

    return device

# =============================================================================
# Close the device and exit
# =============================================================================
def shutdown( error = 0, board = None ):
    print( "Shutting down with error code: " + str(error) )
    if( board != None ):
        board.close()
    sys.exit(error)




def receive(device, channel : int, freq : int, rate : int, gain : int,
            tx_start = None, rx_done = None,
            rxfile : str = '', num_samples : int = 2048):

    status = 0

    ch1 = device.Channel(0)
    ch2 = device.Channel(1)

    ch1.frequency = freq
    ch2.frequency = freq
    ch1.sample_rate = rate
    ch2.sample_rate = rate
    ch1.gain = gain
    ch2.gain = gain


    if( device == None ):
        print( "RX: Invalid device handle." )
        return -1

    if( channel == None ):
        print( "RX: Invalid channel." )
        return -1

    # Configure BladeRF
    #ch             = device.Channel(channel)
    #ch.frequency   = freq
    #ch.sample_rate = rate
    #ch.gain        = gain

    

    # Setup synchronous stream
    device.sync_config(layout         = _bladerf.ChannelLayout.RX_X2,
                       fmt            = _bladerf.Format.SC16_Q11,
                       num_buffers    = 16,
                       buffer_size    = 8192,
                       num_transfers  = 8,
                       stream_timeout = 3500)

    # Enable module
    print( "RX: Start" )
    ch1.enable = True
    ch2.enable = True
    # Create receive buffer
    bytes_per_sample = 4
    buf = bytearray(2048*bytes_per_sample)
    num_samples_read = 0

    # Tell TX thread to begin
    if( tx_start != None ):
        tx_start.set()
    # Save the samples
    while True:
        if num_samples > 0 and num_samples_read == num_samples:
            break
        elif num_samples > 0:
            num = min(len(buf)//bytes_per_sample,num_samples-num_samples_read)
        else:
            num = len(buf)//bytes_per_sample
        num = int(num)
            # Read into buffer
        device.sync_rx(buf, num)
        num_samples_read += num


    # Disable module
    print("RX: Stop")
    ch1.enable = False
    ch2.enable = False

    if(rx_done != None ):
        rx_done.set()

    #for i in range(10):
    #    print("buf1[{}]= {}".format(i, buf[i]), end=' ')


    return buf

def deinterleave(buff):

    buff1 = buff[::2]
    buff2 = buff[1::2]

    


uut = probe_bladerf()

if( uut == None ):
    print( "No bladeRFs detected. Exiting." )
    shutdown(error=-1, board=None)

b = _bladerf.BladeRF(uut)

rx_pool = ThreadPool(processes=1)

rx_ch = 0
rx_freq = 2.3e9
rx_rate = 20e6
rx_gain = 0
rx_ns = 10e6
rx_file = ''

buff1 = rx_pool.apply_async(receive,
                            (),
                            { 'device'        : b,
                              'channel'       : rx_ch,
                              'freq'          : rx_freq,
                              'rate'          : rx_rate,
                              'gain'          : rx_gain,
                              'tx_start'      : None,
                              'rx_done'       : None,
                              'rxfile'        : rx_file,
                              'num_samples'   : rx_ns
                            }).get()

rx_ch = 1

#buff2 = rx_pool.apply_async(receive,
#                            (),
#                            { 'device'        : b,
#                              'channel'       : rx_ch,
#                              'freq'          : rx_freq,
#                              'rate'          : rx_rate,
#                              'gain'          : rx_gain,
#                              'tx_start'      : None,
#                              'rx_done'       : None,
#                              'rxfile'        : rx_file,
#                              'num_samples'   : rx_ns
#                            }).get()
#print(status)

deinterleaved = [buff1[idx::CHANNEL_COUNT] for idx in range(CHANNEL_COUNT)]


plt.psd(deinterleaved[0], Fs=rx_rate, Fc=rx_freq, zorder=1, label='Port 1')

plt.psd(deinterleaved[1], Fs=rx_rate, Fc=rx_freq, zorder=1, label = 'Port 2')


plt.psd(buff1, Fs=rx_rate, Fc=rx_freq, zorder=1, label = 'Both Interleaved')

plt.legend()

plt.show()





print("DONE")




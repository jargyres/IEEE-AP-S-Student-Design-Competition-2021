/*
 * This file is part of the bladeRF project:
 *   http://www.github.com/nuand/bladeRF
 *
 * Copyright (C) 2014 Nuand LLC
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

//compile with
//gcc sync_rx_meta.c example_common.c -Iinclude -o sync_rx_meta -lbladeRF

#include <inttypes.h>
#include <libbladeRF.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
// #include <Python.h>

#include "example_common.h"


//Store these two in global variables so that we can use them in functions later on
struct bladerf *dev1 = NULL;
struct bladerf *dev2 = NULL;

struct args_struct {
    struct bladerf* device;
    bool isDevice1;
};

typedef struct args_struct args_struct;

//Use these structs to pass the argument to the threads we run for RX on dev1 and dev2
args_struct *dev1_args;
args_struct *dev2_args;

//Store the rx data in these same two arrays over and over again
int16_t *dev1_samples;
int16_t *dev2_samples;
int16_t *all_samples;

//Here we have the threads that the RX will run on for both devices
pthread_t dev1_thread;
pthread_t dev2_thread;

// Store the trigger here as a global so we can fire later from our functions
struct bladerf_trigger trig_master;

const unsigned int samples_len = 1024;

/*
    Our array will actually take up samples_len * 4 * sizeof(int16_t) bytes
    This is because for each sample, we need 

    Device 1 Sample i           Device 2 Sample i
    I(2 bytes) , Q(2 bytes)     I(2 bytes), Q(2 bytes)

    So 4 separate numbers needed for each sample
*/
const unsigned int per_device_array_len = samples_len * 4;

pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

void handle_status(int status);

int16_t *init(struct bladerf*, int16_t);

static int init_sync(struct bladerf*, unsigned int);

void EnableTriggers(struct bladerf_trigger*, struct bladerf*, struct bladerf*);

void openDevices();

void setupRX();

void * sync_rx_example(void*);

int16_t * receive_rx();

/*
Quick helper function to handle the many status flags that are thrown around bladerf
*/
void handle_status(int status)
{

}

static void sc16q11_sample_fixup(int16_t *buf, size_t n)
{
    size_t i;

    for (i = 0; i < n; i++) {
        /* I - Mask off the marker and sign extend */
        //        *buf &= (*buf) & 0x0fff;
        //        if (*buf & 0x800) {
        //            *buf |= 0xf000;
        //        }

        *buf = LE16_TO_HOST(*buf);
        buf++;

        /* Q - Mask off the marker and sign extend */
        //        *buf = HOST_TO_LE16(*buf) & 0x0fff;
        //        if (*buf & 0x800) {
        //            *buf |= 0xf000;
        //        }

        *buf = LE16_TO_HOST(*buf);
        buf++;
    }
}


int16_t *init(struct bladerf *dev, int16_t num_samples)
{
    int status = -1;

    /* "User" buffer that we read samples into and do work on, and its
     * associated size, in units of samples. Recall that for the
     * SC16Q11 format (native to the ADCs), one sample = two int16_t values.
     *
     * When using the bladerf_sync_* functions, the buffer size isn't
     * restricted to multiples of any particular size.
     *
     * The value for `num_samples` has no major restrictions here, while the
     * `buffer_size` below must be a multiple of 1024.
     */
    int16_t *samples;

    /* These items configure the underlying asynch stream used by the the sync
     * interface. The "buffer" here refers to those used internally by worker
     * threads, not the `samples` buffer above. */
    const unsigned int num_buffers   = 16;
    const unsigned int buffer_size   = 8192;
    const unsigned int num_transfers = 8;
    const unsigned int timeout_ms    = 1000;

    samples = malloc(2 * num_samples * 2 * sizeof(int16_t));
    if (samples == NULL) {
        perror("malloc");
        goto error;
    }

    /** [sync_config] */

    /* Configure the device's RX for use with the sync interface.
     * SC16 Q11 samples *with* metadata are used. */
    status = bladerf_sync_config(dev, BLADERF_RX_X2,
                                 BLADERF_FORMAT_SC16_Q11, num_buffers,
                                 buffer_size, num_transfers, timeout_ms);
    if (status != 0) {
        fprintf(stderr, "Failed to configure RX sync interface: %s\n",
                bladerf_strerror(status));

        goto error;
    }

    /** [sync_config] */

    /* We must always enable the RX front end *after* calling
     * bladerf_sync_config(), and *before* attempting to RX samples via
     * bladerf_sync_rx(). */
    status = bladerf_enable_module(dev, BLADERF_RX, true);
    if (status != 0) {
        fprintf(stderr, "Failed to enable RX: %s\n", bladerf_strerror(status));

        goto error;
    }

    status = 0;

error:
    if (status != 0) {
        free(samples);
        samples = NULL;
    }

    return samples;
}


/* Initialize sync interface for metadata and allocate our "working"
 * buffer that we'd use to process our RX'd samples.
 *
 * Return sample buffer on success, or NULL on failure.
 */


static int init_sync(struct bladerf *dev, unsigned int timeout_ms)
{
    int status;

    /* These items configure the underlying asynch stream used by the sync
     * interface. The "buffer" here refers to those used internally by worker
     * threads, not the user's sample buffers.
     *
     * It is important to remember that TX buffers will not be submitted to
     * the hardware until `buffer_size` samples are provided via the
     * bladerf_sync_tx call.  Similarly, samples will not be available to
     * RX via bladerf_sync_rx() until a block of `buffer_size` samples has been
     * received.
     */
    const unsigned int num_buffers   = 32;
    const unsigned int buffer_size   = 16384; /* Must be a multiple of 1024 */
    const unsigned int num_transfers = 16;
    // const unsigned int timeout_ms    = 35000;

    /* Configure both the device's x1 RX and TX channels for use with the
     * synchronous
     * interface. SC16 Q11 samples *without* metadata are used. */

    status = bladerf_sync_config(dev, BLADERF_RX_X2, BLADERF_FORMAT_SC16_Q11,
                                 num_buffers, buffer_size, num_transfers,
                                 timeout_ms);
    if (status != 0) {
        fprintf(stderr, "Failed to configure RX sync interface: %s\n",
                bladerf_strerror(status));
        return status;
    }

    status = bladerf_enable_module(dev, BLADERF_RX, true);
    if (status != 0) {
        fprintf(stderr, "Failed to enable RX: %s\n", bladerf_strerror(status));

        return status;
    }


    return status;
}


/**
 * @brief Enable Triggers
 * 
 * To enable the triggers, we have to tie down the tx_0 port on one of the devices to be the master.
 * We enable the rest of the rx ports on both of the devices to be slaves to the master signal
 * 
 * On our devices, there is a jumper cable connecting the J51-1 port on both devices, from which the signal will be sent through
 * 
 * 
 * @param first the master device 
 * @param second the second device
 * @return int any errors
 */
void EnableTriggers(struct bladerf_trigger* trig_master, struct bladerf* first, struct bladerf* second)
{
    int status = 0;
	//this channel will be the master
    bladerf_channel channel_tx_0 = BLADERF_CHANNEL_TX(0);
   
   	//these two channels will be configured for both devices to be slaves
	bladerf_channel channel_rx_0 = BLADERF_CHANNEL_RX(0);

	bladerf_channel channel_rx_1 = BLADERF_CHANNEL_RX(1);

    bladerf_trigger_signal trigger_signal = BLADERF_TRIGGER_J51_1;

    struct bladerf_trigger trig_first_rx_0, trig_first_rx_1, trig_second_rx_0, trig_second_rx_1;


	/*
        Initialize the master signal with 

        struct bladerf* first --> the first device
        bladerf_channel channel_tx_0 --> The TX0 port on the first device
        bladerf_trigger_signal trigger_signal --> The J51-1 signal, which is connected to both devices
        struct bladerf_trigger *trig_master --> The trigger that we set and will control to fire

    */
    status = bladerf_trigger_init(first, channel_tx_0, trigger_signal, trig_master);


    //If we get a zero status code, then we successfully made the trigger
    // Now we set the "role" of the trigger to be BLADERF_TRIGGER_ROLE_MASTER
	if(!status)
    {
        trig_master->role = BLADERF_TRIGGER_ROLE_MASTER;
    }
    else{handle_status(status);}

    
	/*
        Initialize the slave signal on the first device with 

        struct bladerf* first --> the first device
        bladerf_channel channel_rx_0 --> The RX0 port on the first device
        bladerf_trigger_signal trigger_signal --> The J51-1 signal, which is connected to both devices
        struct bladerf_trigger *trig_first_rx_0 --> The trigger for the first rx port on the first device
    */
	status = bladerf_trigger_init(first, channel_rx_0, trigger_signal, &trig_first_rx_0);\

    //If a zero status code, then we set the "role" of the RX0, first device trigger to be BLADERF_TRIGGER_ROLE_SLAVE
	if(!status)
    {
        trig_first_rx_0.role = BLADERF_TRIGGER_ROLE_SLAVE;
    }
    else{handle_status(status);}


	/*
        Initialize the slave signal on the second device with 

        struct bladerf* second --> the second device
        bladerf_channel channel_rx_0 --> The RX0 port on the second device
        bladerf_trigger_signal trigger_signal --> The J51-1 signal, which is connected to both devices
        struct bladerf_trigger *trig_second_rx_0 --> The trigger for the first rx port on the second device
    */
	status = bladerf_trigger_init(second, channel_rx_0, trigger_signal, &trig_second_rx_0);
	
    //If a zero status code, then we set the "role" of the RX0, first device trigger to be BLADERF_TRIGGER_ROLE_SLAVE
	if(!status)
    {
        trig_second_rx_0.role = BLADERF_TRIGGER_ROLE_SLAVE;
    }
    else{handle_status(status);}



	//arm the triggering functionality on the first device, TX0, Master signal
    status = bladerf_trigger_arm(first, trig_master, true, 0, 0);
	handle_status(status);
		
	//arm the triggering on the frist device, RX0, Slave Signal
	status = bladerf_trigger_arm(first, &trig_first_rx_0, true, 0, 0);
	handle_status(status);

	//arm triggering on the second device, RX0, Slave Signal
	status = bladerf_trigger_arm(second, &trig_second_rx_0, true, 0, 0);
	handle_status(status);

}

void openDevices()
{

    int status = -1;

    //We hardcode the device serial numbers for ourselves to make it easy in the python code
    const char *devstr  = "*:serial=cbd";
    const char *devstr2  = "*:serial=35d";

    //This opens the devices for us
    dev1 = example_init(devstr);
    dev2 = example_init(devstr2);

    
    if(dev1)
    {
        //set the master to output it's clock
        status = bladerf_set_smb_mode(dev1, BLADERF_SMB_MODE_OUTPUT);
        if(!status) handle_status(status);
    }
    
    if(dev2)
    {
        //set the slave to input it's clock
        status = bladerf_set_smb_mode(dev2, BLADERF_SMB_MODE_INPUT);
        if(!status) handle_status(status);
    }
    //Now both devices should be open with their clock's synced together
}

void setupRX()
{
    openDevices();
    // malloc our arrays now, since they're global and we always 
    // know we receive "samples_len" samples, we dont have to re-malloc each time
    dev1_samples = malloc(per_device_array_len * sizeof(int16_t));
    dev2_samples = malloc(per_device_array_len * sizeof(int16_t));
    all_samples = malloc(2 * per_device_array_len * sizeof(int16_t));


    // malloc space for our arguments structs we pass to the threads
    dev1_args=(args_struct *)malloc(sizeof(args_struct));
    dev2_args=(args_struct *)malloc(sizeof(args_struct));

    // Get the correct data in our arg structs
    dev1_args->device = dev1;
    dev2_args->device = dev2;

    dev1_args->isDevice1 = true;
    dev2_args->isDevice1 = false;

    // for the last part of the setup, we enable the triggers
    // This gives us the master slave mode we need to receive from both devices at the same time
    EnableTriggers(&trig_master, dev1, dev2);

}

void cleanupDevices()
{
    bladerf_close(dev1);

    bladerf_close(dev2);
}


void * sync_rx_example(void *arguments)
{

    int status, ret;
    bool done         = false;

    args_struct *args = (args_struct*)arguments;

    int16_t *rx_samples = NULL;

    const unsigned int timeout_ms = 30000;

    int16_t j = 0;

    if(args->isDevice1)
    {
        rx_samples = dev1_samples;
    }
    else
    {
        rx_samples = dev2_samples;
    }

    // rx_samples = (int16_t *)malloc(per_device_array_len * sizeof(int16_t));

    if (rx_samples == NULL)
    {
        printf("Error mallocing\n");
        return NULL;
    }

    //set all bytes of the sample array to 0 before receiving
    memset(rx_samples, 1, per_device_array_len * sizeof(int16_t));

    /* Initialize synch interface on RX and TX */
    status = init_sync(args->device, timeout_ms);
    if (status != 0) {
        printf("Failed init sync\n");
        goto out;
    }

    /** [enable_modules] */

    status = bladerf_enable_module(args->device, BLADERF_RX, true);
    if (status != 0) {
        fprintf(stderr, "Failed to enable RX: %s\n", bladerf_strerror(status));
        goto out;
    }



    status = bladerf_sync_rx(args->device, rx_samples, samples_len*2, NULL, timeout_ms);
    if (status != 0) {
        fprintf(stderr, "Failed to RX samples: %s\n", bladerf_strerror(status));
        goto out;
    }

out:
    ret = status;

    /** [disable_modules] */

    /* Disable RX, shutting down our underlying RX stream */
    status = bladerf_enable_module(args->device, BLADERF_RX, false);
    if (status != 0) {
        fprintf(stderr, "Failed to disable RX: %s\n", bladerf_strerror(status));
    }

    bladerf_deinterleave_stream_buffer(BLADERF_RX_X2, BLADERF_FORMAT_SC16_Q11, samples_len, rx_samples);

    return NULL;
}


int16_t * receive_rx()
{

    pthread_create(&dev1_thread, NULL, &sync_rx_example, dev1_args);

    pthread_create(&dev2_thread, NULL, &sync_rx_example, dev2_args);

    bladerf_trigger_fire(dev1, &trig_master);

    pthread_join(dev1_thread, NULL);

    pthread_join(dev2_thread, NULL);

    // int i;

    // for(i = 0; i < samples_len*2; i++)
    // {
    //     all_samples[i] = dev1_samples[i];
    //     printf("%d ", all_samples[i]);
    // }
    // while(i < samples_len * 4)
    // {
    //     all_samples[i] = dev2_samples[i];
    //     printf("%d ", all_samples[i]);
    //     i++;
    // }
    // printf("\n");

    memcpy(all_samples, dev1_samples, per_device_array_len * 2);

    memcpy(&all_samples[per_device_array_len], dev2_samples, per_device_array_len * 2);

    // sc16q11_sample_fixup(all_samples, samples_len*4);

    return all_samples;

}


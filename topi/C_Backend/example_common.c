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

#include <libbladeRF.h>
#include <stdio.h>
#include <stdlib.h>

#include "example_common.h"

// unsigned long freq = 2280000000;

// bladerf_frequency freq = 2280000000;

struct bladerf *example_init(const char *devstr)
{
    int status;
    struct bladerf *dev;

    printf("Opening and initializing device...\n\n");

    status = bladerf_open(&dev, devstr);
    if (status != 0) {
        fprintf(stderr, "Failed to open device: %s\n",
                bladerf_strerror(status));
        goto out;
    }

    status = bladerf_set_frequency(dev, BLADERF_CHANNEL_RX(0), EXAMPLE_RX_FREQ);
    if (status != 0) {
        fprintf(stderr, "Failed to set RX frequency: %s\n",
                bladerf_strerror(status));
        goto out;
    }
        else{
        printf("Set Frequency on RX0 To %llu\n", EXAMPLE_RX_FREQ);
    }
    status = bladerf_set_frequency(dev, BLADERF_CHANNEL_RX(1), EXAMPLE_RX_FREQ);
    if (status != 0) {
        fprintf(stderr, "Failed to set RX frequency: %s\n",
                bladerf_strerror(status));
        goto out;
    }
    else{
        printf("Set Frequency on RX1 To %llu\n", EXAMPLE_RX_FREQ);
    }

    status = bladerf_set_sample_rate(dev, BLADERF_CHANNEL_RX(0),
                                     EXAMPLE_SAMPLERATE, NULL);
    if (status != 0) {
        fprintf(stderr, "Failed to set RX sample rate: %s\n",
                bladerf_strerror(status));
        goto out;
    }
        else{
        printf("Set Samplerate on RX0 To %d\n", EXAMPLE_SAMPLERATE);
    }
    status = bladerf_set_sample_rate(dev, BLADERF_CHANNEL_RX(1),
                                     EXAMPLE_SAMPLERATE, NULL);
    if (status != 0) {
        fprintf(stderr, "Failed to set RX sample rate: %s\n",
                bladerf_strerror(status));
        goto out;
    }
    else{
        printf("Set Samplerate on RX1 To %d\n", EXAMPLE_SAMPLERATE);
    }

    status = bladerf_set_bandwidth(dev, BLADERF_CHANNEL_RX(0),
                                   EXAMPLE_BANDWIDTH, NULL);
    if (status != 0) {
        fprintf(stderr, "Failed to set RX bandwidth: %s\n",
                bladerf_strerror(status));
        goto out;
    }
    else{
        printf("Set Bandwidth on RX0 To %d\n", EXAMPLE_BANDWIDTH);
    }
    status = bladerf_set_bandwidth(dev, BLADERF_CHANNEL_RX(1),
                                   EXAMPLE_BANDWIDTH, NULL);
    if (status != 0) {
        fprintf(stderr, "Failed to set RX bandwidth: %s\n",
                bladerf_strerror(status));
        goto out;
    }
    else{
        printf("Set Bandwidth on RX1 To %d\n", EXAMPLE_BANDWIDTH);
    }

    status = bladerf_set_gain(dev, BLADERF_CHANNEL_RX(0), EXAMPLE_RX_GAIN);
    if (status != 0) {
        fprintf(stderr, "Failed to set RX gain: %s\n",
                bladerf_strerror(status));
        goto out;
    }
    else{
        printf("Set Gain on RX0 To %d\n", EXAMPLE_RX_GAIN);
    }
    status = bladerf_set_gain(dev, BLADERF_CHANNEL_RX(1), EXAMPLE_RX_GAIN);
    if (status != 0) {
        fprintf(stderr, "Failed to set RX gain: %s\n",
                bladerf_strerror(status));
        goto out;
    }
    else{
        printf("Set Gain on RX1 To %d\n", EXAMPLE_RX_GAIN);
    }

    status = bladerf_set_frequency(dev, BLADERF_CHANNEL_TX(0), EXAMPLE_TX_FREQ);
    if (status != 0) {
        fprintf(stderr, "Faield to set TX frequency: %s\n",
                bladerf_strerror(status));
        goto out;
    }

    status = bladerf_set_sample_rate(dev, BLADERF_CHANNEL_TX(0),
                                     EXAMPLE_SAMPLERATE, NULL);
    if (status != 0) {
        fprintf(stderr, "Failed to set TX sample rate: %s\n",
                bladerf_strerror(status));
        goto out;
    }

    status = bladerf_set_bandwidth(dev, BLADERF_CHANNEL_TX(0),
                                   EXAMPLE_BANDWIDTH, NULL);
    if (status != 0) {
        fprintf(stderr, "Failed to set TX bandwidth: %s\n",
                bladerf_strerror(status));
        goto out;
    }

    status = bladerf_set_gain(dev, BLADERF_CHANNEL_TX(0), EXAMPLE_TX_GAIN);
    if (status != 0) {
        fprintf(stderr, "Failed to set TX gain: %s\n",
                bladerf_strerror(status));
        goto out;
    }

out:
    if (status != 0) {
        bladerf_close(dev);
        return NULL;
    } else {
        return dev;
    }
}

#!/bin/sh
# Kept for the habit; the Makefile is the pipeline.
exec make -C "$(dirname "$0")" "$@"

#!/usr/bin/env bash

# On every start-up get data
python get_raw_data.py

# Run API service
python financial/main.py
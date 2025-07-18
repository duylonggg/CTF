#!/bin/bash
for i in {0..9}; do
  pin="${i}0000000"
  echo $pin
  time ./pin_checker <<< "$pin"
done
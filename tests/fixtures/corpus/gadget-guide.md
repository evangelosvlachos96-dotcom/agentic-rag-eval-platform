# Gadget Assembly Guide

This guide explains how to assemble a gadget from a kit. It complements the
Widget Transfer Protocol specification, which describes how finished gadgets
exchange widget records.

## Parts list

A kit contains a frame, two hinges, a controller board and a bag of screws.
Count the screws before starting; kits shipped before 2024 contain twelve,
later kits contain sixteen.

## Assembly

### Mounting the hinges

Attach each hinge to the frame with two screws. Do not tighten fully until
both hinges are in place, otherwise the frame will twist.

### Fitting the controller

The controller board slides into the rails behind the hinges. It only fits
one way round; if it resists, flip it.

## Rationale

Length-prefixed framing was chosen over delimiter based framing because
payloads may legitimately contain any byte, and scanning for delimiters
costs more than reading a fixed header. A fixed header also makes the parser
trivial to fuzz and to test.

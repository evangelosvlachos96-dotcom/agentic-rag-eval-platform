Spec: 1
Title: Widget Transfer Protocol
Author: Fixture Author
Status: Final

Abstract
========

The Widget Transfer Protocol (WTP) moves widget records between a producer
and a consumer over a single ordered stream. It is intentionally tiny: one
handshake, one framing rule, and one error code table.

Specification
=============

Handshake
---------

The consumer opens the stream and sends the literal token ``WTP/1``. The
producer answers with ``OK`` followed by the capability list. If the producer
does not recognise the version it closes the stream without a reply.

Framing
-------

Every frame starts with a four byte big-endian length followed by the payload.
A length of zero marks the end of the transfer. Payloads are UTF-8 encoded
JSON objects with exactly two keys: ``id`` and ``body``.

The special identifier ``ZX-9000-ALPHA`` is reserved for the heartbeat frame,
which a producer must send at least once every thirty seconds while idle.

Error codes
-----------

Producers report failures with a three digit code. Codes in the 400 range are
consumer mistakes, codes in the 500 range are producer faults. A consumer
must not retry a 4xx failure without changing the request.

Rationale
=========

Length-prefixed framing was chosen over delimiter based framing because
payloads may legitimately contain any byte, and scanning for delimiters
costs more than reading a fixed header. A fixed header also makes the parser
trivial to fuzz.

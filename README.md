# Talkushka transcribing service

Part of the "Talkushka" ecosystem


**Table of content:**

- [Project description](#description)
- [Specifications](#specifications)
- [Build](#build)

### Description

The service only purpose is to transcribe an audio file and return a text.  
Service acts as a gRPC Server and listens for appropriate requests.  
Once the server gets a request - it starts transcribing using Whisper models locally on
machine where this server is running.


### Specifications

- Service is develop using Python 3.12.
- Transcriber cls, models, q_size are defined in configuration file.
- gRPC communication model is using mTLS (mutual TLS) meaning the need of properly configured certificates

### Build

- Install the package by `make install` (please note, that once the transcriber launched with specified model for the first time - it is going to load the model)
- Make sure that you have configured certificates correctly [see below](#certificates)
- Run a service by `make` or `run_server` 

### Certificates

To make the services connect to each other using mTLS you need to do the following:
- in case you have `ca.crt` and `server` + `client` certificates - place `ca.crt`, `server.crt` and `server.key` to `cert/`
- otherwise you can generate certificates using make, look for gen_cert commands, then place to `cert/` corresponding `ca.crt`, `server.key`, `server.crt`
- place the same `ca.crt`, `client.crt` and `client.key` to client side
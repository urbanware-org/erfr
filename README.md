# *Erfr* <img src="erfr.png" alt="Erfr logo" height="48px" width="48px" align="right"/>

**Table of contents**
*   [Definition](#definition)
*   [Details](#details)
*   [Requirements](#requirements)
*   [Documentation](#documentation)
*   [Contact](#contact)
*   [Useless facts](#useless-facts)

----

## Definition

The *Erfr* project is an encryption tool based on the one-time pad encryption technique, built to encrypt files in a secure way.

[Top](#erfr-)

## Details

The main features of *Erfr* are the following:

*   Secure encryption of files (as well as the decryption of encrypted data).
*   Optional obfuscation of the encrypted and the key files.
*   Enhanced options to complicate cracking the encrypted data (e. g. in case an unauthorized person has gained access to the encrypted and the key file).

Detailed information about the [encryption engine](../../wiki#encryption-engine) and [key generation](../../wiki#key-generation) can be found inside the [wiki](../../wiki).

The project also consists of [multiple components](../../wiki#components).

On March 2018 the project has officially been discontinued. Details can be found [here](../../wiki#end-of-life).

[Top](#erfr-)

## Requirements

### General

In order to use *Erfr*, the *Python* framework must be installed on the system.

Depending on which version of the framework you are using:

*   *Python* 2.x (version 2.7 or higher is recommended, may also work with earlier versions)
*   *Python* 3.x (version 3.2 or higher is recommended, may also work with earlier versions)

### Key generation

In order to use the optional *[Fortuna](https://en.wikipedia.org/wiki/Fortuna_(PRNG))* pseudo-random number generator to generate keys, a corresponding *Python* module is required. Details can be found [here](https://github.com/urbanware-org/erfr/wiki#fortuna-prng).

[Top](#erfr-)

## Documentation

In the corresponding `docs` sub-directories, there are plain text files containing a detailed documentation for each component with further information and usage examples.

[Top](#erfr-)

## Contact

As mentioned above, this project has been discontinued. For this reason, no new features will be implemented, existing features will not be enhanced and remaining bugs will not be fixed either.

However, if you have questions about it, you can contact me by sending an email to <dev@urbanware.org>.

[Top](#erfr-)

## Useless facts

Whoever cares can find them [here](../../wiki#useless-facts).

[Top](#erfr-)

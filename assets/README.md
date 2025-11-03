# Assets Directory

This directory contains all the media assets for the Lunar Lander game.

## Current Assets

- `background.mp3` - Background music (Jazz 1 by Francisco Alvear)
- `crash.wav` - Crash sound effect (placeholder - needs actual audio)
- `thrust.wav` - Engine thrust sound effect (placeholder - needs actual audio)  
- `landing.wav` - Successful landing sound effect (placeholder - needs actual audio)
- `lander.png` - Lander sprite image
- `icon.ico` - Application icon

# Background Music

To add background music to the Lunar Lander game:

1. Create an audio file (OGG or MP3 format recommended)
2. Name it `background.ogg` or `background.mp3`
3. Place it in the `assets/` directory
4. The game will automatically load and play it when started

## Music Requirements

- Format: OGG (preferred) or MP3
- The music will loop continuously
- Volume is set to 30% by default
- If no music file is found, the game runs normally without audio

## Creating Music

You can create music using:
- Free tools like LMMS, Audacity, or GarageBand
- Online music generators
- Royalty-free music libraries

The music should be ambient/space-themed to fit the lunar landing theme.

# Sound Effects

## Crash Sound

To add a crash sound effect when the lander crashes:

1. Create a short audio file (WAV, OGG, or MP3 format)
2. Name it `crash.wav`, `crash.ogg`, or `crash.mp3`
3. Place it in the `assets/` directory
4. The game will automatically load and play it when a crash occurs

## Sound Effect Requirements

- Format: WAV (preferred for sound effects), OGG, or MP3
- Duration: Short (1-3 seconds recommended)
- Volume: Will be played at 70% volume
- If no crash sound file is found, crashes are silent

## Creating Sound Effects

You can create sound effects using:
- Free tools like Audacity, LMMS, or BFXR
- Online sound effect generators
- Royalty-free sound libraries

The crash sound should be impactful but not too loud or startling.

## Thrust Sound

To add a thrust sound effect when the main engines fire:

1. Create a looping audio file (WAV, OGG, or MP3 format)
2. Name it `thrust.wav`, `thrust.ogg`, or `thrust.mp3`
3. Place it in the `assets/` directory
4. The game will automatically load and play it when thrusting

## Thrust Sound Requirements

- Format: WAV (preferred for sound effects), OGG, or MP3
- Duration: Short loop (2-5 seconds recommended, will loop)
- Volume: Will be played at 60% volume
- If no thrust sound file is found, thrusting is silent

## Landing Success Sound

To add a success sound effect for successful landings:

1. Create a short audio file (WAV, OGG, or MP3 format)
2. Name it `landing.wav`, `landing.ogg`, or `landing.mp3`
3. Place it in the `assets/` directory
4. The game will automatically load and play it on successful landings

## Landing Sound Requirements

- Format: WAV (preferred for sound effects), OGG, or MP3
- Duration: Short (1-3 seconds recommended)
- Volume: Will be played at 80% volume
- If no landing sound file is found, landings are silent
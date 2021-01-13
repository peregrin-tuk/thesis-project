const sequence = SOPHISTICATED_LADY
const length = 16
const temperature = 1.1

const quantizedSequence = mm.sequences.quantizeNoteSequence(sequence, 1)
const player = new mm.SoundFontPlayer('https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus')
let viz = new mm.PianoRollCanvasVisualizer(quantizedSequence, document.getElementById('input'))

const generate = async (checkpoint, chords) => {
    try {
        let model, result, start, end

        switch (checkpoint) {
            case 'improv':
                const improvCheckpoint = 'https://storage.googleapis.com/magentadata/js/checkpoints/music_rnn/chord_pitches_improv'
                model = new mm.MusicRNN(improvCheckpoint)
                await model.initialize()
                start = window.performance.now();
                if (chords) {
                    result = await model.continueSequence(quantizedSequence, length, temperature, ['C', 'C', 'F', 'C', 'F', 'C', 'G7', 'C'])
                } else {
                    result = await model.continueSequence(quantizedSequence, length, temperature)
                }
                end = window.performance.now();
                break;
            case 'melody':
                const melodyCheckpoint = 'https://storage.googleapis.com/magentadata/js/checkpoints/music_rnn/melody_rnn'
                model = new mm.MusicRNN(melodyCheckpoint)
                await model.initialize()
                start = window.performance.now();
                if (chords) {
                    result = await model.continueSequence(quantizedSequence, length, temperature, ['C', 'C', 'F', 'C', 'F', 'C', 'G7', 'C'])
                } else {
                    result = await model.continueSequence(quantizedSequence, length, temperature)
                }
                end = window.performance.now();
                break;
            case 'basic':
                const basicCheckpoint = 'https://storage.googleapis.com/magentadata/js/checkpoints/music_rnn/basic_rnn'
                model = new mm.MusicRNN(basicCheckpoint)
                await model.initialize()
                start = window.performance.now();
                if (chords) {
                    result = await model.continueSequence(quantizedSequence, length, temperature, ['C', 'C', 'F', 'C', 'F', 'C', 'G7', 'C'])
                } else {
                    result = await model.continueSequence(quantizedSequence, length, temperature)
                }
                end = window.performance.now();
                break;
            case 'mel_4b':
                const mel_4barCheckpoint = 'https://storage.googleapis.com/magentadata/js/checkpoints/music_vae/mel_4bar_small_q2'
                model = new mm.MusicVAE(mel_4barCheckpoint)
                await model.initialize()
                start = window.performance.now()
                result = await model.sample(1)
                end = window.performance.now()
                break;
        }

        document.getElementById('done').innerHTML = `<p>Generated in ${end - start} ms using <i>${checkpoint}</i> model. <button id="midi_result" class="button-sm">DOWNLOAD</button><p>`
        let viz = new mm.PianoRollCanvasVisualizer(result, document.getElementById('output'))

        const playOriginalMelody = () => {
            player.stop()
            player.start(sequence)
        }
        const playGeneratedMelody = () => {
            player.stop()
            player.start(result)
        }

        const downloadGeneratedMidi = () => {
            result.notes.forEach(n => n.velocity = 100)
            downloadBlob(new Blob([mm.sequenceProtoToMidi(result)], { type: 'audio/midi' }), `js-${checkpoint}-result.mid`)
        }
        const downloadSourceMidi = () => {
            downloadBlob(new Blob([mm.sequenceProtoToMidi(sequence)], { type: 'audio/midi' }), `js-${checkpoint}-source.mid`)
        }


        document.getElementById('original').onclick = () => {
            playOriginalMelody()
        }
        document.getElementById('generated').onclick = () => {
            playGeneratedMelody()
        }
        document.getElementById('midi_result').onclick = () => {
            downloadGeneratedMidi()
        }
        document.getElementById('midi_source').onclick = () => {
            downloadSourceMidi()
        }


    } catch (error) {
        document.getElementById('done').innerHTML = `<p>ERROR occured: ${error}<p>`
        console.error(error)
    }
}

generate('melody', false)




// Utilities

function downloadBlob(blob, name = 'file.txt') {
    // Convert your blob into a Blob URL (a special url that points to an object in the browser's memory)
    const blobUrl = URL.createObjectURL(blob);

    // Create a link element
    const link = document.createElement("a");

    // Set link's href to point to the Blob URL
    link.href = blobUrl;
    link.download = name;

    // Append link to the body
    document.body.appendChild(link);

    // Dispatch click event on the link
    // This is necessary as link.click() does not work on the latest firefox
    link.dispatchEvent(
        new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        })
    );

    // Remove link from body
    document.body.removeChild(link);
}
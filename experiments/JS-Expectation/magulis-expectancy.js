stability = [6, 2, 4, 2, 5, 4, 2, 5, 2, 4, 2, 4, 6] // index = pitch relative to root note
proximity = [24, 36, 32, 25, 20, 16, 12, 9, 6, 4, 2, 1, 0.25] // index = interval in semitones; mobility factor [* 2/3 for repetition] is already included at index 0
direction_continuation = [6, 20, 12, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0] // index = previous interval in semitones
direction_reversal = [0, 0, 0, 0, 0, 6, 12, 25, 36, 52, 75, 75, 75] // index = previous interval in semitones


function calc_expectancy_rating_for_pitch(candidate, prev, prevprev, single_ratings = false) {
    
    let prev_interval = Math.abs(prev-prevprev)
    let current_interval = Math.abs(candidate-prev)
    let prev_direction = Math.sign(prev-prevprev)
    let current_direction = Math.sign(candidate-prev)
    let continuation = current_direction != 0 && current_direction == prev_direction

    let s = stability[candidate]
    let p = proximity[current_interval]
    let d = continuation ? direction_continuation[prev_interval] : direction_reversal[prev_interval]

    if (current_direction == 0) d /= 3
    if (prev == 11 && candidate == 9) s = 6
    if (single_ratings) return s, p, d
    else return (s * p) + d
}

notes = [
    { pitch: 5},
    { pitch: 7}
]
expectancy_ratings = []
predictions = []
number_of_generated_notes = 8;


let start = performance.now()

for (note = 2; note < number_of_generated_notes; note++) {
    prev_pitch = notes[note-1].pitch
    prevprev_pitch = notes[note-2].pitch
    ratings_for_note = []

    // calculate ratings for all 12 possible pitches
    for (pitch = 0; pitch < 13; pitch++) {
        e = calc_expectancy_rating_for_pitch(pitch, prev_pitch, prevprev_pitch)
        ratings_for_note.push(e)
    }

    // append expectancy ratings to list
    expectancy_ratings.push(ratings_for_note)

    // select pitch with highest rating
    prediction = ratings_for_note.indexOf(Math.max(...ratings_for_note))

    predictions.push(prediction)
    //console.log('prediction ' + note + ': ' + prediction)

    // create and append predicted note to midi
    predicted_note = { velocity: 100, pitch: prediction, start: note/2+1, end: note/2+1.5 }
    notes.push(predicted_note)
}

let end = performance.now()
console.log(`Exe time: ${end - start} ms`)


console.log(predictions)
console.log(expectancy_ratings)
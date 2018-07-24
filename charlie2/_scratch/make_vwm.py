from charlie2.tools.recipes import get_vwm_stimuli
import wave
from tqdm import tqdm

if __name__ == '__main__':
    sequences = [item for sublist in get_vwm_stimuli("en") for item in sublist]
    s = "/Users/smathias/Documents/Charlie2/charlie2/stimuli/audio/verbalworkingmemory"
    for sequence in sequences:
        data = []
        for g in str(sequence):
            p = ["L", "D"][g in "123456789"]
            f = f"{s}/SPAN-{p}{g}-V1.wav"
            w = wave.open(f, 'rb')
            data.append([w.getparams(), w.readframes(w.getnframes())])
            w = wave.open('silence.wav', 'rb')
            data.append([w.getparams(), w.readframes(w.getnframes())])
            w.close()
        output = wave.open(f"{sequence}.wav", 'wb')
        output.setparams(data[0][0])
        for i in range(len(str(sequence))*2):
            output.writeframes(data[i][1])
        output.close()

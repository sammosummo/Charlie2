from charlie2.tools.recipes import get_vwm_stimuli
import wave
from tqdm import tqdm
from os import listdir

if __name__ == '__main__':
    # sequences = [item for sublist in get_vwm_stimuli("en") for item in sublist]
    # s = "/Users/smathias/Documents/Charlie2/charlie2/stimuli/audio/verbalworkingmemory"
    # for sequence in sequences:
    #     data = []
    #     for g in str(sequence):
    #         p = ["L", "D"][g in "123456789"]
    #         f = f"{s}/SPAN-{p}{g}-V1.wav"
    #         w = wave.open(f, 'rb')
    #         data.append([w.getparams(), w.readframes(w.getnframes())])
    #         w = wave.open('silence.wav', 'rb')
    #         data.append([w.getparams(), w.readframes(w.getnframes())])
    #         w.close()
    #     output = wave.open(f"{sequence}.wav", 'wb')
    #     output.setparams(data[0][0])
    #     for i in range(len(str(sequence))*2):
    #         output.writeframes(data[i][1])
    #     output.close()
    p = "/Users/smathias/Documents/Charlie2/charlie2/stimuli/audio/verbalworkingmemory/"
    s = "/Users/smathias/Documents/Charlie2/charlie2/stimuli/audio/common/silence.wav"
    s = wave.open(s, 'rb')
    for f in [f for f in listdir(p) if '.wav' in f]:
        w = wave.open(p + f, 'rb')
        data = []
        data.append([s.getparams(), s.readframes(s.getnframes())])
        data.append([w.getparams(), w.readframes(w.getnframes())])
        w.close()
        output = wave.open('tmp.wav', 'wb')
        output.setparams(data[0][0])
        for i in range(2):
            output.writeframes(data[i][1])
        output.close()






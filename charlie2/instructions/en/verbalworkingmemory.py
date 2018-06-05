instr = [
    """Test of verbal working memory

This test requires that the experimenter
operates the computer. Please allow them to
take over now.""",
    """Say this:

"I am going to say some numbers.  Listen carefully,
and when I am through, I want you to say them right
after me.  Just say what I say."

Give the subject up to two examples until they make
a correct response:

2-4-3
8-9-5""",
    """Say this:

"Now I am going to say some more numbers.  But this
time when I stop, I want you to say them backwards.
For example, if I say 7-1-9, what would you say?"

Give the subject up to two more examples:

1-9
3-4""",
    """Say this:

"I am going to say a group of numbers and letters.
After I say them, I want you to tell me the numbers
fist, in order, starting with the lowest number.
Then tell me the letters in alphabetical order. For
example, if I say B-7, your answer should be 7-B.
The number goes first, then the letter. If I say
9-C-3, then your answer should be 3-9-C, the numbers
in order first, then the letters in alphabetical
order. Let's practice."
""",
    """Say this:

"Ok, let's begin the real test."
""",
    f"""Read this sequence out loud:

{sequence}""",
    f'Responded this: {response}',
    f'Responded anything else',
]
vwm_sequences = [
    [
        629,
        375,
        5417,
        8396,
        36925,
        69471,
        918427,
        635482,
        1285346,
        2814975,
        38295174,
        59182647,
    ],
    [
        51,
        38,
        493,
        526,
        3814,
        1795,
        62972,
        48527,
        715286,
        831964,
        4739128,
        8129365,
    ],
    [
        '6F',
        'G4',
        '3W5',
        'T7L',
        '6GA2',
        '9PF4',
    ],
    [
        'L2,'
        '6P',
        'B5',
        'F7L',
        'R4D',
        'H18',
        'T9A3',
        'V1J5',
        '7N4L',
        '8D6G1',
        'K2C7S',
        '5P3Y9',
        'M4E7Q2',
        'W8H5F3',
        '6G9A2S',
        'R3B4Z1C',
        '5T9J2X7',
        'E1H8R4D',
        '5H9S2N6A',
        'D1R9B4K3',
        '7M2T6F1Z',
    ],
]

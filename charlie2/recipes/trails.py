def make_trail_trials():
    """Details of the trials from charlie v2 trail-making test (shorter).

    """
    blocks = ([0] * 5) + ([1] * 20) + ([2] * 5) + ([3] * 20) + ([4] * 5) + ([5] * 20)
    practices = (
        ([True] * 5)
        + ([False] * 20)
        + ([True] * 5)
        + ([False] * 20)
        + ([True] * 5)
        + ([False] * 20)
    )
    block_types = (
            (["number"] * 5)
            + (["number"] * 20)
            + (["letter"] * 5)
            + (["letter"] * 20)
            + (["sequence"] * 5)
            + (["sequence"] * 20)
    )
    trials = (list(range(5)) + list(range(20))) * 3
    blaze_positions = [
        (-219, -85),
        (357, 276),
        (350, -237),
        (124, -121),
        (31, -267),
        (-243, -45),
        (237, 158),
        (-344, 333),  # move this
        (82, -111),
        (342, -112),
        (189, -308),  # move this
        (-193, -195),
        (-330, -162),
        (-39, -28),
        (112, -273),  # move this
        (-162, -276),
        (-128, -142),
        (207, 79),  # move this
        (369, 0),
        (366, 168),  # move this
        (320, 243),  # move this
        (-4, 132),
        (127, -22),  # move this
        (-9, -127), # move this
        (194, -166),
        (-262, -17),
        (-40, 101),
        (-268, 106),
        (24, -168),
        (241, 32),
        (318, 209),
        (-54, 195),
        (-326, -253),
        (224, -132),
        (138, -308),
        (277, -238),
        (350, -14),
        (-357, -36),
        (-171, -296),
        (-174, -118),
        (333, 96),
        (-286, 80),
        (-213, 190),
        (-66, -148),
        (85, -238),
        (274, -68),
        (-70, 28),
        (90, 56),
        (225, 144),
        (30, 130),
        (310, 10),
        (-318, -2),
        (366, 215),
        (-337, 91),
        (79, -178),
        (-291, -108),
        (-385, 5),
        (-357, -266),
        (273, -252),
        (279, -44),
        (284, 294),
        (333, 18),
        (117, 23),
        (-246, -49),
        (3, -49),
        (177, -167),
        (-81, 95),
        (164, 164),
        (326, -185),
        (-25, -307),
        (-60, -175),
        (-229, 45),
        (-30, 208),
        (-342, 138),
        (-189, -211),
    ]
    glyphs = (
        list(range(1, 6))
        + list(range(1, 21))
        + list("abcde")
        + list("abcdefghijklmnopqrst")
        + list("1a2b3")
        + [
            1,
            "a",
            2,
            "b",
            3,
            "c",
            4,
            "d",
            5,
            "e",
            6,
            "f",
            7,
            "g",
            8,
            "h",
            9,
            "i",
            10,
            "j",
        ]
    )
    glyphs = [str(g) for g in glyphs]
    details = list(zip(blocks, practices, block_types, trials, blaze_positions, glyphs))
    names = [
        "block_number", "practice", "block_type", "trial_number", "blaze_position", "glyph"
    ]
    control = [dict(zip(names, d)) for d in details]
    return control

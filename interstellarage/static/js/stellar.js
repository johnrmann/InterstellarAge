function spectralClassColor (spectralClass) {
    if (spectralClass === "O") {
        return 0x9bb0ff;
    }

    else if (spectralClass === "B") {
        return 0xaabfff;
    }

    else if (spectralClass === "A") {
        return 0xcad8ff;
    }

    else if (spectralClass === "F") {
        return 0xfbf8ff;
    }

    else if (spectralClass === "G") {
        return 0xfff4e8;
    }

    else if (spectralClass === "K") {
        return 0x44ddb4;
    }

    else if (spectralClass === "M") {
        return 0xffbd6f;
    }

    else if (spectralClass === "L") {
        return 0xf84235;
    }

    else if (spectralClass === "T") {
        return 0xba3059;
    }

    else if (spectralClass === "Y") {
        return 0x605170;
    }

    console.log("Unknown spectral class "+spectralClass);
    return 0xffffff;
}
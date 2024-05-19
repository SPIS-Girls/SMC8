inlets = 1;
outlets = 4;

var activeVoices = [false, false, false, false];

function msg_float(r) {
    if (r >= 0 && r < 4) {
        activeVoices[r] = false;
    }
}

function bang() {
    var freeVoice = -1;
    for (var i = 0; i < activeVoices.length; i++) {
        if (!activeVoices[i]) {
            freeVoice = i;
            break;
        }
    }
    if (freeVoice != -1) {
        outlet(freeVoice, "bang");
        activeVoices[freeVoice] = true;
    }
}